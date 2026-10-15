#!/usr/bin/env python3
"""The pack checks and the canary run end to end against local copies, with no network (REG-409, REG-416): a
scratch clone of the pack repository at its anchor stage, and a bag of the pack committed on top of it as a release
would be. Each plant is a commit with one fault, and the check it breaks must fail by name.

    ci/tests/dry_run.py --pack-public <a clone of falden-fixtures/falden-fixture-pack>
                        (--build <the build tree> | --bag <a bag of the pack, such as a clone of a release>)
                        --token-sample <a timestamp token over other data> [--keep DIR]

bagit 1.9.0 runs as BAGIT_CMD names it, by default through uvx from its cache, and OpenSSL 3 is the one OPENSSL
names, or the one ci/run_checks.py finds.

  the anchor stage   cf42ad6 and the anchor tag's commit pass every check, the signature and the tag verified
                     with the keys ci/release-keys.json pins; planted on top: the signature cut, a timestamp token
                     swapped for one over other data, a workflow added, and three keys made here, outside the pin,
                     each named in anchor/allowed_signers: one added there, one that signs the manifest, and one
                     that signs the anchor tag (in a scratch repository of its own, the tag being the
                     repository's), each failing its checks and nothing else; and six commits more, each adding
                     there one line that names a fourth key made here as ssh-keygen reads it, with the pinned
                     release key where a field split finds it: in a quoted option, in quoted principals, after an
                     escaped quote, between unit separators or no-break spaces, or after the key made here and a
                     carriage return, at which ssh-keygen ends the principals, each failing the pinned keys' check
                     alone, naming its line, while a reader's ssh-keygen given that commit's file trusts the key
                     made here. The pack repository's first three commits, whose history holds no anchor manifest,
                     pass, the two that hold anchor/allowed_signers checked for its keys; and planted (the root's
                     ruling 7 for P12-26): a key made here added to anchor/allowed_signers at 2b78c56, which holds
                     no manifest, failing the pinned keys' check alone; the anchor's manifest removed, and anchor/
                     removed, each failing the manifests' check alone, naming the manifest; both faults of check
                     4's plant Y, the manifest removed and a key made here added, failing both checks, naming the
                     key and the manifest, while a reader's ssh-keygen given that file trusts the key; and six line
                     1s other than the release key's plain line, every key in the file pinned: a comment whose
                     third and fourth fields are a key made here, through which a reader's tag check, made by the
                     pack's VERIFYING.md command, trusts a tag that key signed; a blank line; the recovery key's
                     line; and the release key's line with no options, with the option cert-authority, and under
                     another principal; each failing the pinned keys' check alone, naming line 1; and each in a
                     leg of its own, whose clone of the scratch repository is checked out at cf42ad6: the anchor's
                     manifest renamed predicates-01.manifest or under the Arabic-Indic digit one, made a folder, a
                     link that leads nowhere or a submodule, each failing for the manifest that is gone, and a stray
                     predicates-02.manifest beside it, no anchor's, passing every check, as does the commit that
                     removes it again; anchor/allowed_signers, the signature, a timestamp token and the chains each
                     made a link to its copy in the leg's own clone of the pack repository, and anchor/ made such a
                     link at f47dcc3, each failing the checks that read through it, naming the link, while in a
                     reader's clone the link leads nowhere, so that the pack's VERIFYING.md signature command
                     fails there for the anchor/, signature and allowed_signers links; anchor/ made a link, inside
                     the commit, to a folder holding anchor #1's files and no allowed_signers, at f47dcc3 with
                     anchor #1's signature or one by a key made here, and at 2b78c56 (check 6's AL1 to AL3), anchor/
                     made a submodule at f47dcc3, a link at its root, and a link and a submodule three folders down
                     beside the anchor, each failing the check that the commit holds no link and no submodule
                     alone, naming it, as each link and submodule above does too (the root's ruling 8 (i)); and
                     bagit.txt added, whose checks stop on an error that fails the commit, naming it;
  the runner         (the root's ruling 8 (ii)) a leg whose PATH holds git, ssh, bash and sh but no ssh-keygen ends
                     with no result written, exit 2, naming the runner's fault, which the publish step records as
                     infrastructure beside the anchor leg, so the next run checks cf42ad6 again; and a leg whose
                     OPENSSL names nothing, as a path or as a bare name that no entry of PATH holds, passes that
                     candidate over and writes its result; while an error what the commit holds causes is no
                     runner's fault: bagit.txt, with data/ made a link to a folder this runner cannot enter (check
                     7's finding), checked in one leg with cf42ad6 after it, fails the check that the commit holds no
                     link and no submodule and the stopped check, naming the error, and cf42ad6 passes; (the root's
                     ruling 9 (ii)) cf42ad6 with an executable ssh-keygen of its own, which says every signature is
                     good, at its root or in tools/, and anchor #1's manifest changed, checked with '.', an empty
                     entry or tools first on PATH, fails the signature check alone, and with '.' first on a PATH
                     that holds no other ssh-keygen ends the leg with no result written, exit 2, which the publish
                     step records as infrastructure; and (ruling 9 (iii))
                     cf42ad6, checked under a global git configuration of the runner's naming a gpg.ssh.program that
                     does not exist, or sending the pack repository's address to another repository, whose anchor
                     tag a key made here signed, or under an attributes file of the runner's that turns every file's
                     line endings to CRLF, the global one in HOME or in the XDG folder, the system one of a git
                     first on PATH that reads it or one among that git's templates, or under a hook among those
                     templates that changes anchor #1's manifest, passes all 8 checks;
  the release stage  the bag (the build tree's head, made by its tools/bag.py into a clone of the pack repository,
                     or the bag given) committed there: every check of REG-409's list, the VERIFYING.md blocks
                     among them, and the anchor's checks and the manifests' check, which pass since the bag keeps
                     the checkout's anchor/, run as a leg on this machine runs them, with STATUS_OFFLINE=1, so the
                     blocks that install from the network are skipped and say so; a release candidate that holds
                     no witness record fails fixpack witness, as its VERIFYING.md says it does, and nothing else;
                     planted on top: a payload byte, a tag file removed, and a VERIFYING.md block no classification
                     names (the tag manifest resealed, so that block alone breaks), each failing by name, and a
                     payload file made a link to its copy in the leg's own clone, failing the check that the commit
                     holds no link and no submodule, bagit and fixpack verify, while sha256sum -c reads through it;
                     and data/ made a link to a folder this runner cannot enter (check 7's RDROOT), in a leg with
                     the release commit after it, failing that check and the stopped check, naming the error, where
                     the crash adapter's check runs in data/, while the release commit passes both, and in a leg
                     of its own failing that check and the result schema's, which names the error;
  the canary         on that commit tagged v1.0.0, a DOI and a Software Heritage snapshot written into the landing
                     README as a release adds them, against answers made for it in the shapes GitHub, doi.org,
                     Zenodo and Software Heritage give, served by a transport that refuses any other read: every
                     check passes, the three copies' fixity among them (the clone, a Zenodo zip and a vault tarball
                     of the same bag) and both archive copies held to the clone's tag manifest; planted: a moved
                     branch head, a repository not archived, a renamed principal, a Deprecation header, an /activity
                     count that changed and a Zenodo archive with a changed byte, each failing by name; a Zenodo
                     archive and a vault tarball each resealed after a change, a valid bag of other bytes, each
                     failing the check that holds it to the clone and nothing else; answers in a shape the canary
                     does not read, a Zenodo record whose archive
                     has no links and a vault that says done with no fetch_url, each a run that stops and is still
                     published, naming the release, a fail named by its type, with the checks made before it; and a
                     token in the environment, which stops the run. Each run goes through canary_result(), as
                     ci/canary.py's main() does, with no record of a release in this repository's records;
  the records        the legs and the canary's result published into a scratch copy of this repository: one record
                     per commit, the index and the README's table.
"""
import argparse
import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CI = os.path.dirname(HERE)
ROOT = os.path.dirname(CI)
sys.path.insert(0, CI)
import canary as C  # noqa: E402
import detect as D  # noqa: E402
import forge as F  # noqa: E402
import publish as P  # noqa: E402

FAILED = []
ANCHOR_MAIN = "cf42ad65c52a27df82137e78e7e72420ea615515"
# The pack repository's first three commits, before anchor #1: the README and the licenses, then
# anchor/allowed_signers, then the timestamp authorities' chains. None of their histories holds an anchor manifest.
FIRST = ("f47dcc33768a07972df447f4b2e1743225a701e8", "2b5f2ecb3c539633fa0d2869de05affc3ed823e5",
         "2b78c565b007fdd710e6aa06e7755665277ae4ac")
KEYSET = "anchor/allowed_signers: every key it names is pinned in ci/release-keys.json"
MANIFESTS = "anchor/: every anchor manifest a commit it descends from held, it holds too"
WORKFLOW = "the repository holds no workflow"
LINKS = "the commit holds no link and no submodule"
SIG = "anchor #1: its signature, with ssh-keygen -Y verify"
TSR, TSR2 = (f"anchor #1: its timestamp token anchor/predicates-1.{x}, with openssl ts -verify (OpenSSL 3)"
             for x in ("tsr", "tsr2"))
STOPPED = "the checks of this commit, run to their end"
BAGIT = os.environ.get("BAGIT_CMD") or "uvx --offline --exclude-newer 2026-10-01T00:00:00Z --from bagit==1.9.0 bagit.py"
DATE = "Wed, 14 Oct 2026 12:00:00 GMT"
# An ssh-keygen a commit holds of its own, which says every signature is good (the root's ruling 9 (ii) for P12-26).
OWN_KEYGEN = ("#!/bin/sh\necho 'Good \"falden-fixture-anchor\" signature for falden-fixture-release with ED25519 key, "
              "said by an ssh-keygen the commit holds'\nexit 0\n")


def prop(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}", flush=True)
    if not ok:
        FAILED.append(name)
        if detail:
            print(f"          {str(detail)[:1500]}")


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", "-c",
                        "user.name=dry run", "-c", "user.email=dry-run@example.invalid", *args],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])}: {r.stderr.strip()[-400:]}")
    return r.stdout.strip()


def planted_commit(repo, base, message, fn):
    """A commit on top of `base` with `fn(checkout)` applied, kept on a branch of its own so that every clone of the
    scratch repository carries it; its sha."""
    git(repo, "checkout", "-q", "--detach", base)
    fn(repo)
    git(repo, "add", "-A", "-f")  # -f: a global ignore file may list *.pem
    git(repo, "commit", "-q", "-m", message)
    sha = git(repo, "rev-parse", "HEAD")
    git(repo, "branch", "-f", f"planted/{sha[:12]}", sha)
    return sha


