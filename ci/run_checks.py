#!/usr/bin/env python3
"""The pack checks on one platform, a leg, for each commit ci/detect.py found (REG-409, REG-416).

    ci/run_checks.py --commits-env COMMITS --leg NAME --out FILE [--python PY] [--source URL-or-path]

The pack repository is cloned anonymously, and each commit is checked out in a clone of its own, as a reader holds
it. What it is checked for follows from what it holds:

  every commit    the repository holds no workflow (REG-409: no file under .github/workflows/); its tree holds no
                  link (mode 120000) and no submodule (mode 160000) anywhere, each one held failing by its path and
                  kind, as git ls-tree -r reads the commit in this leg's clone, never as the checkout shows it; and
                  every anchor manifest, anchor/predicates-<N>.manifest, that a commit it descends from held, it holds
                  too, each one gone failing by name, so that no anchor leaves the pack by a commit that drops it or
                  anchor/ (a commit whose history held none passes, and a history the clone cannot show is
                  infrastructure). A manifest is held as a file, under its number as the pack writes it: a link, a
                  folder or a submodule by its name holds none, and nor does a name such as predicates-01.manifest.
  anchor stage    a commit that holds anchor/ and no bagit.txt. At every stage, a commit that holds
                  anchor/allowed_signers or an anchor manifest is checked for the keys anchor/allowed_signers names:
                  every one is a key this repository pins in ci/release-keys.json, each line read as ssh-keygen
                  reads it, a key outside the pin failing by its fingerprint and a line ssh-keygen could read another
                  way by its number (the pin may hold more: a key that signed no anchor the pack holds leaves the
                  pack's file before the pin, and one that signed an anchor the pack holds leaves neither), and
                  line 1 is the plain line of a key the pin marks for the tags, as the pack's
                  VERIFYING.md makes a reader's tag check from that line's third and fourth fields, any other line 1
                  failing by its number. And for each anchor, its signature with `ssh-keygen -Y verify`
                  (falden-fixture-release, namespace falden-fixture-anchor), both of its RFC 3161 tokens with
                  `openssl ts -verify` under OpenSSL 3 against anchor/tsa-ca.pem, and its tag anchor/predicates-<N>
                  with `git verify-tag`. The signature and the tag are verified with the pinned keys alone, never
                  with the keys the commit names: the signature with every pinned key, the tag with the pinned
                  release key admitted in git's namespace, as the pack's VERIFYING.md admits the release key. Each
                  file these checks read is one the commit holds itself: a file that is a link, or lies under one,
                  or is a folder, fails the check that reads it, naming it, since a link may lead out of the commit
                  to a file this leg's own clone holds and no reader's clone does. The anchor checks run at the
                  release stage too.
  release stage   a commit whose root holds bagit.txt: both manifests with sha256sum -c, bagit 1.9.0 --validate,
                  `fixpack verify` (PACK VERIFIED), `fixpack witness` (WITNESS VERIFIED), the conformance suite
                  (checks behaved), the crash adapter (exit 3), the grade's --json result against
                  schema/result.schema.json, and the fenced blocks of VERIFYING.md: each classified by the sha256
                  of its text in ci/verifying-blocks.json and run where its class says, once per attested bundle
                  for a per-bundle block; a block not classified fails, naming its line and digest.

Each check is pass, fail, skipped (with why) or infrastructure: an install or a download that still fails after
three tries (a venv's pip, brew's openssl@3, the clone, a commit's fetch while the repository cannot be read) is
infrastructure, never a pass or a fail of the pack. A commit the repository answers for and does not hold fails.
A check that stops on an error raised by what the commit holds fails its commit, naming the error, and the leg goes
on to the next commit; so does a command whose folder in the checkout is not a folder or cannot be entered, as when
the commit holds a link to a folder the runner may not enter. A tool the runner cannot start (starting git,
ssh-keygen, openssl, python or another raises any other OSError) is the runner's fault, not the pack's: the leg ends
with no result written, which the publish step records as infrastructure for that leg (the root's ruling 8 (ii) for
P12-26). A leg starts no tool from an entry of the runner's PATH that is empty, '.' or another relative one, each of
which names a folder by where a command runs, the commit's checkout or this leg's clone among them: they are dropped
before the first tool starts, so a tool found only behind one is a tool the runner cannot start, and the python
--python names and the OpenSSL OPENSSL names are each started by its absolute path (the root's ruling 9 (ii) for
P12-26). A leg starts git, and every command of the pack's, with none of the runner's git configuration, attributes
files or templates (leg_env()): no GIT_ variable of the runner's, the global configuration and the global attributes
file /dev/null, the system configuration and the system attributes file not read, and no template to copy into a
repository git makes; what a check needs is given on its command line (ruling 9 (iii)).
The leg's python runs every Python command of the pack: `python3` on PATH is it. The result is written to --out
in the format falden-status-leg/1, and the exit is 0 when every commit passed, 1 when one failed, and 2 when
nothing failed and something could not be run, or when the runner could not start a tool and nothing is written.

For the tests and dry runs: STATUS_OFFLINE=1 skips every check that needs the network (pip, brew), each said so;
BAGIT_CMD names a bagit to run in place of the venv's, as a command line; --checks keeps only the checks named.
"""
import argparse
import base64
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forge as F  # noqa: E402

PACK_URL = "https://github.com/falden-fixtures/falden-fixture-pack"
BLOCKS = os.path.join(HERE, "verifying-blocks.json")
KEYS = os.path.join(HERE, "release-keys.json")
KEYS_FORMAT = "falden-status-keys/1"
KEY_TYPE = re.compile(r"ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp(?:256|384|521)|sk-(?:ssh-ed25519|ecdsa-sha2-nistp256)@openssh\.com")
LEG_FORMAT = "falden-status-leg/1"
SIGNER, NAMESPACE = "falden-fixture-release", "falden-fixture-anchor"
GOOD_SIGNATURE = f'Good "{NAMESPACE}" signature for {SIGNER}'
GOOD_TAG = 'Good "git" signature for release@falden.ai'
DETAIL = 1500
OFFLINE = os.environ.get("STATUS_OFFLINE") == "1"


