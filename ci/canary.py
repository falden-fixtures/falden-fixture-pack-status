#!/usr/bin/env python3
"""The monthly canary (REG-416; the root's call R3): what a release of the pack recorded, read again from outside it,
with anonymous reads only.

    ci/canary.py --out FILE [--github-output FILE]

BEFORE 1.0 there is nothing to check, and nothing is published: no tag of the pack repository names a release
v<major>.<minor>.<patch> with a major of 1 or more. The run says so, writes `publish=false`, and exits 0. The first
canary record is the first after 1.0.

FROM 1.0, on the newest release tag, every expected value is read from a clone of that tag, never typed here:
  the subject repositories   register/scope.json's repositories in scope, each by its id;
  their sealed heads         the branch heads the captures hold, read through the release's own capture reader
                             (data/bin/capture_reader.py): refs.txt for the fixture repository pack.json names, and
                             <name>-branches.json for each other one;
  their /activity            the count and the newest id of activity.json, or of <name>-activity.json;
  the principals             register/principals.json's `people` and `service_accounts` entries, each id with
                             its login;
  the keyed API version      the capture reader's KEYED_API_VERSION;
  the identifiers            the DOIs and Software Heritage identifiers README.md and CITATION.cff name, the two
                             landing files the release fills after it is sealed, and the Rekor log index of every
                             attested dispatch in data/witness/attest.json.
and checked, anonymously: each repository's branch heads (git ls-remote) against the sealed ones; that GitHub's
/repositories/<id> names it, with archived true, answered under the keyed version with no Deprecation or Sunset
header; its /activity count and newest id; that /user/<id> gives each principal its login; that each DOI resolves
at doi.org, each identifier at Software Heritage's resolver and each log index at Rekor; and the fixity of the three
public copies DoD 5 names, each with bagit 1.9.0 --validate and fixpack verify: the clone of the tag, the Zenodo
record's archive (found through the version DOI) and a Software Heritage vault tarball of the tag's directory. Each
archive copy is held to the clone too, not only to itself: its tagmanifest-sha256.txt, which names every tag file
and the payload manifest by digest, must be the clone's byte for byte, and a copy whose tag manifest differs fails,
naming both digests. Escrow fixity is not here: it is yearly and local (the pass-12 plan, 4.2).

THE READS are anonymous (ci/forge.py): a token in the environment stops the run, at most 60 requests go to GitHub's
API in an hour, and a reset GitHub names is waited out. A read that fails after its retries is infrastructure,
never a pass or a fail. The result, falden-status-canary/1, says which.

A RUN THAT STOPS on an exception is a result too (canary_result()): the checks made by then, and why it stopped, a
read that failed after its retries as infrastructure, and a release record it cannot read or an answer in a shape
this code does not read as a fail, named by its type. It is published when a release is known, from the pack
repository's refs or, when those could not be read, from this repository's own records (records/index.json). With
no release known nothing is published, so before 1.0 nothing ever is (R3).
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(os.path.dirname(HERE), "records", "index.json")
sys.path.insert(0, HERE)
import detect as D  # noqa: E402
import forge as F  # noqa: E402

PACK = D.PACK_REPOSITORY
CANARY_FORMAT = "falden-status-canary/1"
DOI = re.compile(r"\b10\.5281/zenodo\.(\d+)\b")
SWHID = re.compile(r"\bswh:1:(?:snp|rel|rev|dir|cnt):[0-9a-f]{40}\b")
RELEASE_TAG = re.compile(r"refs/tags/v(\d+)\.(\d+)\.(\d+)")
OFFLINE = os.environ.get("STATUS_OFFLINE") == "1"


def item(name, result, detail=""):
    return {"name": name, "result": result, "detail": str(detail).strip()[-1500:]}


def newest_release(refs):
    """(tag, commit) of the newest v<major>.<minor>.<patch> tag with a major of 1 or more, or None."""
    best = None
    for c, rs in D.commits_of(refs).items():
        for r in rs:
            m = RELEASE_TAG.fullmatch(r)
            if m and int(m.group(1)) >= 1:
                v = tuple(int(x) for x in m.groups())
                if best is None or v > best[0]:
                    best = (v, r[len("refs/tags/"):], c)
    return None if best is None else best[1:]


# ------------------------------------------------------------------ what the release recorded
def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def expectations(clone):
    """What the release clone records, read from it. ValueError naming what it cannot read."""
    data = os.path.join(clone, "data")
    try:
        scope = json.load(open(os.path.join(data, "register", "scope.json"), encoding="utf-8"))
        principals = json.load(open(os.path.join(data, "register", "principals.json"), encoding="utf-8"))
        pack = json.load(open(os.path.join(data, "pack.json"), encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as e:
        raise ValueError(f"the release's registers cannot be read: {e}") from e
    sys.path.insert(0, os.path.join(data, "bin"))
    try:
        cr = load_module(os.path.join(data, "bin", "capture_reader.py"), "release_capture_reader")
        cs = cr.open_set(os.path.join(data, "captures", "data"))
    except Exception as e:  # noqa: BLE001 - whatever the release's reader raises is named, not a traceback
        raise ValueError(f"the release's capture reader cannot open its captures: {type(e).__name__}: {e}") from e
    finally:
        sys.path.pop(0)
    fixture = pack.get("fixture_repo")
    repos = []
    for r in scope.get("repositories", []):
        if not r.get("in_scope"):
            continue
        name = r.get("repo_name_observed")
        short = name.split("/", 1)[1] if name and "/" in name else name
        heads, activity, why = None, None, []
        try:
            if name == fixture:
                heads = {ref: sha for sha, ref in (ln.split() for ln in cs.text("refs.txt").splitlines() if ln.strip())
                         if ref.startswith("refs/heads/")}
                rows = cs.load("activity.json")
            else:
                heads = {f"refs/heads/{b['name']}": b["commit"]["sha"] for b in cs.load(f"{short}-branches.json")}
                rows = cs.load(f"{short}-activity.json")
            activity = {"count": len(rows), "newest": max((x.get("id") for x in rows if isinstance(x.get("id"), int)),
                                                          default=None)}
        except Exception as e:  # noqa: BLE001
            why.append(f"{type(e).__name__}: {e}")
        repos.append({"id": int(r["repo_id"]), "name": name, "heads": heads, "activity": activity, "why": why})
    people = [(int(p["principal_id"]), p["login"]) for p in
              (principals.get("people") or []) + (principals.get("service_accounts") or [])
              if p.get("principal_id") is not None and p.get("login")]
    landing = ""
    for f in ("README.md", "CITATION.cff"):
        p = os.path.join(clone, f)
        if os.path.isfile(p):
            landing += open(p, encoding="utf-8").read() + "\n"
    rekor = []
    ap = os.path.join(data, "witness", "attest.json")
    if os.path.isfile(ap):
        try:
            for d in json.load(open(ap, encoding="utf-8")).get("dispatches") or []:
                a = d.get("attested") if isinstance(d, dict) else None
                if isinstance(a, dict) and isinstance(a.get("log_index"), int):
                    rekor.append(a["log_index"])
        except (OSError, ValueError) as e:
            raise ValueError(f"the release's attest record cannot be read: {e}") from e
    return {"repos": repos, "principals": people, "keyed": getattr(cr, "KEYED_API_VERSION", None),
            "dois": sorted(set(f"10.5281/zenodo.{m}" for m in DOI.findall(landing))),
            "swhids": sorted(set(SWHID.findall(landing))), "rekor": sorted(set(rekor)),
            "tagmanifest": tagmanifest_digest(clone)}


# ------------------------------------------------------------------ the copies' fixity
def bagit_cmd(tmp):
    if os.environ.get("BAGIT_CMD"):
        return shlex.split(os.environ["BAGIT_CMD"]), ""
    if OFFLINE:
        return None, "installing bagit 1.9.0 needs the network (STATUS_OFFLINE)"
    venv = os.path.join(tmp, "bagit-venv")
    if subprocess.run([sys.executable, "-m", "venv", venv], capture_output=True).returncode != 0:
        return None, "python -m venv failed"
    for attempt in range(3):
        r = subprocess.run([os.path.join(venv, "bin", "pip"), "install", "--disable-pip-version-check", "bagit==1.9.0"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if r.returncode == 0:
            return [os.path.join(venv, "bin", "python"), "-m", "bagit"], ""
        time.sleep(15 * (attempt + 1))
    return None, "pip install bagit==1.9.0 failed three times"


def bag_root(top):
    """The directory under `top` that holds bagit.txt, the bag's root, or None."""
    for d, _dirs, fs in os.walk(top):
        if "bagit.txt" in fs and os.path.isdir(os.path.join(d, "data")):
            return d
    return None