def leg(source, commits, out, checks="", extra_env=None):
    env = {k: v for k, v in os.environ.items() if k not in F.TOKEN_VARIABLES}
    env.update({"TODO": json.dumps(commits), "PYTHONDONTWRITEBYTECODE": "1"})
    env.update(extra_env or {})
    args = [sys.executable, "-B", os.path.join(CI, "run_checks.py"), "--commits-env", "TODO", "--leg",
            f"{sys.platform} (dry run), Python {sys.version.split()[0]}", "--python", sys.executable,
            "--source", source, "--out", out]
    if checks:
        args += ["--checks", checks]
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run(args, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    sys.stdout.write("".join(f"      {ln}\n" for ln in (r.stdout + r.stderr).strip().splitlines()))
    # A leg that ends on a traceback writes no result: its commits are then missing, and their properties fail.
    return r.returncode, json.load(open(out)) if os.path.exists(out) else {"commits": []}


def by_name(res, sha):
    c = next(x for x in res["commits"] if x["commit"] == sha)
    return {k["name"]: k for k in c["checks"]}, c


def failing(res, sha):
    return [n for n, k in by_name(res, sha)[0].items() if k["result"] == "fail"]


def anchor_stage(t, pp, token_sample):
    repo = os.path.join(t, "anchor-repo")
    git(t, "clone", "-q", pp, repo)
    tag = git(repo, "rev-parse", "refs/tags/anchor/predicates-1^{commit}")
    todo = [{"commit": ANCHOR_MAIN, "refs": ["refs/heads/main"]}, {"commit": tag, "refs": ["refs/tags/anchor/predicates-1"]}]
    rc, res = leg(repo, todo, os.path.join(t, "leg-anchor.json"))
    ok = rc == 0 and all(c["stage"] == "anchor" and c["result"] == "pass" and len(c["checks"]) == 8
                         and {KEYSET, MANIFESTS, LINKS} <= {k["name"] for k in c["checks"]} for c in res["commits"])
    prop(f"anchor stage: {ANCHOR_MAIN[:7]} (main) and {tag[:7]} (anchor/predicates-1) pass all 8 checks each, the "
         f"pinned keys', the manifests' and the links' among them", ok, res)
    rc, res = leg(repo, [{"commit": c, "refs": []} for c in FIRST], os.path.join(t, "leg-anchor-first.json"))
    got = [(c["stage"], c["result"], [k["name"] for k in c["checks"]]) for c in res["commits"]]
    prop("the pack repository's first three commits, whose history holds no anchor manifest, pass as they did: "
         f"{FIRST[0][:7]} at no stage, and {FIRST[1][:7]} and {FIRST[2][:7]}, which hold anchor/allowed_signers, at "
         "the anchor stage, its keys checked", rc == 0 and got == [
             ("none", "pass", [WORKFLOW, LINKS, MANIFESTS]), ("anchor", "pass", [WORKFLOW, LINKS, MANIFESTS, KEYSET]),
             ("anchor", "pass", [WORKFLOW, LINKS, MANIFESTS, KEYSET])], got)
    ruling_seven(t, repo, tag)
    kinds(t, repo)
    runner_fault(t, repo, os.path.join(t, "leg-anchor.json"))
    unenterable(t, repo)
    own_tools(t, repo)
    git_config(t, repo, pp)
    plants = []

    def cut(w):
        p = os.path.join(w, "anchor", "predicates-1.sig")
        data = open(p, "rb").read()
        open(p, "wb").write(data[: len(data) // 2])
    plants.append(("the signature cut", cut, ["anchor #1: its signature, with ssh-keygen -Y verify",
                                              "anchor #1: its timestamp token anchor/predicates-1.tsr, with openssl ts -verify (OpenSSL 3)",
                                              "anchor #1: its timestamp token anchor/predicates-1.tsr2, with openssl ts -verify (OpenSSL 3)"]))
    plants.append(("a timestamp token swapped for one over other data",
                   lambda w: shutil.copy(token_sample, os.path.join(w, "anchor", "predicates-1.tsr")),
                   ["anchor #1: its timestamp token anchor/predicates-1.tsr, with openssl ts -verify (OpenSSL 3)"]))

    def workflow(w):
        os.makedirs(os.path.join(w, ".github", "workflows"))
        open(os.path.join(w, ".github", "workflows", "verify.yml"), "w").write("name: verify\non: [push]\n")
    plants.append(("a workflow added", workflow, ["the repository holds no workflow"]))
    added = planted_key(t, "planted-key-added")
    plants.append(("a key the pin lacks added to anchor/allowed_signers",
                   lambda w: open(os.path.join(w, "anchor", "allowed_signers"), "a").write(added[1]), [KEYSET]))
    signer = planted_key(t, "planted-key-manifest")

    def resigned(w):
        open(os.path.join(w, "anchor", "allowed_signers"), "a").write(signer[1])
        man = os.path.join(w, "anchor", "predicates-1.manifest")
        subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", signer[0], "-n", "falden-fixture-anchor", man],
                       check=True, capture_output=True, stdin=subprocess.DEVNULL)
        os.replace(man + ".sig", os.path.join(w, "anchor", "predicates-1.sig"))
    plants.append(("the manifest signed by a key the pin lacks, which anchor/allowed_signers names", resigned,
                   [KEYSET, "anchor #1: its signature, with ssh-keygen -Y verify",
                    "anchor #1: its timestamp token anchor/predicates-1.tsr, with openssl ts -verify (OpenSSL 3)",
                    "anchor #1: its timestamp token anchor/predicates-1.tsr2, with openssl ts -verify (OpenSSL 3)"]))
    # A line ssh-keygen reads as naming a key the pin lacks, the pinned release key written where it reads no key
    # (P12-26's check of round 3 found the first): KEYSET alone fails, naming the line, while a reader's ssh-keygen,
    # given the commit's anchor/allowed_signers as the pack's VERIFYING.md gives it, trusts that key.
    readers = {}
    two = planted_key(t, "planted-key-two-ways")
    key = " ".join(two[1].split()[2:4])
    release = json.load(open(os.path.join(CI, "release-keys.json"), encoding="utf-8"))["keys"][0]["key"]
    rt, rb = release.split()
    ns = 'namespaces="falden-fixture-anchor"'
    for label, line in (
            ("inside a quoted option", f'falden-fixture-release namespaces="falden-fixture-anchor,z {release} z" {key} two-ways'),
            ("inside quoted principals", f'"falden-fixture-release,z {release} z" {ns} {key} two-ways'),
            ("after an escaped quote inside a quoted option",
             f'falden-fixture-release namespaces="falden-fixture-anchor,z\\" {release} " {key} two-ways'),
            ("between unit separators (0x1f)", f"falden-fixture-release,z\x1f{rt}\x1f{rb}\x1fz {ns} {key} two-ways"),
            ("between no-break spaces (U+00A0)", f"falden-fixture-release,z\u00a0{rt}\u00a0{rb}\u00a0z {ns} {key} two-ways"),
            ("after it, a carriage return ending the principals for ssh-keygen",
             f"falden-fixture-release\r{key} {release} two-ways")):
        name = f"a key the pin lacks named on a line of anchor/allowed_signers with the pinned release key {label}"
        readers[name] = two[0]
        plants.append((name, lambda w, line=line: open(os.path.join(w, "anchor", "allowed_signers"), "ab").write(
            (line + "\n").encode("utf-8")), [KEYSET]))
    shas = [(name, planted_commit(repo, ANCHOR_MAIN, f"planted: {name}", fn), want) for name, fn, want in plants]
    rc, res = leg(repo, [{"commit": s, "refs": []} for _n, s, _w in shas], os.path.join(t, "leg-anchor-plants.json"))
    for name, sha, want in shas:
        got = failing(res, sha)
        if name not in readers:
            prop(f"anchor stage, planted: {name}: fails {', '.join(want)}, and nothing else", sorted(got) == sorted(want), got)
            continue
        said = by_name(res, sha)[0].get(KEYSET, {}).get("detail", "")
        trusts = reader_trusts(repo, sha, readers[name], t)
        prop(f"anchor stage, planted: {name}: fails {', '.join(want)}, naming line 3, and nothing else, while a "
             f"reader's ssh-keygen given that commit's anchor/allowed_signers trusts a manifest the planted key signed",
             sorted(got) == sorted(want) and "line 3 " in said and trusts,
             {"failing": got, "detail": said, "a reader's ssh-keygen trusts the planted key": trusts})
    # The anchor tag signed by a key the pin lacks, which anchor/allowed_signers names first, as the pack's VERIFYING.md
    # reads the tag's key from that file: in a scratch repository of its own, since the tag is the repository's.
    repo2 = os.path.join(t, "anchor-repo-tag")
    git(t, "clone", "-q", pp, repo2)
    tagger = planted_key(t, "planted-key-tag")

    def first(w):
        p = os.path.join(w, "anchor", "allowed_signers")
        held = open(p).read()
        open(p, "w").write(tagger[1] + held)
    sha = planted_commit(repo2, ANCHOR_MAIN, "planted: the anchor tag signed by a key the pin lacks", first)
    git(repo2, "-c", "gpg.format=ssh", "-c", f"user.signingkey={tagger[0]}", "tag", "-s", "-f", "-m",
        "planted: anchor #1's tag, signed by a key the pin lacks", "anchor/predicates-1", sha)
    rc, res = leg(repo2, [{"commit": sha, "refs": []}], os.path.join(t, "leg-anchor-tag.json"))
    want = [KEYSET, "anchor #1: its tag anchor/predicates-1, with git verify-tag"]
    got = failing(res, sha)
    prop(f"anchor stage, planted: the anchor tag signed by a key the pin lacks, which anchor/allowed_signers names "
         f"first: fails {', '.join(want)}, and nothing else", sorted(got) == sorted(want), got)
    return [os.path.join(t, "leg-anchor.json")]


def planted_key(t, name):
    """A key made here, which ci/release-keys.json does not pin: (its private key's path, its line for
    anchor/allowed_signers, under the release principal)."""
    path = os.path.join(t, name)
    if not os.path.exists(path):
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", name, "-f", path], check=True,
                       capture_output=True, stdin=subprocess.DEVNULL)
    typ, blob = open(path + ".pub").read().split()[:2]
    return path, f'falden-fixture-release namespaces="falden-fixture-anchor" {typ} {blob} {name}\n'


def reader_trusts(repo, sha, key_path, t):
    """Whether a reader's `ssh-keygen -Y verify`, run as the pack's VERIFYING.md runs it, with the commit's
    anchor/allowed_signers (falden-fixture-release, namespace falden-fixture-anchor), trusts a manifest the key at
    `key_path` signed."""
    d = tempfile.mkdtemp(prefix="reader-", dir=t)
    signers, man = os.path.join(d, "allowed_signers"), os.path.join(d, "manifest")
    open(signers, "wb").write(subprocess.run(["git", "-C", repo, "show", f"{sha}:anchor/allowed_signers"],
                                             capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout)
    open(man, "w").write("# a manifest the planted key signed\n")
    subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", key_path, "-n", "falden-fixture-anchor", man], check=True,
                   capture_output=True, stdin=subprocess.DEVNULL)
    with open(man, "rb") as fh:
        r = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", "falden-fixture-release", "-n",
                            "falden-fixture-anchor", "-s", man + ".sig"], stdin=fh, capture_output=True, text=True,
                           errors="replace")
    return r.returncode == 0 and "Good" in r.stdout + r.stderr


# The reader's tag check, the pack's VERIFYING.md:643 and :644 as the pack prints them, run in a tree that holds the
# commit's anchor/allowed_signers, with the signers file moved from /tmp into the scratch folder and the clone that
# holds the tag named by -C.
READER_TAG = ("printf 'release@falden.ai namespaces=\"git\" %s\\n' \"$(awk 'NR==1 {print $3, $4}' "
              "anchor/allowed_signers)\" > \"$SIGNERS\"\n"
              "git -C \"$CLONE\" -c gpg.ssh.allowedSignersFile=\"$SIGNERS\" verify-tag anchor/predicates-1\n")