# ------------------------------------------------------------------ running things
class RunnerFault(Exception):
    """The runner cannot start a tool it needs: infrastructure, never a finding about the pack (the root's ruling 8
    (ii) for P12-26). The leg ends with no result written, which the publish step records as infrastructure for a leg
    whose result never arrived."""


def start(cmd, cwd=None, **kw):
    """subprocess.run(cmd, cwd=cwd, **kw). When starting `cmd` raises an OSError (no such file, permission denied or
    another), the runner cannot start that tool: RunnerFault. Every `cwd` given here is the commit's checkout or a
    folder of it, so when `cwd` is not a folder, or the error names `cwd`, as Python names a folder it could not enter
    to start the command (a link the commit holds may lead to a folder this runner may not enter), what the commit
    holds caused it, and the error is raised as it is, failing that commit."""
    try:
        return subprocess.run(cmd, cwd=cwd, **kw)
    except OSError as e:
        if cwd is not None and (not os.path.isdir(cwd) or getattr(e, "filename", None) == cwd):
            raise
        raise RunnerFault(f"the runner cannot start {cmd[0]}: {e}") from e


def run(cmd, cwd, env, timeout=600, stdin=None):
    """(exit, the output's last DETAIL characters, seconds); exit None on a timeout."""
    t0 = time.time()
    try:
        r = start(cmd, cwd, env=env, capture_output=True, text=True, timeout=timeout,
                  stdin=stdin if stdin is not None else subprocess.DEVNULL, errors="replace")
        out, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
        out, rc = out + f"\n(timed out after {timeout} s)", None
    out = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", out)
    return rc, out[-DETAIL:], round(time.time() - t0, 1)


def check(name, result, detail="", seconds=0):
    return {"name": name, "result": result, "detail": detail.strip()[-DETAIL:], "seconds": seconds}


def absolute_entries(path):
    """The entries of PATH `path` that are absolute, in their order (the root's ruling 9 (ii) for P12-26). An empty
    entry, '.' and any other entry that is not absolute name a folder by where a command runs, which may be the
    commit's checkout or this leg's clone, so a tool found there could be one the commit holds."""
    return [p for p in path.split(os.pathsep) if os.path.isabs(p)]