def fixity(name, root, bagit):
    """[items]: bagit --validate and fixpack verify on the bag at `root`."""
    if root is None:
        return [item(f"{name}: a BagIt bag", "fail", "no directory holding bagit.txt and data/")]
    out = []
    if bagit[0] is None:
        out.append(item(f"{name}: bagit 1.9.0 --validate", "infrastructure", bagit[1]))
    else:
        r = subprocess.run(bagit[0] + ["--validate", "."], cwd=root, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        said = r.stdout + r.stderr
        out.append(item(f"{name}: bagit 1.9.0 --validate", "pass" if r.returncode == 0 and "is valid" in said else "fail",
                        said[-600:]))
    r = subprocess.run([sys.executable, "-B", "data/bin/fixpack", "verify"], cwd=root, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    said = r.stdout + r.stderr
    out.append(item(f"{name}: fixpack verify", "pass" if r.returncode == 0 and "PACK VERIFIED" in said else "fail",
                    said[-600:]))
    return out


def tagmanifest_digest(root):
    """The sha256 of tagmanifest-sha256.txt at a bag's root, or None when the root holds none."""
    p = os.path.join(root, "tagmanifest-sha256.txt") if root else ""
    if not (p and os.path.isfile(p)):
        return None
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def same_tagmanifest(name, root, want):
    """An item: the archive copy at `root` holds the release clone's tagmanifest-sha256.txt, byte for byte (its
    sha256 `want`). A copy can be a valid bag of other bytes; the clone's tag manifest is what each copy is held to."""
    label = f"{name}: its tagmanifest-sha256.txt is the release clone's"
    if want is None:
        return item(label, "fail", "the clone of the release holds no tagmanifest-sha256.txt to hold the copy to")
    got = tagmanifest_digest(root)
    if got == want:
        return item(label, "pass", f"sha256 {got}, the clone's")
    return item(label, "fail", f"the copy's tagmanifest-sha256.txt is {'sha256 ' + got if got else 'absent'}, and the "
                               f"release clone's is sha256 {want}")


def safe_extract(archive_bytes, kind, dest):
    """Extract a zip or a gzipped tar into `dest`, refusing a member outside it or a link."""
    if kind == "zip":
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
            for n in z.namelist():
                if n.startswith("/") or ".." in n.split("/"):
                    raise ValueError(f"the archive holds {n!r}, outside its folder")
            z.extractall(dest)
        return
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:*") as t:
        for m in t.getmembers():
            if m.name.startswith("/") or ".." in m.name.split("/") or m.issym() or m.islnk():
                raise ValueError(f"the archive holds {m.name!r}, outside its folder or a link")
        if hasattr(tarfile, "data_filter"):  # Python 3.12 on, and the 3.9 security releases: the stricter filter too
            t.extractall(dest, filter="data")
        else:
            t.extractall(dest)


# ------------------------------------------------------------------ the canary
def run_canary(forge, ls, clone_from, tmp, say=print, state=None):
    """The canary's result: {"format", "publish", "release", "checks", "result", "time"}. `state`, when given, holds
    what a run that stops on an exception had found by then: the release, once found, and the checks made."""
    state = {} if state is None else state
    refs = ls(f"https://github.com/{PACK}")
    rel = newest_release(refs)
    if rel is None:
        say("  canary: the pack repository names no release from 1.0 on: nothing to check, and nothing is published")
        return {"format": CANARY_FORMAT, "publish": False, "release": None, "checks": [], "result": "none",
                "time": None}
    tag, commit = rel
    state["release"] = {"tag": tag, "commit": commit}
    clone = os.path.join(tmp, "release")
    r = subprocess.run(["git", "clone", "--quiet", "--branch", tag, clone_from, clone], capture_output=True, text=True,
                       env=F.git_env(), stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise F.Unreachable(f"git clone --branch {tag}: {(r.stderr or r.stdout).strip()[-300:]}")
    exp = expectations(clone)
    state["expected"] = True
    checks = state.setdefault("checks", [])
    api = "https://api.github.com"
    for repo in exp["repos"]:
        name = repo["name"]
        if repo["why"] or repo["heads"] is None:
            checks.append(item(f"{name}: the release's captures of it", "fail",
                               "; ".join(repo["why"]) or "no sealed heads"))
            continue
        live = {ref: sha for sha, ref in ls(f"https://github.com/{name}") if ref.startswith("refs/heads/")}
        moved = sorted(set(live.items()) ^ set(repo["heads"].items()))
        checks.append(item(f"{name}: its branch heads are the sealed ones", "fail" if moved else "pass",
                           f"{len(moved)} differ: {moved[:6]}" if moved else f"{len(live)} heads, as sealed"))
        a = forge.get(f"{api}/repositories/{repo['id']}", api_version=exp["keyed"])
        info = a.json() if a.status == 200 else {}
        checks.append(item(f"{name}: GitHub's /repositories/{repo['id']} names it, archived",
                           "pass" if info.get("full_name") == name and info.get("archived") is True else "fail",
                           f"status {a.status}, full_name {info.get('full_name')!r}, archived {info.get('archived')!r}"))
        marks = {k: a.headers.get(k) for k in ("deprecation", "sunset") if a.headers.get(k)}
        checks.append(item(f"{name}: no deprecation marked on the keyed API version {exp['keyed']}",
                           "fail" if marks else "pass", json.dumps(marks) if marks else "no Deprecation or Sunset header"))
        rows, url = [], f"{api}/repos/{name}/activity?per_page=100"
        while url:
            p = forge.get(url, api_version=exp["keyed"])
            if p.status != 200:
                rows = None
                break
            rows += p.json()
            m = re.search(r'<([^>]+)>;\s*rel="next"', p.headers.get("link", ""))
            url = m.group(1) if m else None
        if rows is None:
            checks.append(item(f"{name}: its /activity", "fail", f"status {p.status}"))
        else:
            got = {"count": len(rows), "newest": max((x.get("id") for x in rows if isinstance(x.get("id"), int)), default=None)}
            checks.append(item(f"{name}: its /activity count and newest id are the sealed ones",
                               "pass" if got == repo["activity"] else "fail", f"now {got}, sealed {repo['activity']}"))
    for pid, login in exp["principals"]:
        a = forge.get(f"{api}/user/{pid}")
        got = a.json().get("login") if a.status == 200 else None
        checks.append(item(f"principal {pid}: GitHub still names it {login}", "pass" if got == login else "fail",
                           f"status {a.status}, login {got!r}"))
    if not exp["dois"]:
        checks.append(item("the release's DOI", "fail", "README.md and CITATION.cff name no DOI"))
    for doi in exp["dois"]:
        a = forge.get(f"https://doi.org/{doi}", accept="*/*", method="HEAD", follow=False)
        checks.append(item(f"{doi} resolves", "pass" if a.status in (301, 302, 303, 307, 308) and a.headers.get("location")
                           else "fail", f"status {a.status}, location {a.headers.get('location')!r}"))
    if not exp["swhids"]:
        checks.append(item("the release's Software Heritage identifiers", "fail", "README.md and CITATION.cff name none"))
    for s in exp["swhids"]:
        a = forge.get(f"https://archive.softwareheritage.org/api/1/resolve/{s}/")
        checks.append(item(f"{s} resolves at Software Heritage", "pass" if a.status == 200 else "fail", f"status {a.status}"))
    for n in exp["rekor"]:
        a = forge.get(f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={n}")
        checks.append(item(f"Rekor log index {n} resolves", "pass" if a.status == 200 else "fail", f"status {a.status}"))
    # R3: the three public copies DoD 5 names.
    bagit = bagit_cmd(tmp)
    checks += fixity(f"the clone of {tag}", clone, bagit)
    checks += zenodo_copy(forge, exp, tmp, bagit)
    checks += swh_copy(forge, exp, tag, tmp, bagit)
    rs = {c["result"] for c in checks}
    result = "fail" if "fail" in rs else "infrastructure" if "infrastructure" in rs else "pass"
    return {"format": CANARY_FORMAT, "publish": True, "release": {"tag": tag, "commit": commit}, "checks": checks,
            "result": result, "time": forge.dates[-1] if forge.dates else None}


def zenodo_copy(forge, exp, tmp, bagit):
    """The Zenodo record's archive of the release, found through its version DOI, checked as a bag."""
    if not exp["dois"]:
        return [item("the Zenodo archive", "fail", "the release names no DOI to find it by")]
    rec = max(int(d.rsplit(".", 1)[1]) for d in exp["dois"])  # the version DOI is the newer record of the two
    a = forge.get(f"https://zenodo.org/api/records/{rec}", accept="application/json")
    if a.status != 200:
        return [item(f"the Zenodo record {rec}", "fail", f"status {a.status}")]
    files = [f for f in a.json().get("files", []) if str(f.get("key", "")).endswith(".zip")]
    if len(files) != 1:
        return [item(f"the Zenodo record {rec}'s archive", "fail", f"{len(files)} zip archives, not one")]
    z = forge.get(files[0]["links"]["self"], accept="*/*")
    if z.status != 200:
        return [item(f"the Zenodo record {rec}'s archive", "infrastructure" if z.status >= 500 else "fail",
                     f"status {z.status}")]
    dest = os.path.join(tmp, "zenodo")
    try:
        safe_extract(z.body, "zip", dest)
    except (ValueError, zipfile.BadZipFile) as e:
        return [item(f"the Zenodo record {rec}'s archive", "fail", str(e))]
    root = bag_root(dest)
    out = fixity(f"the Zenodo record {rec}'s archive", root, bagit)
    if root is not None:
        out.append(same_tagmanifest(f"the Zenodo record {rec}'s archive", root, exp.get("tagmanifest")))
    return out


def swh_copy(forge, exp, tag, tmp, bagit):
    """A Software Heritage vault tarball of the release tag's directory, cooked anonymously, checked as a bag."""
    snaps = [s for s in exp["swhids"] if s.startswith("swh:1:snp:")]
    if not snaps:
        return [item("the Software Heritage copy", "fail", "the release names no snapshot to find it in")]
    base = "https://archive.softwareheritage.org/api/1"
    sn = forge.get(f"{base}/snapshot/{snaps[0][len('swh:1:snp:'):]}/")
    br = (sn.json().get("branches") or {}).get(f"refs/tags/{tag}") if sn.status == 200 else None
    if not br:
        return [item("the Software Heritage copy", "fail", f"the snapshot holds no refs/tags/{tag} (status {sn.status})")]
    target, kind = br.get("target"), br.get("target_type")
    if kind == "release":
        r = forge.get(f"{base}/release/{target}/")
        target, kind = (r.json().get("target"), r.json().get("target_type")) if r.status == 200 else (None, None)
    if kind == "revision":
        r = forge.get(f"{base}/revision/{target}/")
        target = r.json().get("directory") if r.status == 200 else None
    if not target:
        return [item("the Software Heritage copy", "fail", f"refs/tags/{tag} leads to no directory")]
    url = f"{base}/vault/flat/swh:1:dir:{target}/"
    status = forge.get(url)
    if status.status == 404:
        status = forge.get(url, method="POST")  # an anonymous request to cook it: no credential, no write to the archive
    for _ in range(40):
        info = status.json() if status.status == 200 else {}
        if info.get("status") == "done":
            break
        if info.get("status") == "failed" or status.status not in (200, 404):
            return [item("the Software Heritage vault", "infrastructure", f"status {status.status}, {info.get('status')}")]
        forge.sleep(30)
        status = forge.get(url)
    else:
        return [item("the Software Heritage vault", "infrastructure", "the tarball was not ready in 20 minutes")]
    t = forge.get(info["fetch_url"], accept="*/*")
    if t.status != 200:
        return [item("the Software Heritage vault tarball", "infrastructure" if t.status >= 500 else "fail", f"status {t.status}")]
    dest = os.path.join(tmp, "swh")
    try:
        safe_extract(t.body, "tar", dest)
    except (ValueError, tarfile.TarError) as e:
        return [item("the Software Heritage vault tarball", "fail", str(e))]
    root = bag_root(dest)
    out = fixity("the Software Heritage vault tarball", root, bagit)
    if root is not None:
        out.append(same_tagmanifest("the Software Heritage vault tarball", root, exp.get("tagmanifest")))
    return out


def known_release(index_path=INDEX):
    """{"tag", "commit"} of the newest release this repository's records name, or None: a record of a commit that a
    tag v<major>.<minor>.<patch> with a major of 1 or more points at, which a canary record and the pack checks'
    record of a release both are."""
    try:
        with open(index_path, encoding="utf-8") as fh:
            index = json.load(fh)
    except (OSError, ValueError, RecursionError):
        return None
    best = None
    for r in (index.get("records") if isinstance(index, dict) else None) or []:
        if not (isinstance(r, dict) and isinstance(r.get("refs"), list) and re.fullmatch(r"[0-9a-f]{40}", str(r.get("commit")))):
            continue
        for ref in r["refs"]:
            m = RELEASE_TAG.fullmatch(str(ref))
            if m and int(m.group(1)) >= 1:
                v = tuple(int(x) for x in m.groups())
                if best is None or v > best[0]:
                    best = (v, {"tag": ref[len("refs/tags/"):], "commit": r["commit"]})
    return None if best is None else best[1]


def stopped(e, state, forge, index_path=INDEX):
    """The result of a run that stopped on `e`: the checks made by then and why it stopped, published when a release
    is known, from the pack repository's refs (state) or else from this repository's records."""
    if isinstance(e, F.Unreachable):
        why = item("the reads", "infrastructure", str(e))
    elif isinstance(e, ValueError) and not state.get("expected"):
        why = item("what the release recorded", "fail", str(e))
    else:
        why = item("the canary's run", "fail", f"it stopped on what it could not read: {type(e).__name__}: {e}")
    rel = state.get("release")
    if rel is None:
        rel = known_release(index_path)
        if rel is not None:
            why = item(why["name"], why["result"], f"{why['detail']} (the release named is the newest this "
                                                   f"repository's records hold: the pack repository's refs were not read)")
    checks = list(state.get("checks") or []) + [why]
    return {"format": CANARY_FORMAT, "publish": rel is not None, "release": rel, "checks": checks,
            "result": "fail" if any(c["result"] == "fail" for c in checks) else "infrastructure",
            "time": forge.dates[-1] if forge.dates else None}


def canary_result(forge, ls, clone_from, tmp, index_path=INDEX, say=print):
    """run_canary's result, or, when it stops on any exception, stopped()'s: a month that ends on an answer this
    code does not read still leaves its record, once a release is known."""
    state = {}
    try:
        return run_canary(forge, ls, clone_from, tmp, say=say, state=state)
    except Exception as e:  # noqa: BLE001 - every way a run stops is recorded, named by its type
        return stopped(e, state, forge, index_path)


def main(argv):
    ap = argparse.ArgumentParser(prog="ci/canary.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--github-output", default="")
    a = ap.parse_args(argv)
    try:
        F.refuse_tokens()
    except F.TokenInEnvironment as e:
        print(f"  canary: {e}")
        return 2
    forge = F.Forge()
    with tempfile.TemporaryDirectory(prefix="canary-") as tmp:
        res = canary_result(forge, D.ls_remote, f"https://github.com/{PACK}", tmp, index_path=INDEX)
    if not res["publish"] and res["checks"]:
        print(f"  canary: it stopped before any release was known: {res['checks'][-1]['detail']}; nothing is published")
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"publish={'true' if res['publish'] else 'false'}\n")
    print(f"  canary: {res['result']}, {len(res['checks'])} checks, {forge.requests} requests; written to {a.out}")
    return 0 if res["result"] in ("pass", "none") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