def reader_tag_trusts(repo, sha, key_path, t):
    """Whether a reader's tag check, made as the pack's VERIFYING.md makes it from the commit's anchor/allowed_signers,
    admits an anchor tag the key at `key_path` signed, in a scratch repository of its own."""
    d = tempfile.mkdtemp(prefix="reader-tag-", dir=t)
    os.makedirs(os.path.join(d, "tree", "anchor"))
    open(os.path.join(d, "tree", "anchor", "allowed_signers"), "wb").write(subprocess.run(
        ["git", "-C", repo, "show", f"{sha}:anchor/allowed_signers"], capture_output=True, check=True,
        stdin=subprocess.DEVNULL).stdout)
    clone = os.path.join(d, "clone")
    git(d, "init", "-q", "-b", "main", clone)
    open(os.path.join(clone, "f.txt"), "w").write("x\n")
    git(clone, "add", "f.txt")
    git(clone, "commit", "-q", "-m", "one")
    git(clone, "-c", "gpg.format=ssh", "-c", f"user.signingkey={key_path}", "tag", "-s", "-m",
        "a tag a key the pin lacks signed", "anchor/predicates-1", "HEAD")
    env = dict(F.git_env(), SIGNERS=os.path.join(d, "falden-tag-signers"), CLONE=clone)
    r = subprocess.run(["bash", "-c", READER_TAG], cwd=os.path.join(d, "tree"), env=env, capture_output=True,
                       text=True, stdin=subprocess.DEVNULL, errors="replace")
    return r.returncode == 0 and 'Good "git" signature' in r.stdout + r.stderr


def ruling_seven(t, repo, tag):
    """The root's ruling 7 for P12-26, planted on the pack repository's own commits: the keys anchor/allowed_signers
    names, checked at a commit that holds no anchor manifest (i); every anchor manifest a commit's history held, a
    history the clone cannot show being infrastructure (ii); and line 1 of anchor/allowed_signers (iii)."""
    held = git(repo, "show", f"{ANCHOR_MAIN}:anchor/allowed_signers") + "\n"
    rel, rec = held.splitlines(keepends=True)  # the release key's line, then the recovery key's
    release = json.load(open(os.path.join(CI, "release-keys.json"), encoding="utf-8"))["keys"][0]["key"]
    ns = 'namespaces="falden-fixture-anchor"'
    path, line = planted_key(t, "planted-key-seven")
    key = " ".join(line.split()[2:4])
    fp = subprocess.run(["ssh-keygen", "-l", "-E", "sha256", "-f", path + ".pub"], capture_output=True, text=True,
                        stdin=subprocess.DEVNULL).stdout.split()[1]
    man = os.path.join("anchor", "predicates-1.manifest")
    gone = "anchor/predicates-1.manifest is gone"

    def signers(w, text, mode="w"):
        open(os.path.join(w, "anchor", "allowed_signers"), mode).write(text)

    def plant_y(w):
        os.remove(os.path.join(w, man))
        signers(w, line, "a")
    plants = (  # name, base, fault, failing, stage, what each failing check names, a reader's view
        (f"a key the pin lacks added to anchor/allowed_signers at {FIRST[2][:7]}, whose history holds no anchor manifest",
         FIRST[2], lambda w: signers(w, line, "a"), [KEYSET], "anchor", {KEYSET: fp}, None),
        ("the anchor's manifest removed", ANCHOR_MAIN, lambda w: os.remove(os.path.join(w, man)), [MANIFESTS], "anchor",
         {MANIFESTS: gone}, None),
        ("anchor/ removed", ANCHOR_MAIN, lambda w: shutil.rmtree(os.path.join(w, "anchor")), [MANIFESTS], "none",
         {MANIFESTS: gone}, None),
        ("check 4's plant Y, the anchor's manifest removed and a key the pin lacks added to anchor/allowed_signers",
         ANCHOR_MAIN, plant_y, [KEYSET, MANIFESTS], "anchor", {KEYSET: fp, MANIFESTS: gone}, "signature"),
        ("line 1 a comment whose third and fourth fields are a key the pin lacks", ANCHOR_MAIN,
         lambda w: signers(w, f"# falden-fixture-release {key} planted\n" + rel + rec), [KEYSET], "anchor",
         {KEYSET: "line 1 "}, "tag"),
        ("line 1 a blank line", ANCHOR_MAIN, lambda w: signers(w, "\n" + rel + rec), [KEYSET], "anchor",
         {KEYSET: "line 1 "}, None),
        ("line 1 the recovery key's line, the release key's after it", ANCHOR_MAIN, lambda w: signers(w, rec + rel),
         [KEYSET], "anchor", {KEYSET: "line 1 "}, None),
        ("line 1 the release key's line with no options", ANCHOR_MAIN,
         lambda w: signers(w, f"falden-fixture-release {release} falden-fixture-release\n" + rel + rec), [KEYSET],
         "anchor", {KEYSET: "line 1 "}, None),
        ("line 1 the release key's line with the option cert-authority", ANCHOR_MAIN,
         lambda w: signers(w, f"falden-fixture-release cert-authority,{ns} {release} falden-fixture-release\n" + rec),
         [KEYSET], "anchor", {KEYSET: "line 1 "}, None),
        ("line 1 the release key's line under another principal", ANCHOR_MAIN,
         lambda w: signers(w, f"falden-fixture-recovery {ns} {release} falden-fixture-release\n" + rel + rec),
         [KEYSET], "anchor", {KEYSET: "line 1 "}, None))
    shas = [(p, planted_commit(repo, p[1], f"planted: {p[0]}", p[2])) for p in plants]
    rc, res = leg(repo, [{"commit": s, "refs": []} for _p, s in shas], os.path.join(t, "leg-anchor-ruling7.json"))
    label = {fp: "the key", gone: "the manifest", "line 1 ": "line 1"}
    for (name, _base, _fn, want, stage, said, reader), sha in shas:
        checks, c = by_name(res, sha)
        got = failing(res, sha)
        named = all(v in checks.get(k, {}).get("detail", "") for k, v in said.items())
        trusts = (reader_trusts(repo, sha, path, t) if reader == "signature" else
                  reader_tag_trusts(repo, sha, path, t) if reader == "tag" else True)
        prop(f"anchor stage, planted: {name}: fails {' and '.join(sorted(want))}, naming "
             f"{' and '.join(label[v] for _k, v in sorted(said.items()))}, and nothing else, "
             + ("at no stage" if stage == "none" else f"at the {stage} stage")
             + {"signature": ", while a reader's ssh-keygen given that commit's anchor/allowed_signers trusts a "
                             "manifest the key the pin lacks signed",
                "tag": ", while a reader's tag check, made from that commit's anchor/allowed_signers by the pack's "
                       "VERIFYING.md command, trusts a tag the key the pin lacks signed"}.get(reader, ""),
             sorted(got) == sorted(want) and c["stage"] == stage and named and trusts,
             {"failing": got, "stage": c["stage"], "details": {k: checks.get(k, {}).get("detail", "")[:300] for k in said},
              "the reader's view": trusts})
    # A history the clone cannot show: the manifest-removed plant, read from a shallow clone of the scratch repository.
    sha = shas[1][1]
    shallow = os.path.join(t, "anchor-repo-shallow")
    git(t, "clone", "-q", "--depth", "1", "--branch", f"planted/{sha[:12]}", "file://" + repo, shallow)
    rc, res = leg(shallow, [{"commit": sha, "refs": []}], os.path.join(t, "leg-anchor-shallow.json"))
    checks, c = by_name(res, sha)
    k = checks.get(MANIFESTS, {})
    prop("anchor stage, planted: the anchor's manifest removed, read from a shallow clone: the manifests' check is "
         "infrastructure, never a pass, and so is the commit, exit 2", rc == 2 and c["result"] == "infrastructure"
         and k.get("result") == "infrastructure" and "shallow" in k.get("detail", ""), (rc, c["result"], k))


def reader_signature_verifies(repo, sha, t):
    """Whether a reader's clone of the commit verifies anchor #1's signature with the pack's VERIFYING.md command,
    run from the clone's root as the page says, the clone made where no folder named pack sits beside it."""
    d = tempfile.mkdtemp(prefix="reader-clone-", dir=t)
    clone = os.path.join(d, "a", "clone")
    git(t, "clone", "-q", "--no-checkout", repo, clone)
    git(clone, "checkout", "-q", "--detach", sha)
    cmd = ("ssh-keygen -Y verify -f anchor/allowed_signers -I falden-fixture-release -n falden-fixture-anchor "
           "-s anchor/predicates-1.sig < anchor/predicates-1.manifest")
    r = subprocess.run(["bash", "-c", cmd], cwd=clone, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                       errors="replace")
    return r.returncode == 0 and "Good" in r.stdout + r.stderr