def leg_env(python, tmp):
    """The environment the pack's commands run in: this leg's python first on PATH as `python3`, in `tmp`, which
    run_leg() names by its absolute path, then the runner's PATH entries that are absolute and no other
    (absolute_entries()); no token; and no git configuration, attributes file or template of the runner's (the root's
    ruling 9 (iii) for P12-26): no GIT_ variable of the runner's environment reaches a git command, the global
    configuration is /dev/null and the system configuration is not read (forge.git_env()), the system attributes file
    is not read (GIT_ATTR_NOSYSTEM) and the global one, core.attributesFile, which is $XDG_CONFIG_HOME/git/attributes
    or $HOME/.config/git/attributes when no configuration names another, is /dev/null, given in the scope of git's
    command line (GIT_CONFIG_COUNT), and no template is copied into a repository git makes (GIT_TEMPLATE_DIR empty), so
    no hook or info/attributes of the runner's git reaches one; and what a check needs, such as the tag check's signers
    file, is given on its command line."""
    bindir = os.path.join(tmp, "leg-bin")
    os.makedirs(bindir, exist_ok=True)
    link = os.path.join(bindir, "python3")
    if not os.path.lexists(link):
        os.symlink(python, link)
    env = F.git_env({k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    # The runner's attributes files, which git reads whatever configuration it reads and which can change what a
    # checkout holds (a line ending, an encoding): the system one is not read, and the global one is /dev/null.
    env["GIT_ATTR_NOSYSTEM"] = "1"
    n = int(env["GIT_CONFIG_COUNT"])
    env.update({"GIT_CONFIG_COUNT": str(n + 1), f"GIT_CONFIG_KEY_{n}": "core.attributesFile",
                f"GIT_CONFIG_VALUE_{n}": os.devnull})
    # And the runner's git templates, which git copies into each repository it makes, the leg's clone and checkouts
    # among them, where a hook among them runs and an info/attributes among them is read: none is copied.
    env["GIT_TEMPLATE_DIR"] = ""
    env["PATH"] = os.pathsep.join([bindir] + absolute_entries(env.get("PATH", "/usr/bin:/bin")))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def platform_name():
    return "macos" if sys.platform == "darwin" else "linux"


def tool_version(cmd, env):
    rc, out, _s = run(cmd, None, env, timeout=60)
    return (out.strip().splitlines() or ["unavailable"])[0] if rc is not None else "unavailable"


# ------------------------------------------------------------------ OpenSSL 3
def openssl3(env, install=True):
    """(path, how) of an OpenSSL 3: the one on PATH, Homebrew's openssl@3, or one installed with brew (three
    tries); (None, why) when none can be had, which the timestamp checks record as infrastructure."""
    cands = [os.environ.get("OPENSSL"), shutil.which("openssl", path=env.get("PATH")),
             "/opt/homebrew/opt/openssl@3/bin/openssl", "/usr/local/opt/openssl@3/bin/openssl"]
    for c in [c for c in cands if c]:
        # By its absolute path, so that the timestamp checks, which run in the commit's checkout, start the file whose
        # version is read here: a bare name as the leg's PATH finds it, any other as named from where this leg runs.
        c = os.path.abspath(c) if os.sep in c else shutil.which(c, path=env.get("PATH"))
        if c is None:
            continue
        try:
            rc, out, _s = run([c, "version"], None, env, timeout=60)
        except RunnerFault:
            continue  # a candidate this runner cannot start is no OpenSSL 3 it holds; the next is tried
        if rc == 0 and out.strip().startswith("OpenSSL 3"):
            return c, out.strip().splitlines()[0]
    brew = shutil.which("brew", path=env.get("PATH"))
    if not (install and brew and sys.platform == "darwin"):
        return None, "no OpenSSL 3: the openssl on PATH is not OpenSSL 3 and Homebrew's openssl@3 is not installed"
    if OFFLINE:
        return None, "no OpenSSL 3 on this machine, and installing one needs the network (STATUS_OFFLINE)"
    for attempt in range(3):
        rc, out, _s = run([brew, "install", "openssl@3"], None, env, timeout=1200)
        if rc == 0:
            return openssl3(env, install=False)
        time.sleep(15 * (attempt + 1))
    return None, f"brew install openssl@3 failed three times: {out.strip()[-300:]}"


# ------------------------------------------------------------------ the anchor stage
# An anchor manifest's name, its number written as the pack writes it (tools/anchor.py): 1, 2 and so on, no leading
# zero, ASCII digits alone. A name written another way, such as predicates-01.manifest, is no anchor's.
MANIFEST_NAME = r"predicates-([1-9][0-9]*)\.manifest"


def not_held(wt, rel, folder=False):
    """Why the commit's checkout at `wt` does not hold `rel` ('/'-separated) as a file of its own (a folder of its
    own, with folder=True), or None when it does. Each part of the path is read with lstat, and none may be a link: a
    link the commit holds may lead out of its checkout, to a file of this leg's own clone of the pack repository that
    no reader's clone of the commit holds, so the anchor stage reads no file through a link."""
    p, parts = wt, rel.split("/")
    for i, part in enumerate(parts):
        p, here = os.path.join(p, part), "/".join(parts[:i + 1])
        try:
            mode = os.lstat(p).st_mode
        except OSError:
            return f"the commit holds no {rel}"
        if stat.S_ISLNK(mode):
            return (f"{rel} is a link" if here == rel else f"{rel} lies under {here}, which is a link") + (
                ", and the anchor stage reads no file through a link")
        if (i < len(parts) - 1 or folder) and not stat.S_ISDIR(mode):
            return f"{here} is not a folder"
        if i == len(parts) - 1 and not folder and not stat.S_ISREG(mode):
            return f"{rel} is {'a folder' if stat.S_ISDIR(mode) else 'not a file'}"
    return None


def anchors(wt):
    """The numbers of the anchors the commit holds: each anchor/predicates-<N>.manifest in anchor/, read only when
    anchor/ is a folder of the commit's own. A manifest by such a name that is a link or a folder is listed too, and
    fails its anchor's checks by name."""
    if not_held(wt, "anchor", folder=True):
        return []
    return sorted({int(m.group(1)) for f in os.listdir(os.path.join(wt, "anchor"))
                   for m in [re.fullmatch(MANIFEST_NAME, f)] if m})


def no_workflow(clone, commit, env):
    rc, out, s = run(["git", "-C", clone, "ls-tree", "-r", "--name-only", commit, "--", ".github/workflows"],
                     None, env)
    if rc != 0:
        return check("the repository holds no workflow", "fail", f"git ls-tree exited {rc}: {out}", s)
    held = [ln for ln in out.splitlines() if ln.strip()]
    return check("the repository holds no workflow", "fail" if held else "pass",
                 ("the commit holds " + ", ".join(held)) if held else "nothing under .github/workflows/", s)


MANIFESTS = "anchor/: every anchor manifest a commit it descends from held, it holds too"
LINKS = "the commit holds no link and no submodule"


def git_out(clone, args, env):
    """(exit, the whole standard output as bytes, the end of standard error) of one git command in the clone; exit
    None on a timeout."""
    try:
        r = start(["git", "-C", clone, *args], env=env, capture_output=True, stdin=subprocess.DEVNULL, timeout=600)
    except subprocess.TimeoutExpired:
        return None, b"", "timed out after 600 s"
    return r.returncode, r.stdout, r.stderr.decode(errors="replace").strip()[-300:]


def no_links(clone, commit, env):
    """One check, at every stage and whatever the commit's history (the root's ruling 8 (i) for P12-26): the commit's
    tree holds no link (mode 120000) and no submodule (mode 160000) anywhere, each one held failing by its path and
    kind. It is read from git ls-tree -r of the commit in this leg's clone, never from the checkout, where a link may
    show as a file and a submodule as an empty folder."""
    t0 = time.time()
    rc, out, err = git_out(clone, ["ls-tree", "-r", "-z", commit], env)
    if rc != 0:
        return check(LINKS, "fail", f"git ls-tree -r exited {rc}: {err}", round(time.time() - t0, 1))
    kinds = {b"120000": "a link", b"160000": "a submodule"}
    entries = [e for e in out.split(b"\0") if e]
    held = []
    for entry in entries:
        meta, _tab, path = entry.partition(b"\t")  # <mode> <type> <object>, a tab, the path
        kind = kinds.get(meta.split()[0]) if meta.split() else None
        if kind:
            held.append(f"{path.decode(errors='replace')} is {kind}")
    named = "; ".join(held)
    if len(named) > DETAIL - 100:  # the record keeps DETAIL characters: name what fits, and how many there are
        named = named[:DETAIL - 100].rsplit("; ", 1)[0] + "; and more"
    return check(LINKS, "fail" if held else "pass",
                 f"{named} ({len(held)} in all)" if held else
                 f"none of the {len(entries)} files of its tree is a link or a submodule", round(time.time() - t0, 1))


def manifests_in(clone, commit, env):
    """The anchor manifests anchor/predicates-<N>.manifest the commit's tree holds, by name, each a file (a blob of
    mode 100644 or 100755): a link, a folder or a submodule by that name holds none; None when git cannot read that
    tree."""
    rc, out, _e = git_out(clone, ["ls-tree", "-z", commit, "anchor/"], env)
    if rc != 0:
        return None
    held = set()
    for entry in out.split(b"\0"):
        meta, _tab, path = entry.partition(b"\t")  # <mode> <type> <object>, a tab, the path
        if meta.split()[:2] in ([b"100644", b"blob"], [b"100755", b"blob"]) and re.fullmatch(
                b"anchor/" + MANIFEST_NAME.encode(), path):
            held.add(path.decode())
    return held


def kept_manifests(clone, sha, env):
    """One check: every anchor manifest that the commit, or a commit it descends from in the pack repository, held,
    the commit holds (the root's ruling 7 (ii) for P12-26), each one gone failing by name, so that no anchor leaves
    the pack by a commit that drops its manifest, or anchor/ itself. A commit whose history held none passes. Each
    commit of the history is read from the clone, which holds the pack repository's whole history: a clone that is
    shallow, or a commit or tree it cannot read, is a history it cannot show, infrastructure and never a pass."""
    t0 = time.time()

    def result(r, detail):
        return check(MANIFESTS, r, detail, round(time.time() - t0, 1))
    rc, out, err = git_out(clone, ["rev-parse", "--is-shallow-repository"], env)
    if rc != 0 or out.strip() != b"false":
        return result("infrastructure", "the clone cannot show the commit's history: "
                      + ("it is shallow" if out.strip() == b"true" else
                         f"git rev-parse --is-shallow-repository exited {rc}: {err}"))
    rc, out, err = git_out(clone, ["rev-list", sha], env)
    history = out.decode(errors="replace").split()
    if rc != 0 or not history:
        return result("infrastructure", f"the clone cannot show the commit's history: git rev-list exited {rc}: {err}")
    held, now = {}, manifests_in(clone, sha, env)
    for c in [sha] + [c for c in history if c != sha]:
        names = now if c == sha else manifests_in(clone, c, env)
        if names is None:
            return result("infrastructure", f"the clone cannot show the commit's history: the tree of {c} cannot be "
                                            f"read")
        for n in names:
            held.setdefault(n, c)  # rev-list names the commit first, then its history, newest first
    gone = sorted(set(held) - now)
    if gone:
        return result("fail", "; ".join(f"{n} is gone, which {held[n][:12]}, a commit it descends from, holds"
                                        for n in gone))
    return result("pass", f"it holds every anchor manifest its history holds: {', '.join(sorted(held))}" if held
                  else "no commit of its history holds an anchor manifest")


def fingerprint(blob):
    """A public key's fingerprint as `ssh-keygen -l` prints it, SHA256:<the sha256 of its blob, base64, unpadded>;
    ValueError when the blob is not base64."""
    raw = base64.b64decode(blob, validate=True)
    return "SHA256:" + base64.b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")


def pinned_keys(path=None):
    """[{"name", "key", "sha256", "tags"}]: the release keys this repository pins (ci/release-keys.json), each key
    `<type> <base64>` and held to the fingerprint it is pinned with, one of them at least marked for the tags.
    ValueError naming what is wrong, which fails every anchor check rather than trusting anything else."""
    path = path or KEYS
    where = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError, RecursionError) as e:
        raise ValueError(f"{where} cannot be read: {e}") from e
    keys = doc.get("keys") if isinstance(doc, dict) and doc.get("format") == KEYS_FORMAT else None
    if not isinstance(keys, list) or not keys:
        raise ValueError(f"{where} is not {KEYS_FORMAT} with a list of keys")
    out = []
    for i, k in enumerate(keys, 1):
        parts = str(k.get("key", "")).split() if isinstance(k, dict) else []
        if len(parts) != 2 or not KEY_TYPE.fullmatch(parts[0]):
            raise ValueError(f"key {i} of {where} is not `<type> <base64>`")
        try:
            fp = fingerprint(parts[1])
        except ValueError as e:
            raise ValueError(f"key {i} of {where} has a blob that is not base64") from e
        if k.get("sha256") != fp:
            raise ValueError(f"key {i} of {where} ({k.get('name')}) is {fp}, not the {k.get('sha256')} it is pinned as")
        out.append({"name": str(k.get("name") or f"key {i}"), "key": " ".join(parts), "sha256": fp,
                    "tags": k.get("tags") is True})
    if not any(k["tags"] for k in out):
        raise ValueError(f"{where} marks no key for the tags")
    return out


def signer_key(line):
    """The key one line of an allowed_signers file names, read as ssh-keygen reads the line (sshsig.c): its
    principals, then its options when the next field is not a key type, then the key's type and base64; (type,
    base64, comment), or None for a blank line or a comment. `line` is the line's bytes, its newline cut.

    ssh-keygen reads a quoted part of the principals, and a quoted part of the options, whole, spaces and all, and in
    the options a backslash before a quote keeps that quote from closing; a plain field split does neither, and takes
    for spaces bytes ssh-keygen does not (0x1f, a no-break space), while ssh-keygen ends the principals at a carriage
    return, as a split on spaces and tabs does not. So a line is read here only where the readings cannot differ:
    printable ASCII, spaces and tabs alone, no quote in the principals, and options with no backslash and no quote
    left open at a space or tab. Any other line raises ValueError, naming why, as does one with no key where
    ssh-keygen reads one."""
    if any(not (b == 9 or 32 <= b <= 126) for b in line):
        raise ValueError("holds a character other than printable ASCII, a space or a tab")
    text = line.decode("ascii").strip(" \t")
    if not text or text.startswith("#"):
        return None
    f = re.split(r"[ \t]+", text)
    if '"' in f[0]:
        raise ValueError("has a quote in its principals")
    at = 1
    if len(f) > 1 and not KEY_TYPE.fullmatch(f[1]):
        if "\\" in f[1] or f[1].count('"') % 2:
            raise ValueError("has a backslash, or a quote left open at a space or tab, in its options")
        at = 2
    if len(f) < at + 2 or not KEY_TYPE.fullmatch(f[at]):
        raise ValueError("names no key where ssh-keygen reads one")
    return f[at], f[at + 1], " ".join(f[at + 2:])


TAG_OPTIONS = f'namespaces="{NAMESPACE}"'
TAG_LINE = f"{SIGNER} {TAG_OPTIONS}"


def plain_tag_key(line, pinned):
    """The pinned name of the key the pin marks for the tags that `line` (its bytes, its newline cut) names in the
    plain form, `falden-fixture-release namespaces="falden-fixture-anchor" <type> <base64>` and a comment or none,
    its fields split as awk splits a line, on spaces and tabs; None for any other line. Line 1 of
    anchor/allowed_signers must be such a line (the root's ruling 7 (iii) for P12-26): the pack's VERIFYING.md makes a
    reader's tag check from line 1's third and fourth fields (awk 'NR==1 {print $3, $4}'), so those must be the tag
    key's type and base64."""
    f = re.split(r"[ \t]+", line.decode("ascii", errors="replace").strip(" \t"))
    if len(f) < 4 or f[0] != SIGNER or f[1] != TAG_OPTIONS:
        return None
    return {k["key"]: k["name"] for k in pinned if k["tags"]}.get(f"{f[2]} {f[3]}")


def key_set(wt, pinned):
    """One check: every key the commit's anchor/allowed_signers names is one the pin holds, each line read as
    ssh-keygen reads it (signer_key()), and line 1 is the plain line of a key the pin marks for the tags
    (plain_tag_key()). A key outside the pin fails, named by its line, type, fingerprint and comment; a line
    ssh-keygen could read another way, or that names no key, fails, named by its line and why; and any other line 1
    fails, named as line 1."""
    name = "anchor/allowed_signers: every key it names is pinned in ci/release-keys.json"
    why = not_held(wt, "anchor/allowed_signers")
    if why:
        return check(name, "fail", why)
    held = {k["key"]: k["name"] for k in pinned}
    named, bad = [], []
    with open(os.path.join(wt, "anchor", "allowed_signers"), "rb") as fh:
        lines = fh.read().split(b"\n")  # lines as ssh-keygen reads them: a newline ends one, and nothing else does
    for i, ln in enumerate(lines, 1):
        try:
            got = signer_key(ln)
        except ValueError as e:
            bad.append(f"line {i} {e}")
            continue
        if got is None:
            continue
        typ, blob, note = got
        if f"{typ} {blob}" in held:
            named.append(held[f"{typ} {blob}"])
            continue
        try:
            fp = fingerprint(blob)
        except ValueError:
            fp = "a blob that is not base64"
        bad.append(f"line {i} names {typ} {fp}" + (f" ({note})" if note else "")
                   + ", which ci/release-keys.json does not pin")
    if not named and not bad:
        bad.append("it names no key")
    first = plain_tag_key(lines[0], pinned)
    if first is None:
        bad.insert(0, f"line 1 is not the plain line of a key ci/release-keys.json marks for the tags, {TAG_LINE} "
                      f"<type> <base64> and a comment or none: the pack's VERIFYING.md makes a reader's tag check "
                      f"from line 1's third and fourth fields")
    return check(name, "fail" if bad else "pass", "; ".join(bad) or f"{len(named)} keys, each pinned: "
                 f"{', '.join(named)}; line 1 is {first}'s plain line")


def anchor_checks(clone, wt, env, ossl, keys_path=None):
    try:
        pinned = pinned_keys(keys_path)
    except ValueError as e:
        return [check("the release keys this repository pins, ci/release-keys.json", "fail", str(e))]
    out = [key_set(wt, pinned)]
    # The signers the checks below are given: the pinned keys alone, written beside the commit's checkout.
    signers = os.path.join(os.path.dirname(wt), "pinned-signers")
    with open(signers, "w", encoding="utf-8") as fh:
        fh.write("".join(f'{SIGNER} namespaces="{NAMESPACE}" {k["key"]}\n' for k in pinned))
    tag_signers = os.path.join(os.path.dirname(wt), "pinned-tag-signers")
    with open(tag_signers, "w", encoding="utf-8") as fh:
        fh.write("".join(f'release@falden.ai namespaces="git" {k["key"]}\n' for k in pinned if k["tags"]))
    for n in anchors(wt):
        base = f"anchor/predicates-{n}"
        name = f"anchor #{n}: its signature, with ssh-keygen -Y verify"
        # Each file a check reads is the commit's own (not_held()), or the check fails, naming it.
        why = not_held(wt, f"{base}.manifest") or not_held(wt, f"{base}.sig")
        if why:
            out.append(check(name, "fail", why))
        else:
            with open(os.path.join(wt, f"{base}.manifest"), "rb") as fh:
                rc, said, s = run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", SIGNER, "-n",
                                   NAMESPACE, "-s", f"{base}.sig"], wt, env, stdin=fh)
            out.append(check(name, "pass" if rc == 0 and GOOD_SIGNATURE in said else "fail", said, s))
        for tok in ("tsr", "tsr2"):
            name = f"anchor #{n}: its timestamp token {base}.{tok}, with openssl ts -verify (OpenSSL 3)"
            why = not_held(wt, f"{base}.{tok}") or not_held(wt, f"{base}.sig") or not_held(wt, "anchor/tsa-ca.pem")
            if why:
                out.append(check(name, "fail", why))
            elif ossl[0] is None:
                out.append(check(name, "infrastructure", ossl[1]))
            else:
                rc, said, s = run([ossl[0], "ts", "-verify", "-in", f"{base}.{tok}", "-data", f"{base}.sig",
                                   "-CAfile", "anchor/tsa-ca.pem"], wt, env)
                out.append(check(name, "pass" if rc == 0 and "Verification: OK" in said else "fail",
                                 f"{ossl[1]}: {said}", s))
        tag = f"anchor/predicates-{n}"
        rc, _o, _s = run(["git", "-C", clone, "rev-parse", "-q", "--verify", f"refs/tags/{tag}"], None, env)
        name = f"anchor #{n}: its tag {tag}, with git verify-tag"
        if rc != 0:
            out.append(check(name, "fail", f"the repository has no tag {tag} for {base}.manifest"))
            continue
        rc, said, s = run(["git", "-C", clone, "-c", f"gpg.ssh.allowedSignersFile={tag_signers}", "verify-tag", tag],
                          None, env)
        out.append(check(name, "pass" if rc == 0 and GOOD_TAG in said else "fail", said, s))
    return out