def kinds(t, repo):
    """What the anchor stage reads, planted on the pack repository's own commits, each checked in a leg of its own,
    whose clone of the pack repository is checked out at main, cf42ad6, as a leg's clone on GitHub is at the default
    branch: an anchor manifest is a file named anchor/predicates-<N>.manifest, its number written as the pack writes
    it, and each file the anchor checks read is the commit's own, never a link, nor under one, nor a folder, so that
    none of them reads the copy in the leg's own clone of the pack repository, which no reader's clone of the commit
    holds; a commit that holds a link or a submodule anywhere in its tree fails, at every stage, whatever its history
    (the root's ruling 8 (i)); and a check that stops on an error fails its commit, naming the error."""
    man = os.path.join("anchor", "predicates-1.manifest")
    gone = "anchor/predicates-1.manifest is gone"

    def link_to_clone(rel):
        """`rel` made a link to the same path in the leg's own clone of the pack repository, tmp/pack, beside the
        commit's checkout tmp/wt-<commit>/tree."""
        def fn(w):
            p = os.path.join(w, *rel.split("/"))
            if os.path.lexists(p):
                shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)
            os.symlink("../" * rel.count("/") + "../../pack/" + rel, p)
        return fn

    def folder(w):
        os.remove(os.path.join(w, man))
        os.makedirs(os.path.join(w, man))
        open(os.path.join(w, man, "f"), "w").write("x\n")

    def dangling(w):
        os.remove(os.path.join(w, man))
        os.symlink("nowhere", os.path.join(w, man))

    def gitlink(w, rel):  # an empty folder at a gitlink's path keeps git add -A from dropping it
        os.makedirs(os.path.join(w, *rel.split("/")))
        git(w, "update-index", "--add", "--cacheinfo", f"160000,{ANCHOR_MAIN},{rel}")

    def submodule(w):
        os.remove(os.path.join(w, man))
        gitlink(w, "anchor/predicates-1.manifest")
    signer = planted_key(t, "planted-key-elsewhere")

    def anchor_elsewhere(with_chains_from_anchor=False, planted_signature=False):
        """anchor/ made a link, inside the commit, to elsewhere/, which holds anchor #1's manifest, its signature
        (cf42ad6's, or one by a key the pin lacks), both tokens and the chains, and no allowed_signers (check 6's
        AL1 to AL3, b3afb13 and 60784c2 failing them, 8c796cb passing them at two checks)."""
        def fn(w):
            os.makedirs(os.path.join(w, "elsewhere"))
            names = ["predicates-1.manifest", "predicates-1.tsr", "predicates-1.tsr2"]
            names += [] if planted_signature else ["predicates-1.sig"]
            names += [] if with_chains_from_anchor else ["tsa-ca.pem"]
            for f in names:
                open(os.path.join(w, "elsewhere", f), "wb").write(subprocess.run(
                    ["git", "-C", repo, "show", f"{ANCHOR_MAIN}:anchor/{f}"], capture_output=True, check=True,
                    stdin=subprocess.DEVNULL).stdout)
            if planted_signature:
                m = os.path.join(w, "elsewhere", "predicates-1.manifest")
                subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", signer[0], "-n", "falden-fixture-anchor", m],
                               check=True, capture_output=True, stdin=subprocess.DEVNULL)
                os.replace(m + ".sig", os.path.join(w, "elsewhere", "predicates-1.sig"))
            if with_chains_from_anchor:
                os.replace(os.path.join(w, "anchor", "tsa-ca.pem"), os.path.join(w, "elsewhere", "tsa-ca.pem"))
            if os.path.lexists(os.path.join(w, "anchor")):
                shutil.rmtree(os.path.join(w, "anchor"))
            os.symlink("elsewhere", os.path.join(w, "anchor"))
        return fn

    def deep_link(w):
        os.makedirs(os.path.join(w, "docs", "a", "b", "c"))
        open(os.path.join(w, "docs", "a", "b", "real.txt"), "w").write("x\n")
        os.symlink("../real.txt", os.path.join(w, "docs", "a", "b", "c", "link.txt"))
    stray02 = os.path.join("anchor", "predicates-02.manifest")
    stray = planted_commit(repo, ANCHOR_MAIN, "planted: a stray anchor/predicates-02.manifest beside the manifest",
                           lambda w: shutil.copy(os.path.join(w, man), os.path.join(w, stray02)))
    link = ", and the anchor stage reads no file through a link"
    plants = (  # name, base or a commit made, fault, failing, what each failing check names, checks, a reader's view,
        # the stage
        ("the anchor's manifest renamed anchor/predicates-01.manifest, no anchor's name", ANCHOR_MAIN,
         lambda w: os.rename(os.path.join(w, man), os.path.join(w, "anchor", "predicates-01.manifest")), [MANIFESTS],
         {MANIFESTS: gone}, 4, None, "anchor"),
        ("the anchor's manifest renamed under the Arabic-Indic digit one, which Python's \\d reads as 1", ANCHOR_MAIN,
         lambda w: os.rename(os.path.join(w, man), os.path.join(w, "anchor", "predicates-\u0661.manifest")),
         [MANIFESTS], {MANIFESTS: gone}, 4, None, "anchor"),
        ("the anchor's manifest made a folder", ANCHOR_MAIN, folder, [MANIFESTS, SIG],
         {MANIFESTS: gone, SIG: "anchor/predicates-1.manifest is a folder"}, 8, None, "anchor"),
        ("the anchor's manifest made a link that leads nowhere", ANCHOR_MAIN, dangling, [MANIFESTS, SIG, LINKS],
         {MANIFESTS: gone, SIG: "anchor/predicates-1.manifest is a link" + link,
          LINKS: "anchor/predicates-1.manifest is a link (1 in all)"}, 8, None, "anchor"),
        ("the anchor's manifest made a submodule", ANCHOR_MAIN, submodule, [MANIFESTS, SIG, LINKS],
         {MANIFESTS: gone, SIG: "anchor/predicates-1.manifest is a folder",
          LINKS: "anchor/predicates-1.manifest is a submodule (1 in all)"}, 8, None, "anchor"),
        ("a stray anchor/predicates-02.manifest beside the manifest, no anchor's name", stray, None, [], {}, 8, None,
         "anchor"),
        ("that stray removed again", stray, lambda w: os.remove(os.path.join(w, stray02)), [], {}, 8, None, "anchor"),
        (f"anchor/ made a link to anchor/ in the leg's own clone of the pack repository, at {FIRST[0][:7]}, which "
         f"holds no anchor/", FIRST[0], link_to_clone("anchor"), [KEYSET, LINKS],
         {KEYSET: "anchor/allowed_signers lies under anchor, which is a link" + link, LINKS: "anchor is a link (1 in all)"},
         4, False, "anchor"),
        ("the signature made a link to its copy in the leg's own clone of the pack repository", ANCHOR_MAIN,
         link_to_clone("anchor/predicates-1.sig"), [SIG, TSR, TSR2, LINKS],
         {SIG: "anchor/predicates-1.sig is a link" + link, TSR: "anchor/predicates-1.sig is a link",
          TSR2: "anchor/predicates-1.sig is a link", LINKS: "anchor/predicates-1.sig is a link (1 in all)"}, 8, False,
         "anchor"),
        ("anchor/allowed_signers made a link to its copy in the leg's own clone of the pack repository", ANCHOR_MAIN,
         link_to_clone("anchor/allowed_signers"), [KEYSET, LINKS],
         {KEYSET: "anchor/allowed_signers is a link" + link, LINKS: "anchor/allowed_signers is a link (1 in all)"}, 8,
         False, "anchor"),
        ("a timestamp token made a link to its copy in the leg's own clone of the pack repository", ANCHOR_MAIN,
         link_to_clone("anchor/predicates-1.tsr"), [TSR, LINKS],
         {TSR: "anchor/predicates-1.tsr is a link" + link, LINKS: "anchor/predicates-1.tsr is a link (1 in all)"}, 8,
         None, "anchor"),
        ("the chains made a link to their copy in the leg's own clone of the pack repository", ANCHOR_MAIN,
         link_to_clone("anchor/tsa-ca.pem"), [TSR, TSR2, LINKS],
         {TSR: "anchor/tsa-ca.pem is a link", TSR2: "anchor/tsa-ca.pem is a link",
          LINKS: "anchor/tsa-ca.pem is a link (1 in all)"}, 8, None, "anchor"),
        ("bagit.txt added, which takes the commit to the release stage with no data/ to run in", ANCHOR_MAIN,
         lambda w: open(os.path.join(w, "bagit.txt"), "w").write("BagIt-Version: 1.0\n"), [STOPPED],
         {STOPPED: "No such file or directory"}, 9, None, "release"),
        # The root's ruling 8 (i): a link or a submodule anywhere in the tree, whatever the stage and the history.
        (f"anchor/ made a link, inside the commit, to a folder holding anchor #1's manifest, signature, tokens and "
         f"chains and no allowed_signers, at {FIRST[0][:7]}, whose history holds no manifest (check 6's AL1)",
         FIRST[0], anchor_elsewhere(), [LINKS], {LINKS: "anchor is a link (1 in all)"}, 3, False, "anchor"),
        ("the same, the signature made by a key the pin lacks (check 6's AL2)", FIRST[0],
         anchor_elsewhere(planted_signature=True), [LINKS], {LINKS: "anchor is a link (1 in all)"}, 3, False,
         "anchor"),
        (f"anchor/ replaced by such a link at {FIRST[2][:7]}, its chains moved there and allowed_signers left out, "
         f"the signature by a key the pin lacks (check 6's AL3)", FIRST[2],
         anchor_elsewhere(with_chains_from_anchor=True, planted_signature=True), [LINKS],
         {LINKS: "anchor is a link (1 in all)"}, 3, False, "anchor"),
        (f"anchor/ made a submodule at {FIRST[0][:7]}, whose history holds no manifest", FIRST[0],
         lambda w: gitlink(w, "anchor"), [LINKS], {LINKS: "anchor is a submodule (1 in all)"}, 3, None, "anchor"),
        (f"a link at the root of {FIRST[0][:7]}, which holds no anchor/", FIRST[0],
         lambda w: os.symlink("README.md", os.path.join(w, "notes.txt")), [LINKS],
         {LINKS: "notes.txt is a link (1 in all)"}, 3, None, "none"),
        ("a link three folders down, beside the anchor", ANCHOR_MAIN, deep_link, [LINKS],
         {LINKS: "docs/a/b/c/link.txt is a link (1 in all)"}, 8, None, "anchor"),
        ("a submodule three folders down, beside the anchor", ANCHOR_MAIN, lambda w: gitlink(w, "x/y/z"), [LINKS],
         {LINKS: "x/y/z is a submodule (1 in all)"}, 8, None, "anchor"))
    shas = [(p, p[1] if p[2] is None else planted_commit(repo, p[1], f"planted: {p[0]}", p[2])) for p in plants]
    git(repo, "checkout", "-q", "main")  # each leg's clone of the scratch repository is then checked out at cf42ad6
    for (name, _base, _fn, want, said, n, reader, stage), sha in shas:
        out = os.path.join(t, f"leg-kinds-{sha[:12]}.json")
        rc, res = leg(repo, [{"commit": sha, "refs": []}], out,
                      extra_env={"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"} if STOPPED in want else None)
        c = next((x for x in res["commits"] if x["commit"] == sha), None)
        if c is None:
            prop(f"anchor stage, planted: {name}", False, f"the leg wrote no result for {sha[:12]}, exit {rc}")
            continue
        checks = {k["name"]: k for k in c["checks"]}
        got = sorted(k for k, v in checks.items() if v["result"] == "fail")
        named = all(v in checks.get(k, {}).get("detail", "") for k, v in said.items())
        views = reader_signature_verifies(repo, sha, t) if reader is not None else None
        prop(f"anchor stage, planted: {name}: " + (f"fails {' and '.join(sorted(want))}, naming "
             f"{'the error' if STOPPED in want else 'it'}, and nothing else" if want else "passes every check")
             + f", {n} checks, " + ("at no stage" if stage == "none" else f"at the {stage} stage")
             + (", while a reader's clone of it does not verify the anchor's signature with the pack's VERIFYING.md "
                "command" if reader is False else ""),
             got == sorted(want) and named and len(checks) == n and c["stage"] == stage and views is reader,
             {"failing": got, "stage": c["stage"], "checks": len(checks), "a reader's clone verifies": views,
              "details": {k: checks.get(k, {}).get("detail", "")[:240] for k in said}})