# ------------------------------------------------------------------ the release stage
def sha256sum_cmd():
    if shutil.which("sha256sum"):
        return ["sha256sum", "-c", "--quiet"]
    return ["shasum", "-a", "256", "-c", "--quiet"]


def bagit_cmd(python, tmp, env):
    """(the command that runs bagit 1.9.0, or None, and why not): BAGIT_CMD, else a venv of this leg's python
    with bagit==1.9.0 from PyPI, three tries."""
    if os.environ.get("BAGIT_CMD"):
        return shlex.split(os.environ["BAGIT_CMD"]), ""
    if OFFLINE:
        return None, "installing bagit 1.9.0 needs the network (STATUS_OFFLINE)"
    venv = os.path.join(tmp, "bagit-venv")
    rc, out, _s = run([python, "-m", "venv", venv], None, env, timeout=300)
    if rc != 0:
        return None, f"python -m venv failed: {out}"
    pip = os.path.join(venv, "bin", "pip")
    for attempt in range(3):
        rc, out, _s = run([pip, "install", "--disable-pip-version-check", "bagit==1.9.0"], None, env, timeout=600)
        if rc == 0:
            return [os.path.join(venv, "bin", "python"), "-m", "bagit"], ""
        time.sleep(15 * (attempt + 1))
    return None, f"pip install bagit==1.9.0 failed three times: {out.strip()[-300:]}"


def result_schema(wt, env):
    data = os.path.join(wt, "data")
    name = "the grade's --json result against schema/result.schema.json"
    t0 = time.time()
    try:
        r = start(["python3", "bin/fixpack", "grade", "--json", "adapters/oracle.py"], data, env=env,
                  capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900, errors="replace")
        result = json.loads(r.stdout)
        sch = json.load(open(os.path.join(data, "schema", "result.schema.json"), encoding="utf-8"))
    except (ValueError, OSError, subprocess.TimeoutExpired) as e:
        return check(name, "fail", f"the result or the schema could not be read: {e}", round(time.time() - t0, 1))
    missing = [k for k in sch.get("required", []) if k not in result]
    extra = [k for k in result if k not in sch.get("properties", {})]
    ok = r.returncode == 0 and not missing and not extra and result.get("adapter_error") is None
    return check(name, "pass" if ok else "fail",
                 f"exit {r.returncode}; required keys missing {missing}, keys the schema does not declare {extra}, "
                 f"adapter_error {result.get('adapter_error')!r}", round(time.time() - t0, 1))


def fenced(text):
    """[(line of the opening fence, the block's text)] for each fenced block of `text`."""
    out, cur, start = [], None, None
    for i, ln in enumerate(text.split("\n"), 1):
        if ln.startswith("```"):
            if cur is None:
                cur, start = [], i
            else:
                out.append((start, "\n".join(cur) + "\n"))
                cur = None
        elif cur is not None:
            cur.append(ln)
    return out