def runner_fault(t, repo, anchor_leg):
    """The root's ruling 8 (ii): a runner fault is infrastructure, not a verdict. A leg on a machine whose PATH holds
    what the leg starts but ssh-keygen (check 6's runner_fault.sh) ends with no result written, exit 2, naming the
    fault; the publish step records that leg as infrastructure beside the anchor leg, which passed cf42ad6, and the
    next six-hourly run checks cf42ad6 again. And an OPENSSL that names nothing, as a path or as a bare name that no
    entry of PATH holds, is a candidate passed over: the leg finds another OpenSSL 3 and writes its result."""
    tools = os.path.join(t, "no-ssh-keygen-bin")
    os.makedirs(tools)
    for n in ("git", "ssh", "bash", "sh"):
        if shutil.which(n):
            os.symlink(shutil.which(n), os.path.join(tools, n))
    out = os.path.join(t, "leg-no-ssh-keygen.json")
    env = {k: v for k, v in os.environ.items() if k not in F.TOKEN_VARIABLES}
    env.update({"TODO": json.dumps([{"commit": ANCHOR_MAIN, "refs": ["refs/heads/main"]}]), "PATH": tools,
                "PYTHONDONTWRITEBYTECODE": "1"})
    r = subprocess.run([sys.executable, "-B", os.path.join(CI, "run_checks.py"), "--commits-env", "TODO", "--leg",
                        "a runner with no ssh-keygen (dry run)", "--python", sys.executable, "--source", repo, "--out",
                        out], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    said = (r.stdout + r.stderr).strip()
    sys.stdout.write("".join(f"      {ln}\n" for ln in said.splitlines()[-4:]))
    prop("runner fault, planted: a PATH holding git, ssh, bash and sh but no ssh-keygen: the leg ends with no result "
         "written, exit 2, naming the runner's fault, never a fail of cf42ad6", r.returncode == 2
         and not os.path.exists(out) and "the runner cannot start ssh-keygen" in said and "the runner's fault" in said,
         {"exit": r.returncode, "written": os.path.exists(out), "said": said[-600:]})
    commits = [{"commit": ANCHOR_MAIN, "refs": ["refs/heads/main"]}]
    recs = P.pack_records(commits, DATE, [P.read_leg(anchor_leg), P.read_leg(out)], 2, "Wed, 14 Oct 2026 12:30:00 GMT",
                          {"id": "dry-run", "attempt": "1", "event": "schedule", "url": ""})
    rec = recs[0][1]
    again = (ANCHOR_MAIN, ("refs/heads/main",)) not in D.recorded(
        {"records": [{"workflow": "pack-checks", "commit": ANCHOR_MAIN, "refs": ["refs/heads/main"],
                      "result": rec["result"]}]})
    prop("runner fault: the publish step records that leg as infrastructure beside the anchor leg, which passed "
         "cf42ad6, and the next six-hourly run checks cf42ad6 again", rec["result"] == "infrastructure"
         and [e["result"] for e in rec["legs"]] == ["pass", "infrastructure"] and again,
         {"result": rec["result"], "legs": [e["result"] for e in rec["legs"]], "checked again": again})
    # OPENSSL naming a path that holds nothing, and a bare name that no entry of the leg's PATH holds (the round 9
    # check's K8): each a candidate passed over.
    for key, named, how in (("names-nothing", os.path.join(t, "no-such-openssl"), "naming a path that holds nothing"),
                            ("bare-name", "no-such-openssl-made-here", "a bare name that no entry of PATH holds")):
        out2 = os.path.join(t, f"leg-openssl-{key}.json")
        rc, res = leg(repo, commits, out2, extra_env={"OPENSSL": named})
        c = next((x for x in res["commits"] if x["commit"] == ANCHOR_MAIN), {})
        prop(f"runner fault, planted: OPENSSL {how}: that candidate is passed over and the leg writes its result, "
             f"cf42ad6 passing every check with another OpenSSL 3, or its token checks infrastructure when this machine "
             f"holds none", c.get("result") == "pass" and len(c.get("checks", [])) == 8
             or c.get("result") == "infrastructure",
             {"exit": rc, "result": c.get("result"), "checks": [(k["name"][:50], k["result"], k["detail"][-160:])
                                                                for k in c.get("checks", [])]})


def locked_folder(t):
    """A folder of the scratch tree that a plant's data/ is made a link to, which a leg cannot enter while its mode is
    000 (shut()), as on a runner a link to a folder such as /root or /var/root cannot be entered."""
    path = os.path.join(t, "a-folder-this-runner-cannot-enter")
    os.makedirs(path, exist_ok=True)
    return path


@contextlib.contextmanager
def shut(t):
    """The locked folder at mode 000 while the legs inside run, giving whether this user is kept out of it: a user who
    enters any folder, as root does, is not, and on that machine this plant cannot be made."""
    path = locked_folder(t)
    os.chmod(path, 0)
    try:
        yield not os.access(path, os.X_OK)
    finally:
        os.chmod(path, 0o700)


def unenterable(t, repo):
    """Check 7's finding (the root's ruling 8 (ii)): bagit.txt and data/ made a link to a folder this runner cannot
    enter, the folder the crash adapter's check runs in, at cf42ad6, checked in one leg with cf42ad6 itself after it.
    Entering that folder raises an error what the commit holds causes, not a tool the runner cannot start: that commit
    fails the check that the commit holds no link and no submodule, naming the link, and the stopped check, naming the
    error, and the leg goes on, cf42ad6 keeping its result (fix round 7's code ended the leg there, writing nothing)."""
    locked = locked_folder(t)

    def fn(w):
        open(os.path.join(w, "bagit.txt"), "w").write("BagIt-Version: 1.0\n")
        os.symlink(locked, os.path.join(w, "data"))
    sha = planted_commit(repo, ANCHOR_MAIN, "planted: bagit.txt, and data/ a link to a folder this runner cannot enter",
                         fn)
    git(repo, "checkout", "-q", "main")
    with shut(t) as kept_out:
        rc, res = leg(repo, [{"commit": sha, "refs": []}, {"commit": ANCHOR_MAIN, "refs": ["refs/heads/main"]}],
                      os.path.join(t, "leg-unenterable.json"), extra_env={"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"})
    c = next((x for x in res["commits"] if x["commit"] == sha), None)
    m = next((x for x in res["commits"] if x["commit"] == ANCHOR_MAIN), None)
    checks = {k["name"]: k for k in (c or {}).get("checks", [])}
    got = sorted(n for n, k in checks.items() if k["result"] == "fail")
    prop("anchor stage, planted: bagit.txt, and data/ a link to a folder this runner cannot enter, the folder the "
         "crash adapter's check runs in (check 7's finding): fails the check that the commit holds no link and no "
         "submodule, naming the link, and the stopped check, naming the error entering it, at the release stage, 9 "
         "checks, and the leg goes on to cf42ad6, which passes all 8 checks, exit 1",
         kept_out and rc == 1 and c is not None and c["stage"] == "release" and got == sorted([LINKS, STOPPED])
         and len(checks) == 9 and checks[LINKS]["detail"] == "data is a link (1 in all)"
         and "Permission denied" in checks[STOPPED]["detail"] and m is not None and m["stage"] == "anchor"
         and m["result"] == "pass" and len(m["checks"]) == 8,
         {"kept out of the folder": kept_out, "exit": rc, "plant": c and {"stage": c["stage"], "failing": got,
          "checks": len(checks), "details": {n: checks[n]["detail"][:240] for n in got}},
          "cf42ad6": m and (m["stage"], m["result"], len(m["checks"]))})


def own_tools(t, repo):
    """The root's ruling 9 (ii): a leg runs no program from an empty or relative PATH entry. cf42ad6 with an executable
    ssh-keygen of its own, which says every signature is good, at its root or in tools/, and anchor #1's manifest
    changed, each checked in a leg of its own with '.', an empty entry or tools ahead of the runner's PATH: the
    signature check starts the runner's ssh-keygen, which refuses the changed manifest, so the commit fails that check
    alone. And with '.' first on a PATH that holds what the leg starts but ssh-keygen, the commit's own the only one
    there, the leg ends with no result written, exit 2, naming the runner's fault: infrastructure, never a pass."""
    man = os.path.join("anchor", "predicates-1.manifest")

    def own(rel):
        def fn(w):
            p = os.path.join(w, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(OWN_KEYGEN)
            os.chmod(p, 0o755)
            open(os.path.join(w, man), "a").write("# a line the signature does not cover\n")
        return fn
    root = planted_commit(repo, ANCHOR_MAIN, "planted: an executable ssh-keygen of its own at the root, anchor #1's "
                                             "manifest changed", own("ssh-keygen"))
    tools = planted_commit(repo, ANCHOR_MAIN, "planted: an executable ssh-keygen of its own in tools/, anchor #1's "
                                              "manifest changed", own("tools/ssh-keygen"))
    git(repo, "checkout", "-q", "main")  # each leg's clone of the scratch repository is checked out at cf42ad6
    runner_path = os.environ.get("PATH", os.defpath)
    for name, sha, first, where in (("'.'", root, ".", "at its root"), ("an empty entry", root, "", "at its root"),
                                    ("tools, a folder of the commit,", tools, "tools", "in tools/")):
        out = os.path.join(t, f"leg-own-ssh-keygen-{sha[:12]}-{first or 'empty'}.json")
        rc, res = leg(repo, [{"commit": sha, "refs": []}], out, extra_env={"PATH": first + os.pathsep + runner_path})
        c = next((x for x in res["commits"] if x["commit"] == sha), None)
        checks = {k["name"]: k for k in (c or {}).get("checks", [])}
        got = sorted(n for n, k in checks.items() if k["result"] == "fail")
        prop(f"anchor stage, planted: an executable ssh-keygen of its own {where}, which says every signature is good, "
             f"and anchor #1's manifest changed, checked with {name} first on PATH: fails the signature check alone, "
             f"the runner's ssh-keygen refusing the manifest, 8 checks, exit 1", rc == 1 and c is not None
             and got == [SIG] and len(checks) == 8
             and "an ssh-keygen the commit holds" not in checks[SIG]["detail"],
             {"exit": rc, "failing": got, "checks": len(checks), "signature": checks.get(SIG, {}).get("detail", "")[-240:]})
    tools_bin = os.path.join(t, "no-ssh-keygen-bin")  # git, ssh, bash and sh, as runner_fault() made it
    out = os.path.join(t, "leg-own-ssh-keygen-dot-no-other.json")
    env = {k: v for k, v in os.environ.items() if k not in F.TOKEN_VARIABLES}
    env.update({"TODO": json.dumps([{"commit": root, "refs": []}]), "PATH": "." + os.pathsep + tools_bin,
                "PYTHONDONTWRITEBYTECODE": "1"})
    r = subprocess.run([sys.executable, "-B", os.path.join(CI, "run_checks.py"), "--commits-env", "TODO", "--leg",
                        "a runner whose only ssh-keygen is behind '.' (dry run)", "--python", sys.executable, "--source",
                        repo, "--out", out], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    said = (r.stdout + r.stderr).strip()
    sys.stdout.write("".join(f"      {ln}\n" for ln in said.splitlines()[-4:]))
    rec = P.pack_records([{"commit": root, "refs": []}], DATE, [P.read_leg(out)], 1, "Wed, 14 Oct 2026 12:40:00 GMT",
                         {"id": "dry-run", "attempt": "1", "event": "schedule", "url": ""})[0][1]
    prop("runner fault, planted: '.' first on a PATH holding git, ssh, bash and sh but no ssh-keygen, the commit at "
         "its root above the only one: the leg ends with no result written, exit 2, naming the runner's fault, and the "
         "publish step records that leg as infrastructure, never a pass", r.returncode == 2 and not os.path.exists(out)
         and "the runner cannot start ssh-keygen" in said and "the runner's fault" in said
         and rec["result"] == "infrastructure",
         {"exit": r.returncode, "written": os.path.exists(out), "said": said[-600:], "record": rec["result"]})


def runner_git(t, name, attributes=None, template=None):
    """A git of a runner's own, made here: a copy of a git that finds its own files from where it is run, as Apple's
    does (`git --exec-path` names <prefix>/libexec/git-core), with that git's subcommands linked; its system attributes
    files, <prefix>/etc/gitattributes and <prefix>/share/git-core/gitattributes, holding `attributes`; and its
    templates, <prefix>/share/git-core/templates, that git's own, or with `template` ({path: (text, mode)}) those files
    alone. Tried on the git PATH names, then /usr/bin/git, and kept only when a repository the copy makes, under no
    configuration of the runner's, reads those attributes and holds those files. (The folder the copy is in, None), or
    (None, why) when no git here does, on which the plant cannot be made."""
    tried = []
    for i, cand in enumerate(c for c in (shutil.which("git"), "/usr/bin/git") if c):
        r = subprocess.run([cand, "--exec-path"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        core = r.stdout.strip()
        prefix = os.path.dirname(os.path.dirname(core))
        real = os.path.join(prefix, "bin", "git")
        if r.returncode != 0 or not os.path.isfile(real):
            tried.append(f"{cand}: no git beside {core!r}")
            continue
        root = os.path.join(t, f"{name}-{i}")
        share = os.path.join(root, "share", "git-core")
        for d in (os.path.join(root, "bin"), os.path.join(root, "libexec"), os.path.join(root, "etc"), share):
            os.makedirs(d)
        shutil.copy2(real, os.path.join(root, "bin", "git"))
        os.symlink(core, os.path.join(root, "libexec", "git-core"))
        if template is None:
            if os.path.isdir(os.path.join(prefix, "share", "git-core", "templates")):
                os.symlink(os.path.join(prefix, "share", "git-core", "templates"), os.path.join(share, "templates"))
        else:
            for rel, (text, mode) in template.items():
                p = os.path.join(share, "templates", *rel.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(text)
                os.chmod(p, mode)
        if attributes is not None:
            for folder in (os.path.join(root, "etc"), share):
                open(os.path.join(folder, "gitattributes"), "w").write(attributes)
        env = {"PATH": os.environ.get("PATH", os.defpath), "HOME": root, "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull}
        git_copy, probe = os.path.join(root, "bin", "git"), os.path.join(root, "probe")
        subprocess.run([git_copy, "init", "-q", probe], env=env, capture_output=True, stdin=subprocess.DEVNULL)
        said = subprocess.run([git_copy, "-C", probe, "check-attr", "text", "--", "f"], env=env, capture_output=True,
                              text=True, stdin=subprocess.DEVNULL).stdout.strip()
        held = [rel for rel in template or {} if os.path.isfile(os.path.join(probe, ".git", *rel.split("/")))]
        if (attributes is None or said == "f: text: set") and len(held) == len(template or {}):
            return os.path.join(root, "bin"), None
        tried.append(f"a repository a copy of {real} makes reads {said!r} and holds {held} of {sorted(template or {})}")
    return None, "no git here reads the files beside it that it is given: " + ("; ".join(tried) or "no git found")


def git_config(t, repo, pp):
    """The root's ruling 9 (iii): the runner's git configuration cannot change a leg's result. cf42ad6, checked in a
    leg whose HOME holds a global configuration (.gitconfig) naming a gpg.ssh.program that does not exist, and in one
    whose global configuration sends the scratch repository's address to another clone of the pack repository, whose
    anchor tag a key made here signed: it passes all 8 checks in each, exit 0, as it does with no such configuration.
    And so it does under each attributes file of the runner's, which git reads whatever configuration it reads (the
    round 9 check's finding 1), holding `* text eol=crlf`, which turns every file's line endings to CRLF in a checkout:
    the global one in HOME (.config/git/attributes) and in the XDG folder, the system one of a git first on PATH that
    reads it, and an info/attributes among that git's templates, which it copies into each repository it makes; and
    under a post-checkout hook among those templates, which changes anchor #1's manifest (runner_git())."""
    other = os.path.join(t, "other-pack-repository")
    git(t, "clone", "-q", pp, other)
    tagger = planted_key(t, "planted-key-other-repository-tag")
    git(other, "-c", "gpg.format=ssh", "-c", f"user.signingkey={tagger[0]}", "tag", "-s", "-f", "-m",
        "planted: anchor #1's tag, signed by a key the pin lacks", "anchor/predicates-1",
        git(other, "rev-parse", "refs/tags/anchor/predicates-1^{commit}"))
    commits = [{"commit": ANCHOR_MAIN, "refs": ["refs/heads/main"]}]
    for key, name, text in (
            ("program", "naming a gpg.ssh.program that does not exist", '[gpg "ssh"]\n\tprogram = /nonexistent/ssh-keygen\n'),
            ("url", "sending the pack repository's address to another repository, whose anchor tag a key the pin lacks "
                    "signed", f'[url "{other}"]\n\tinsteadOf = {repo}\n')):
        home = os.path.join(t, f"runner-home-{key}")
        os.makedirs(home, exist_ok=True)
        open(os.path.join(home, ".gitconfig"), "w").write(text)
        rc, res = leg(repo, commits, os.path.join(t, f"leg-git-config-{key}.json"), extra_env={"HOME": home})
        c = next((x for x in res["commits"] if x["commit"] == ANCHOR_MAIN), None)
        bad = [(k["name"], k["result"], k["detail"][-200:]) for k in (c or {}).get("checks", []) if k["result"] != "pass"]
        prop(f"anchor stage, planted: a global git configuration of the runner's {name}: {ANCHOR_MAIN[:7]} passes all 8 "
             f"checks, as with none, exit 0", rc == 0 and c is not None and c["result"] == "pass" and not bad
             and len(c["checks"]) == 8, {"exit": rc, "not passing": bad, "checks": len((c or {}).get("checks", []))})
    crlf = "* text eol=crlf\n"
    home, xdg, empty = (os.path.join(t, f"runner-{n}-attributes") for n in ("home", "xdg", "empty"))
    for folder in (os.path.join(home, ".config", "git"), os.path.join(xdg, "git"), empty):
        os.makedirs(folder, exist_ok=True)
    open(os.path.join(home, ".config", "git", "attributes"), "w").write(crlf)
    open(os.path.join(xdg, "git", "attributes"), "w").write(crlf)
    hook = ("#!/bin/sh\nif [ -f anchor/predicates-1.manifest ]; then\n"
            "  echo '# a line a hook of the runner wrote' >> anchor/predicates-1.manifest\nfi\n")

    def first_on_path(name, **files):
        """PATH with a git of the runner's own first (runner_git()), or why it cannot be made here."""
        got, why = runner_git(t, f"runner-git-{name}", **files)
        return {"PATH": got + os.pathsep + os.environ.get("PATH", os.defpath)} if got else why
    for key, name, extra in (
            ("home", "a global git attributes file of the runner's, HOME's .config/git/attributes, holding * text "
                     "eol=crlf, which turns every file's line endings to CRLF in a checkout",
             {"HOME": home, "XDG_CONFIG_HOME": ""}),
            ("xdg", "the same in the XDG folder, $XDG_CONFIG_HOME/git/attributes, with no attributes file in HOME",
             {"HOME": empty, "XDG_CONFIG_HOME": xdg}),
            ("system", "the same as the system attributes file of a git first on PATH that reads it",
             first_on_path("system-attributes", attributes=crlf)),
            ("template", "the same as an info/attributes among the templates of a git first on PATH, which it copies "
                         "into each repository it makes",
             first_on_path("template-attributes", template={"info/attributes": (crlf, 0o644)})),
            ("hook", "a post-checkout hook among the templates of a git of the runner's first on PATH, which changes "
                     "anchor #1's manifest", first_on_path("template-hook", template={"hooks/post-checkout": (hook, 0o755)}))):
        said = f"anchor stage, planted: {name}: {ANCHOR_MAIN[:7]} passes all 8 checks, as with none, exit 0"
        if isinstance(extra, str):  # a plant this machine cannot make fails, naming why
            prop(said, False, extra)
            continue
        rc, res = leg(repo, commits, os.path.join(t, f"leg-git-attributes-{key}.json"), extra_env=extra)
        c = next((x for x in res["commits"] if x["commit"] == ANCHOR_MAIN), None)
        bad = [(k["name"], k["result"], k["detail"][-200:]) for k in (c or {}).get("checks", []) if k["result"] != "pass"]
        prop(said, rc == 0 and c is not None and c["result"] == "pass" and not bad and len(c["checks"]) == 8,
             {"exit": rc, "not passing": bad, "checks": len((c or {}).get("checks", []))})


def make_bag(t, pp, build=None, bag=None):
    repo = os.path.join(t, "release-repo")
    git(t, "clone", "-q", pp, repo)
    git(repo, "checkout", "-q", "-B", "main", ANCHOR_MAIN)
    if build:
        r = subprocess.run([sys.executable, "-B", os.path.join(build, "tools", "bag.py"), "--out", repo],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if r.returncode != 0:
            raise RuntimeError(f"tools/bag.py: {(r.stdout + r.stderr).strip()[-600:]}")
        print("      " + r.stdout.strip())
    else:  # the bag is a whole repository root: it replaces the checkout's files, the checkout's .git aside
        for name in os.listdir(repo):
            if name != ".git":
                p = os.path.join(repo, name)
                shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)
        shutil.copytree(bag, repo, ignore=shutil.ignore_patterns(".git"), symlinks=True, dirs_exist_ok=True)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "the bag, as a release would publish it")
    return repo, git(repo, "rev-parse", "HEAD")


def release_stage(t, repo, sha):
    env = {"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"}
    t0 = time.time()
    rc, res = leg(repo, [{"commit": sha, "refs": ["refs/heads/main"]}], os.path.join(t, "leg-release.json"), extra_env=env)
    checks, c = by_name(res, sha)
    fails = sorted(n for n, k in checks.items() if k["result"] == "fail")
    witness = checks.get("data/bin/fixpack witness", {})
    prop(f"release stage: {sha[:7]} is checked at the release stage, {len(checks)} checks in {time.time() - t0:.0f} s",
         c["stage"] == "release", c["stage"])
    if os.path.isdir(os.path.join(repo, "data", "witness")):
        prop("release stage: every check passes or is skipped with why", not fails,
             [(n, checks[n]["detail"][-200:]) for n in fails])
    else:
        prop("release stage: every check passes or is skipped with why, but fixpack witness, which fails as "
             "VERIFYING.md says it does on a pack with no witness record", fails == ["data/bin/fixpack witness"]
             and "WITNESS FAILED" in witness.get("detail", ""), [(n, checks[n]["detail"][-200:]) for n in fails])
    for name in (MANIFESTS, KEYSET, "anchor #1: its signature, with ssh-keygen -Y verify",
                 "manifest-sha256.txt with sha256sum -c", "tagmanifest-sha256.txt with sha256sum -c", "bagit 1.9.0 --validate",
                 "data/bin/fixpack verify", "bash data/conformance/run.sh", "the crash adapter is an adapter error, exit 3",
                 "the grade's --json result against schema/result.schema.json",
                 "VERIFYING.md: every fenced block classified in ci/verifying-blocks.json"):
        k = next((v for n, v in checks.items() if n == name or n.replace("shasum -a 256 -c", "sha256sum -c") == name), None)
        prop(f"release stage: {name}: pass", k is not None and k["result"] == "pass", k)
    skipped = sorted(n for n, k in checks.items() if k["result"] == "skipped")
    ran = sorted(n for n, k in checks.items() if n.startswith("VERIFYING.md block") and k["result"] == "pass")
    prop(f"release stage: {len(ran)} VERIFYING.md blocks run and pass here, {len(skipped)} skipped, each with why",
         len(ran) >= 6 and all(checks[n]["detail"] for n in skipped), {"ran": ran, "skipped": {n: checks[n]["detail"][:90] for n in skipped}})
    return os.path.join(t, "leg-release.json")


def release_plants(t, repo, base):
    def payload(w):
        p = os.path.join(w, "data", "LIMITS.md")
        b = bytearray(open(p, "rb").read())
        b[100] ^= 1
        open(p, "wb").write(bytes(b))

    def tag_file(w):
        os.remove(os.path.join(w, "KEYS.md"))

    def unclassified(w):
        open(os.path.join(w, "VERIFYING.md"), "a").write("\n```\necho a command no classification names\n```\n")
        tm = os.path.join(w, "tagmanifest-sha256.txt")
        lines = []
        for ln in open(tm).read().splitlines():
            if ln.endswith("  VERIFYING.md"):
                ln = hashlib.sha256(open(os.path.join(w, "VERIFYING.md"), "rb").read()).hexdigest() + "  VERIFYING.md"
            lines.append(ln)
        open(tm, "w").write("\n".join(lines) + "\n")
    plants = (("a payload byte", payload, "manifest,bagit,verify",
               ["manifest-sha256.txt with sha256sum -c", "bagit 1.9.0 --validate", "data/bin/fixpack verify"]),
              ("a tag file removed (KEYS.md)", tag_file, "tagmanifest,bagit,verify",
               ["tagmanifest-sha256.txt with sha256sum -c", "bagit 1.9.0 --validate", "data/bin/fixpack verify"]),
              ("a VERIFYING.md block no classification names, the tag manifest resealed", unclassified,
               "tagmanifest,verifying", ["VERIFYING.md: every fenced block classified in ci/verifying-blocks.json"]))
    for name, fn, checks, want in plants:
        sha = planted_commit(repo, base, f"planted: {name}", fn)
        rc, res = leg(repo, [{"commit": sha, "refs": []}], os.path.join(t, f"leg-plant-{sha[:7]}.json"), checks=checks,
                      extra_env={"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"})
        got = [n.replace("shasum -a 256 -c", "sha256sum -c") for n in failing(res, sha)]
        detail = by_name(res, sha)[0]
        prop(f"release stage, planted: {name}: fails {', '.join(want)}, and nothing else", sorted(got) == sorted(want),
             {n: detail[n]["detail"][-160:] for n in detail})
    # The root's ruling 8 (i) at the release stage: a payload file made a link to its copy in the leg's own clone of
    # the pack repository, tmp/pack, checked out at main, the bag, through which sha256sum -c reads the same bytes.
    def payload_link(w):
        p = os.path.join(w, "data", "LIMITS.md")
        os.remove(p)
        os.symlink("../../../pack/data/LIMITS.md", p)
    sha = planted_commit(repo, base, "planted: a payload file made a link to its copy in the leg's own clone",
                         payload_link)
    git(repo, "checkout", "-q", "main")
    rc, res = leg(repo, [{"commit": sha, "refs": []}], os.path.join(t, f"leg-plant-{sha[:7]}.json"),
                  checks="links,manifest,bagit,verify", extra_env={"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"})
    want = [LINKS, "bagit 1.9.0 --validate", "data/bin/fixpack verify"]
    got = [n.replace("shasum -a 256 -c", "sha256sum -c") for n in failing(res, sha)] if res["commits"] else None
    detail = by_name(res, sha)[0] if res["commits"] else {}
    prop(f"release stage, planted: a payload file made a link to its copy in the leg's own clone, which sha256sum -c "
         f"reads through: fails {', '.join(want)}, the links' check naming it, and nothing else",
         got is not None and sorted(got) == sorted(want)
         and detail.get(LINKS, {}).get("detail") == "data/LIMITS.md is a link (1 in all)",
         {n: detail[n]["detail"][-160:] for n in detail} if detail else f"no result, exit {rc}")
    # Check 7's finding at the release stage (its RDROOT): data/ itself made a link to a folder this runner cannot
    # enter, checked in one leg with the release commit after it (the links' check and the crash adapter's, which runs
    # in data/), and alone with the links' check and the result schema's, which runs there too and catches the error.
    locked = locked_folder(t)

    def data_locked(w):
        shutil.rmtree(os.path.join(w, "data"))
        os.symlink(locked, os.path.join(w, "data"))
    sha = planted_commit(repo, base, "planted: data/ a link to a folder this runner cannot enter", data_locked)
    git(repo, "checkout", "-q", "main")
    crash = "the crash adapter is an adapter error, exit 3"
    schema = "the grade's --json result against schema/result.schema.json"
    with shut(t) as kept_out:
        rc, res = leg(repo, [{"commit": sha, "refs": []}, {"commit": base, "refs": ["refs/heads/main"]}],
                      os.path.join(t, f"leg-plant-{sha[:7]}-crash.json"), checks="links,crash",
                      extra_env={"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"})
        rc2, res2 = leg(repo, [{"commit": sha, "refs": []}], os.path.join(t, f"leg-plant-{sha[:7]}-schema.json"),
                        checks="links,schema", extra_env={"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1"})
    view = {}
    for name, r in (("crash", res), ("schema", res2)):
        for c in r["commits"]:
            view[(name, c["commit"])] = {k["name"]: k for k in c["checks"]}
    p, after, alone = view.get(("crash", sha), {}), view.get(("crash", base), {}), view.get(("schema", sha), {})
    prop("release stage, planted: data/ a link to a folder this runner cannot enter (check 7's RDROOT): fails the "
         "links' check, naming the link, and the stopped check, naming the error entering data/, where the crash "
         "adapter's check runs, and the leg goes on to the release commit, which passes both checks, exit 1",
         kept_out and rc == 1 and sorted(n for n, k in p.items() if k["result"] == "fail") == sorted([LINKS, STOPPED])
         and p[LINKS]["detail"] == "data is a link (1 in all)" and "Permission denied" in p[STOPPED]["detail"]
         and sorted(after) == sorted([LINKS, crash]) and all(k["result"] == "pass" for k in after.values()),
         {"kept out of the folder": kept_out, "exit": rc, "plant": {n: (k["result"], k["detail"][-200:]) for n, k in
          p.items()}, "the release commit": {n: k["result"] for n, k in after.items()}})
    prop("release stage, planted: the same, with the result schema's check, which runs in data/ too: it fails, naming "
         "the error entering data/, and the links' check fails, naming the link; nothing stops, exit 1",
         kept_out and rc2 == 1
         and sorted(n for n, k in alone.items() if k["result"] == "fail") == sorted([LINKS, schema])
         and STOPPED not in alone and "Permission denied" in alone[schema]["detail"],
         {"kept out of the folder": kept_out, "exit": rc2, "plant": {n: (k["result"], k["detail"][-200:]) for n, k in
          alone.items()}})
    git(repo, "checkout", "-q", "main")


# ------------------------------------------------------------------ the canary's answers
def answers_for(clone, snap, dirid, zipped, tarred):
    """Answers in the shapes GitHub, doi.org, Zenodo and Software Heritage give, made from what the release holds, so
    the canary passes; and the ls-remote answer for each subject repository."""
    exp = C.expectations(clone)
    data = os.path.join(clone, "data")
    sys.path.insert(0, os.path.join(data, "bin"))
    cs = C.load_module(os.path.join(data, "bin", "capture_reader.py"), "dry_reader").open_set(os.path.join(data, "captures", "data"))
    sys.path.pop(0)
    pack = json.load(open(os.path.join(data, "pack.json")))
    h = {"date": DATE, "x-ratelimit-remaining": "50", "content-type": "application/json"}
    ans, ls = {}, {}
    for r in exp["repos"]:
        ls[r["name"]] = [(sha, ref) for ref, sha in sorted(r["heads"].items())]
        ans[f"https://api.github.com/repositories/{r['id']}"] = (200, dict(h), {"id": r["id"], "full_name": r["name"], "archived": True})
        short = r["name"].split("/", 1)[1]
        rows = cs.load("activity.json" if r["name"] == pack["fixture_repo"] else f"{short}-activity.json")
        pages = [rows[i:i + 100] for i in range(0, len(rows), 100)] or [[]]
        for i, page in enumerate(pages):
            url = f"https://api.github.com/repos/{r['name']}/activity?per_page=100" + (f"&page={i + 1}" if i else "")
            hh = dict(h)
            if i + 1 < len(pages):
                hh["link"] = f'<https://api.github.com/repos/{r["name"]}/activity?per_page=100&page={i + 2}>; rel="next"'
            ans[url] = (200, hh, page)
    for pid, login in exp["principals"]:
        ans[f"https://api.github.com/user/{pid}"] = (200, dict(h), {"id": pid, "login": login})
    for doi in exp["dois"]:
        ans[f"https://doi.org/{doi}"] = (302, {"date": DATE, "location": f"https://zenodo.org/doi/{doi}"}, b"")
    for s in exp["swhids"]:
        ans[f"https://archive.softwareheritage.org/api/1/resolve/{s}/"] = (200, dict(h), {"object_id": s})
    for n in exp["rekor"]:
        ans[f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={n}"] = (200, dict(h), {"logIndex": n})
    base = "https://archive.softwareheritage.org/api/1"
    rel_id, rev_id = "1" * 40, "2" * 40
    ans[f"{base}/snapshot/{snap}/"] = (200, dict(h), {"branches": {"refs/tags/v1.0.0": {"target": rel_id, "target_type": "release"}}})
    ans[f"{base}/release/{rel_id}/"] = (200, dict(h), {"target": rev_id, "target_type": "revision"})
    ans[f"{base}/revision/{rev_id}/"] = (200, dict(h), {"directory": dirid})
    ans[f"{base}/vault/flat/swh:1:dir:{dirid}/"] = (200, dict(h), {"status": "done", "fetch_url": f"{base}/vault/flat/swh:1:dir:{dirid}/raw/"})
    ans[f"{base}/vault/flat/swh:1:dir:{dirid}/raw/"] = (200, {"date": DATE}, tarred)
    rec = max(int(d.rsplit(".", 1)[1]) for d in exp["dois"])
    ans[f"https://zenodo.org/api/records/{rec}"] = (200, dict(h), {"files": [{"key": "falden-fixture-pack-v1.0.0.zip",
                                                                            "links": {"self": f"https://zenodo.org/api/records/{rec}/files/x.zip/content"}}]})
    ans[f"https://zenodo.org/api/records/{rec}/files/x.zip/content"] = (200, {"date": DATE}, zipped)
    return ans, ls


def archive(bag, kind):
    """The bag at `bag` as a zip with a top folder, as GitHub's release archive is, or as a vault's tar.gz."""
    buf = io.BytesIO()
    if kind == "zip":
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for d, dirs, fs in os.walk(bag):
                dirs[:] = [x for x in dirs if x != ".git"]
                for f in fs:
                    p = os.path.join(d, f)
                    z.write(p, os.path.join("falden-fixtures-falden-fixture-pack-0123456", os.path.relpath(p, bag)))
    else:
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            tf.add(bag, arcname="swh-dir", filter=lambda ti: None if ".git" in ti.name.split("/") else ti)
    return buf.getvalue()


def canary(t, repo, base):
    snap, dirid = "3" * 40, "4" * 40

    def landing(w):
        open(os.path.join(w, "README.md"), "a").write(f"\nDOI: 10.5281/zenodo.1234567 (concept), 10.5281/zenodo.1234568 "
                                                      f"(this version). Software Heritage: swh:1:snp:{snap}\n")
    sha = planted_commit(repo, base, "the landing README given its DOI and SWHID, as a release adds them", landing)
    git(repo, "tag", "-f", "-a", "-m", "v1.0.0 (dry run)", "v1.0.0", sha)
    git(repo, "checkout", "-q", "main")
    clone = os.path.join(t, "canary-expect")
    git(t, "clone", "-q", "--branch", "v1.0.0", repo, clone)
    zipped, tarred = archive(clone, "zip"), archive(clone, "tar")
    answers, ls = answers_for(clone, snap, dirid, zipped, tarred)
    pack_refs = [(git(repo, "rev-parse", "v1.0.0"), "refs/tags/v1.0.0"), (sha, "refs/tags/v1.0.0^{}")]

    no_records = os.path.join(t, "canary-no-records.json")
    json.dump({"format": P.RECORD_FORMAT, "records": []}, open(no_records, "w"))

    def run(edit=None, edit_ls=None, env_extra=None):
        a = copy.deepcopy(answers)
        lsm = copy.deepcopy(ls)
        if edit:
            edit(a)
        if edit_ls:
            edit_ls(lsm)
        sent = []

        def transport(method, url, headers, follow=True):
            sent.append(url)
            if "Authorization" in headers:
                raise AssertionError("a read carried a credential")
            if url not in a:
                raise OSError(f"no answer made for {url}")
            status, hh, body = a[url]
            return status, dict(hh), body if isinstance(body, bytes) else json.dumps(body).encode()

        def lsr(url):
            name = url[len("https://github.com/"):]
            return pack_refs if name == C.PACK else lsm[name]
        clock = [1_800_000_000.0]
        fg = F.Forge(transport=transport, clock=lambda: clock[0], sleep=lambda s: clock.__setitem__(0, clock[0] + s),
                     say=lambda m: None)
        with tempfile.TemporaryDirectory(prefix="canary-run-", dir=t) as tmp:
            old = dict(os.environ)
            os.environ.update({"BAGIT_CMD": BAGIT, "STATUS_OFFLINE": "1", **(env_extra or {})})
            try:
                F.refuse_tokens()
                res = C.canary_result(fg, lsr, repo, tmp, index_path=no_records, say=lambda m: None)
            finally:
                os.environ.clear()
                os.environ.update(old)
        return res, sent

    t0 = time.time()
    res, sent = run()
    bad = [k for k in res["checks"] if k["result"] != "pass"]
    prop(f"canary: on v1.0.0, against answers made for it, every one of its {len(res['checks'])} checks passes, the "
         f"three copies' fixity among them and both archive copies held to the clone's tag manifest ({len(sent)} "
         f"reads, none to the network, {time.time() - t0:.0f} s)",
         res["publish"] and res["result"] == "pass" and not bad and
         sum(k["name"].endswith("fixpack verify") for k in res["checks"]) == 3 and
         sum(k["name"].endswith("its tagmanifest-sha256.txt is the release clone's") for k in res["checks"]) == 2,
         bad or res)
    json.dump(res, open(os.path.join(t, "canary.json"), "w"), indent=1)
    first = C.expectations(clone)["repos"][0]
    pid, login = C.expectations(clone)["principals"][0]
    rec = max(int(d.rsplit(".", 1)[1]) for d in C.expectations(clone)["dois"])
    zurl = f"https://zenodo.org/api/records/{rec}/files/x.zip/content"

    def moved(lsm):
        sha0, ref0 = lsm[first["name"]][0]
        lsm[first["name"]][0] = ("f" * 40, ref0)

    def changed_zip(a):
        clone2 = os.path.join(t, "zen-plant")
        if os.path.exists(clone2):
            shutil.rmtree(clone2)
        shutil.copytree(clone, clone2, ignore=shutil.ignore_patterns(".git"))
        p = os.path.join(clone2, "data", "LIMITS.md")
        x = bytearray(open(p, "rb").read())
        x[200] ^= 1
        open(p, "wb").write(bytes(x))
        a[zurl] = (200, {"date": DATE}, archive(clone2, "zip"))
    plants = (
        ("a moved branch head", None, moved, f"{first['name']}: its branch heads are the sealed ones"),
        ("a repository not archived", lambda a: a[f"https://api.github.com/repositories/{first['id']}"][2].__setitem__("archived", False),
         None, f"{first['name']}: GitHub's /repositories/{first['id']} names it, archived"),
        ("a renamed principal", lambda a: a[f"https://api.github.com/user/{pid}"][2].__setitem__("login", login + "-renamed"),
         None, f"principal {pid}: GitHub still names it {login}"),
        ("a Deprecation header on the keyed version",
         lambda a: a[f"https://api.github.com/repositories/{first['id']}"][1].__setitem__("deprecation", "@1798761600"),
         None, f"{first['name']}: no deprecation marked on the keyed API version"),
        ("an /activity count that changed",
         lambda a: a[f"https://api.github.com/repos/{first['name']}/activity?per_page=100"][2].pop(), None,
         f"{first['name']}: its /activity count and newest id are the sealed ones"),
        ("a Zenodo archive with a changed byte", changed_zip, None, f"the Zenodo record {rec}'s archive: fixpack verify"),
    )
    for name, edit, edit_ls, want in plants:
        res, _sent = run(edit, edit_ls)
        failed = [k["name"] for k in res["checks"] if k["result"] == "fail"]
        prop(f"canary, planted: {name}: fails {want!r}", any(f.startswith(want) for f in failed) and res["result"] == "fail",
             failed)
    # A copy resealed after a change is a valid bag of other bytes: only its tag manifest, held to the clone's, shows it.
    def resealed(name):
        d = os.path.join(t, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(clone, d, ignore=shutil.ignore_patterns(".git"))
        info = os.path.join(d, "bag-info.txt")
        open(info, "a").write("External-Description: a copy changed after the release and resealed (dry run)\n")
        tm = os.path.join(d, "tagmanifest-sha256.txt")
        lines = [hashlib.sha256(open(info, "rb").read()).hexdigest() + "  bag-info.txt"
                 if ln.endswith("  bag-info.txt") else ln for ln in open(tm).read().splitlines()]
        open(tm, "w").write("\n".join(lines) + "\n")
        return d
    raw = f"https://archive.softwareheritage.org/api/1/vault/flat/swh:1:dir:{dirid}/raw/"
    held = hashlib.sha256(open(os.path.join(clone, "tagmanifest-sha256.txt"), "rb").read()).hexdigest()
    reseals = (
        ("a Zenodo archive", lambda a: a.__setitem__(zurl, (200, {"date": DATE}, archive(resealed("zen-reseal"), "zip"))),
         f"the Zenodo record {rec}'s archive: its tagmanifest-sha256.txt is the release clone's"),
        ("a vault tarball", lambda a: a.__setitem__(raw, (200, {"date": DATE}, archive(resealed("swh-reseal"), "tar"))),
         "the Software Heritage vault tarball: its tagmanifest-sha256.txt is the release clone's"),
    )
    for name, edit, want in reseals:
        res, _sent = run(edit)
        bad = [k for k in res["checks"] if k["result"] != "pass"]
        prop(f"canary, planted: {name} resealed after a change, a valid bag of other bytes: fails {want!r} and nothing "
             f"else, naming the release clone's digest", [k["name"] for k in bad] == [want] and held in bad[0]["detail"]
             and res["result"] == "fail", [(k["name"], k["result"], k["detail"][-240:]) for k in bad])
    # Answers in a shape the canary does not read: the run stops, and its record is still published (fix round 2).
    vault = f"https://archive.softwareheritage.org/api/1/vault/flat/swh:1:dir:{dirid}/"
    stops = (
        ("a Zenodo record whose archive has no links",
         lambda a: a[f"https://zenodo.org/api/records/{rec}"][2]["files"][0].pop("links"), "KeyError: 'links'"),
        ("a vault that says done with no fetch_url", lambda a: a[vault][2].pop("fetch_url"), "KeyError: 'fetch_url'"),
    )
    for name, edit, want in stops:
        res, _sent = run(edit)
        last = res["checks"][-1] if res["checks"] else {}
        kept = [k["name"] for k in res["checks"][:-1] if k["result"] == "pass"]
        prop(f"canary, planted: {name}: the run stops and is still published, naming v1.0.0, a fail of the canary's "
             f"run naming {want}, with the {len(kept)} checks passed before it",
             res["publish"] is True and (res.get("release") or {}).get("tag") == "v1.0.0" and res["result"] == "fail"
             and last.get("name") == "the canary's run" and want in last.get("detail", "")
             and "the clone of v1.0.0: fixpack verify" in kept, (last, kept))
    reached = []

    def door(*_a, **_k):
        reached.append(_a)
        raise AssertionError("the canary read past a token in its environment")
    saved = (C.F.Forge, C.D.ls_remote)
    C.F.Forge, C.D.ls_remote = door, door
    old = dict(os.environ)
    os.environ["GITHUB_TOKEN"] = "planted"
    out = os.path.join(t, "canary-token.json")
    try:
        rc = C.main(["--out", out])
    except AssertionError:
        rc = None
    finally:
        C.F.Forge, C.D.ls_remote = saved
        os.environ.clear()
        os.environ.update(old)
    prop("canary, planted: a token in the environment stops ci/canary.py before any read, exit 2, nothing written",
         rc == 2 and not reached and not os.path.exists(out), (rc, reached))
    return os.path.join(t, "canary.json")


def records(t, legs, canary_json):
    root = os.path.join(t, "status-copy")
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    for p in sorted(os.listdir(os.path.join(root, "records"))):
        if p != "index.json":
            shutil.rmtree(os.path.join(root, "records", p))
    json.dump({"format": P.RECORD_FORMAT, "records": []}, open(os.path.join(root, "records", "index.json"), "w"))
    run = {"id": "dry-run", "attempt": "1", "event": "workflow_dispatch", "url": ""}
    written = []
    for i, path in enumerate(legs):
        leg_doc = P.read_leg(path)
        commits = [{"commit": c["commit"], "refs": c["refs"]} for c in json.load(open(path))["commits"]]
        written += P.pack_records(commits, DATE, [leg_doc], 1, f"Wed, 14 Oct 2026 12:0{i}:00 GMT", run)
    if canary_json:
        written += P.canary_record(json.load(open(canary_json)), "Wed, 14 Oct 2026 12:09:00 GMT", run)
    index = P.write(root, written)
    readme = open(os.path.join(root, "README.md")).read()
    table = readme.split(P.BEGIN)[1].split(P.END)[0].strip()
    prop(f"records: {len(written)} records written into a scratch copy of this repository, listed in the index and "
         f"the README's table", len(index["records"]) == len(written) and table.count("\n| ") == len(written),
         table)
    print("\n".join("      " + ln for ln in table.splitlines()))
    return root


def main():
    ap = argparse.ArgumentParser(prog="ci/tests/dry_run.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--pack-public", required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--build")
    src.add_argument("--bag")
    # Required: without it the swap plant could not run, and the run would still say every plant failed by name.
    ap.add_argument("--token-sample", required=True, help="a timestamp token over other data, for the swap plant")
    ap.add_argument("--keep", help="a directory to keep the scratch trees in")
    a = ap.parse_args()
    if not os.path.isfile(a.token_sample):
        print(f"  status-dry-run: --token-sample {a.token_sample!r} is no file; nothing was run")
        return 2
    F.refuse_tokens()
    t = a.keep or tempfile.mkdtemp(prefix="status-dry-")
    os.makedirs(t, exist_ok=True)
    try:
        legs = anchor_stage(t, os.path.abspath(a.pack_public), a.token_sample)
        repo, sha = make_bag(t, os.path.abspath(a.pack_public), a.build and os.path.abspath(a.build),
                             a.bag and os.path.abspath(a.bag))
        legs.append(release_stage(t, repo, sha))
        release_plants(t, repo, sha)
        cj = canary(t, repo, sha)
        records(t, legs, cj)
    finally:
        if not a.keep:
            shutil.rmtree(t, ignore_errors=True)
    if FAILED:
        print(f"  status-dry-run: {len(FAILED)} propert{'y' if len(FAILED) == 1 else 'ies'} failed")
        return 1
    print("  status-dry-run: the anchor and release stages, the canary and the records hold, and every plant failed by name")
    return 0


if __name__ == "__main__":
    sys.exit(main())