def block_digest(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def load_blocks(path=BLOCKS):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return {b["sha256"]: b for b in doc["blocks"]}


def bundles(wt):
    """[{placeholder: value}] for each attested dispatch of the witness record, for a per-bundle block; and the
    problems that keep one from being run. The repository is the journal's for the dispatch's event, the event
    id being <lineage>.<seq> (the attest design, 2.2)."""
    w = os.path.join(wt, "data", "witness")
    ap = os.path.join(w, "attest.json")
    if not os.path.isfile(ap):
        return [], []
    try:
        doc = json.load(open(ap, encoding="utf-8"))
        lines = open(os.path.join(w, "journal.jsonl"), encoding="utf-8").read().splitlines()
        head = json.loads(lines[0]) if lines else {}
        repos = {}
        for ln in lines[1:]:
            r = json.loads(ln)
            if isinstance(r.get("seq"), int) and isinstance(r.get("repo"), str):
                repos[f"{head.get('lineage')}.{r['seq']}"] = r["repo"]
    except (OSError, ValueError, IndexError) as e:
        return [], [f"the witness record cannot be read for its bundles: {e}"]
    out, problems = [], []
    for d in doc.get("dispatches") or []:
        a = d.get("attested") if isinstance(d, dict) else None
        if d.get("outcome") != "attested" or not isinstance(a, dict):
            continue
        acq = next((x for x in d.get("acquisitions") or [] if x.get("bundle") == a.get("bundle")), {})
        vals = {"<bundle>": a.get("bundle") and os.path.join("witness", a["bundle"]),
                "<owner>/<repository>": repos.get(d.get("event_id")), "<ref>": d.get("ref"),
                "<digest>": a.get("digest"),
                "<trusted root file>": acq.get("trusted_root") and os.path.join("witness", acq["trusted_root"])}
        gone = [k for k, v in vals.items() if not v]
        if gone:
            problems.append(f"dispatch {d.get('dispatch_id')}: the record gives no {', '.join(gone)}")
        else:
            out.append(vals)
    return out, problems


def verifying_checks(wt, env, plat, blocks):
    """One check for the page's classification, and one for each block run here."""
    page = os.path.join(wt, "VERIFYING.md")
    if not os.path.isfile(page):
        return [check("VERIFYING.md: every fenced block classified", "fail", "the commit holds no VERIFYING.md")]
    found = fenced(open(page, encoding="utf-8").read())
    unclassified = [(n, block_digest(b)) for n, b in found if block_digest(b) not in blocks]
    out = [check("VERIFYING.md: every fenced block classified in ci/verifying-blocks.json",
                 "fail" if unclassified else "pass",
                 "; ".join(f"the block at line {n} (sha256 {h[:16]}) is not classified" for n, h in unclassified)
                 or f"{len(found)} blocks, each classified")]
    bset, bprob = None, []
    for n, body in found:
        b = blocks.get(block_digest(body))
        if b is None:
            continue
        name = f"VERIFYING.md block at line {n} ({body.strip().splitlines()[0][:60] if body.strip() else 'empty'})"
        cls = b["class"]
        if "manual" in cls:
            out.append(check(name, "skipped", f"not run here: {b['why']}"))
            continue
        if plat not in cls:
            out.append(check(name, "skipped", f"runs on {', '.join(c for c in cls if c != 'per-bundle')} only"))
            continue
        if b.get("network") and OFFLINE:
            out.append(check(name, "skipped", "it needs the network (STATUS_OFFLINE): " + b["why"]))
            continue
        runs = [{}]
        if "per-bundle" in cls:
            if bset is None:
                bset, bprob = bundles(wt)
            if bprob:
                out.append(check(name, "fail", "; ".join(bprob)))
                continue
            if not bset:
                out.append(check(name, "skipped", "this pack's witness record holds no attested dispatch"))
                continue
            runs = bset
        for vals in runs:
            text = body
            for k, v in vals.items():
                text = text.replace(k, shlex.quote(v))
            script = os.path.join(os.path.dirname(wt), f"block-{n}.sh")
            open(script, "w", encoding="utf-8").write(text)
            cwd = os.path.join(wt, b.get("cwd", "."))
            tries = 3 if b.get("network") else 1
            installed = True
            for attempt in range(tries):
                rc, said, s = run(["bash", "-e", "-o", "pipefail", script], cwd, env, timeout=int(b.get("timeout", 1800)))
                installed = not b.get("probe") or run(["bash", "-c", b["probe"]], cwd, env, timeout=120)[0] == 0
                if installed:
                    break
                time.sleep(15 * (attempt + 1))
            if not installed:
                out.append(check(name, "infrastructure", f"its install did not complete in {tries} tries: {said}", s))
                continue
            want = int(b.get("expect_exit", 0))
            ok = rc == want and all(e in said for e in b.get("expect", []))
            label = name + (f" for {vals.get('<owner>/<repository>')} {vals.get('<ref>')}" if vals else "")
            out.append(check(label, "pass" if ok else "fail",
                             f"exit {rc}, expected {want}" + (f", and {b['expect']}" if b.get("expect") else "")
                             + (f" ({b['why_exit']})" if b.get("why_exit") else "") + f": {said}", s))
    return out


def release_checks(wt, env, python, tmp, plat, blocks, only):
    out = []

    def want(key):
        return not only or key in only

    sums = sha256sum_cmd()
    for key, man in (("manifest", "manifest-sha256.txt"), ("tagmanifest", "tagmanifest-sha256.txt")):
        if want(key):
            rc, said, s = run(sums + [man], wt, env)
            out.append(check(f"{man} with {' '.join(sums[:-1])}", "pass" if rc == 0 else "fail", said or "every line OK", s))
    if want("bagit"):
        cmd, why = bagit_cmd(python, tmp, env)
        if cmd is None:
            out.append(check("bagit 1.9.0 --validate", "skipped" if OFFLINE else "infrastructure", why))
        else:
            rc, said, s = run(cmd + ["--validate", "."], wt, env, timeout=1800)
            out.append(check("bagit 1.9.0 --validate", "pass" if rc == 0 and "is valid" in said else "fail", said, s))
    for key, cmd, ok_line in (("verify", ["python3", "data/bin/fixpack", "verify"], "PACK VERIFIED"),
                              ("witness", ["python3", "data/bin/fixpack", "witness"], "WITNESS VERIFIED"),
                              ("conformance", ["bash", "data/conformance/run.sh"], "checks behaved")):
        if want(key):
            rc, said, s = run(cmd, wt, env, timeout=3600)
            out.append(check(" ".join(cmd[1:] if cmd[0] == "python3" else cmd), "pass" if rc == 0 and ok_line in said
                             else "fail", said, s))
    if want("crash"):
        rc, said, s = run(["python3", "bin/fixpack", "grade", "adapters/crash.sh"], os.path.join(wt, "data"), env,
                          timeout=900)
        out.append(check("the crash adapter is an adapter error, exit 3", "pass" if rc == 3 else "fail",
                         f"exit {rc}: {said}", s))
    if want("schema"):
        out.append(result_schema(wt, env))
    if want("verifying"):
        out += verifying_checks(wt, env, plat, blocks)
    return out


# ------------------------------------------------------------------ one leg
def clone_pack(source, dest, env):
    last = ""
    for attempt in range(3):
        shutil.rmtree(dest, ignore_errors=True)
        rc, out, _s = run(["git", "clone", "--quiet", source, dest], None, env, timeout=1800)
        if rc == 0:
            return None
        last = out
        time.sleep(10 * (attempt + 1))
    return f"git clone {source} failed three times: {last.strip()[-300:]}"


def checkout(clone, wt, sha, env):
    """`sha` checked out at `wt` as a reader's clone holds it, with a .git directory of its own (sharing the clone's
    objects), never a worktree: a worktree's .git is a file, which the pack's verifier reads as a tag file no manifest
    lists (FIX-E016), so a worktree would fail a sound release. (exit, output)."""
    rc, out, _s = run(["git", "clone", "--quiet", "--shared", "--no-checkout", clone, wt], None, env, timeout=600)
    if rc == 0:
        rc, out, _s = run(["git", "-C", wt, "checkout", "--quiet", "--detach", sha], None, env, timeout=600)
    return rc, out


def fetch_commit(clone, sha, env, pause=10):
    """(None, '') when `sha` was fetched into the clone from its origin, three tries; else (result, why): 'fail' when
    the origin answers and does not give the commit, which the repository then does not hold, and 'infrastructure'
    when the origin could not be read at all, after three tries more, never a pass or a fail of the pack."""
    last = ""
    for attempt in range(3):
        rc, out, _s = run(["git", "-C", clone, "fetch", "-q", "origin", sha], None, env, timeout=600)
        if rc == 0:
            return None, ""
        last = out.strip()[-300:]
        if attempt < 2:
            time.sleep(pause * (attempt + 1))
    for attempt in range(3):
        rc, out, _s = run(["git", "-C", clone, "ls-remote", "origin", "HEAD"], None, env, timeout=120)
        if rc == 0:
            return "fail", f"the repository does not hold {sha}: git fetch said {last}"
        if attempt < 2:
            time.sleep(pause * (attempt + 1))
    return "infrastructure", (f"{sha} could not be fetched, and the repository could not be read, three tries each: "
                              f"{out.strip()[-300:]}")


STOPPED = "the checks of this commit, run to their end"


def commit_result(checks):
    rs = {c["result"] for c in checks}
    return "fail" if "fail" in rs else "infrastructure" if "infrastructure" in rs else "pass"


def run_leg(commits, leg, python, source=PACK_URL, only=None, blocks_path=BLOCKS, say=print):
    with tempfile.TemporaryDirectory(prefix="pack-checks-") as tmp:
        # By its absolute path: Python 3.11 and older name it as TMPDIR does, and a TMPDIR of '.' would make the leg's
        # own PATH entry, and every file the checks name in it, relative to where each command runs.
        tmp = os.path.abspath(tmp)
        env = leg_env(python, tmp)
        plat = platform_name()
        info = {"name": leg, "platform": plat, "system": platform.platform(),
                "python": tool_version([python, "--version"], env), "git": tool_version(["git", "--version"], env),
                "ssh": tool_version(["ssh", "-V"], env)}
        clone = os.path.join(tmp, "pack")
        err = clone_pack(source, clone, env)
        if err:
            return {"format": LEG_FORMAT, "leg": info, "result": "infrastructure", "problem": err,
                    "commits": [{"commit": c["commit"], "refs": c["refs"], "stage": "unknown", "result": "infrastructure",
                                 "checks": [check("the pack repository, cloned anonymously", "infrastructure", err)]}
                                for c in commits]}
        ossl = None
        blocks = load_blocks(blocks_path)
        results = []
        for c in commits:
            sha, stage, checks = c["commit"], "unknown", []
            try:
                wt = os.path.join(tmp, f"wt-{sha[:12]}", "tree")
                os.makedirs(os.path.dirname(wt))
                rc, out = checkout(clone, wt, sha, env)
                if rc != 0:
                    shutil.rmtree(wt, ignore_errors=True)
                    got, why = fetch_commit(clone, sha, env)
                    if got is None:
                        rc, out = checkout(clone, wt, sha, env)
                        got, why = "fail", f"the repository does not hold {sha}: {out}"
                if rc != 0:
                    results.append({"commit": sha, "refs": c["refs"], "stage": "unknown", "result": got,
                                    "checks": [check("the commit, checked out", got, why)]})
                    continue
                stage = ("release" if os.path.isfile(os.path.join(wt, "bagit.txt"))
                         else "anchor" if os.path.isdir(os.path.join(wt, "anchor")) else "none")
                if not only or "workflow" in only:
                    checks.append(no_workflow(clone, sha, env))
                if not only or "links" in only:
                    checks.append(no_links(clone, sha, env))
                if not only or "anchor" in only:
                    checks.append(kept_manifests(clone, sha, env))
                    # The keys anchor/allowed_signers names are checked at every stage, with or without a manifest.
                    if anchors(wt) or os.path.lexists(os.path.join(wt, "anchor", "allowed_signers")):
                        if anchors(wt):
                            if ossl is None:
                                ossl = openssl3(env)
                            info["openssl"] = ossl[1]
                        checks += anchor_checks(clone, wt, env,
                                                ossl or (None, "no anchor manifest: no token to verify"))
                if stage == "release":
                    checks += release_checks(wt, env, python, tmp, plat, blocks, only)
            except RunnerFault:
                raise  # the runner's fault, not the commit's: the leg ends with no result written (ruling 8 (ii))
            except Exception as e:  # noqa: BLE001
                # An error raised while a commit is checked, which what the commit holds can cause, fails that commit,
                # naming the error, and the leg goes on to the next: it never ends the leg before its result is
                # written, which would leave every commit of the run with no result, recorded as infrastructure.
                checks.append(check(STOPPED, "fail", f"they stopped on {type(e).__name__}: {e}"))
            r = commit_result(checks)
            refs = ", ".join(c["refs"]) or "named by commit"
            not_passed = [f"{x['result']}: {x['name']}" for x in checks if x["result"] != "pass"]
            say(f"  {sha[:12]} ({refs}): {stage} stage, {r}, {len(checks)} checks"
                + (f"; {'; '.join(not_passed)}" if not_passed else ""))
            results.append({"commit": sha, "refs": c["refs"], "stage": stage, "result": r, "checks": checks})
        return {"format": LEG_FORMAT, "leg": info, "result": commit_result(
            [{"result": x["result"]} for x in results]) if results else "pass", "commits": results}


def main(argv):
    ap = argparse.ArgumentParser(prog="ci/run_checks.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--commits-env", default="COMMITS", help="the environment variable holding detect's commits")
    ap.add_argument("--leg", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--source", default=PACK_URL)
    ap.add_argument("--checks", default="", help="comma-separated: workflow, links, anchor, manifest, tagmanifest, "
                                                  "bagit, verify, witness, conformance, crash, schema, verifying")
    a = ap.parse_args(argv)
    try:
        F.refuse_tokens()
    except F.TokenInEnvironment as e:
        print(f"  pack-checks: {e}")
        return 2
    try:
        commits = json.loads(os.environ.get(a.commits_env, "[]"))
        assert isinstance(commits, list) and all(isinstance(c, dict) and re.fullmatch(r"[0-9a-f]{40}", str(c.get("commit")))
                                                 and isinstance(c.get("refs", []), list) for c in commits)
    except (ValueError, AssertionError):
        print(f"  pack-checks: {a.commits_env} is not detect's list of commits")
        return 2
    # The python --python names, found on the absolute entries of PATH alone, as the leg's own PATH holds them.
    python = shutil.which(a.python, path=os.pathsep.join(absolute_entries(os.environ.get("PATH", os.defpath))))
    try:
        if python is None:
            raise RunnerFault(f"the runner cannot start {a.python}: no program it names is found, at its path or on "
                              f"an absolute entry of PATH")
        res = run_leg(commits, a.leg, os.path.realpath(python), a.source,
                      {x.strip() for x in a.checks.split(",") if x.strip()} or None)
    except RunnerFault as e:
        print(f"  pack-checks: {a.leg}: {e}. That is the runner's fault, not the pack's: this leg writes no result, "
              f"and its record shows it as infrastructure")
        return 2
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(f"  pack-checks: {a.leg}: {res['result']} ({len(res['commits'])} commit(s)); written to {a.out}")
    return {"pass": 0, "fail": 1}.get(res["result"], 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
