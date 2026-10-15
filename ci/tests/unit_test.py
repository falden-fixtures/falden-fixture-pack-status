#!/usr/bin/env python3
"""The status repository's own tests, offline: no network is reached, and nothing outside a temporary directory is
written. Each property is checked on what the code does as it is, and each plant, a fault put in on purpose, must be
refused by name.

  forge      a token in the environment stops a run; no Authorization header is sent; the 61st request to the API
             in an hour waits for the hour to pass, and a request after GitHub says none remain waits for its reset;
             a wait past the run's limit is refused; a read that fails three times is Unreachable;
  detect     a commit a branch or tag points at with no record is named, one with a pass or a fail recorded with
             the same refs is not, a tag peeled to its commit, pull request refs left out; planted: a commit whose
             only record is infrastructure is named again, and so is one with two, while one with three is left to
             a dispatch; a dispatch's ref is named whatever the records say, and one that names nothing is refused;
             a private or other repository is refused;
  keys       the pinned release keys are read from ci/release-keys.json, each held to its fingerprint, which is the
             one ssh-keygen -l prints; planted: a pin whose fingerprint is not its key's, and one with no key for
             the tags, refused; anchor/allowed_signers naming the pinned keys or some of them passes, and so does
             one whose line 1 is the tag key's plain line, then a comment, a blank line, and the pinned key with no
             options, with tabs and with two options; planted, six line 1s other than the tag key's plain line,
             each in a file whose key lines name pinned keys alone, fail, naming line 1: a comment whose third and
             fourth fields are a key the pin lacks, through which a reader's tag check made by the pack's
             VERIFYING.md command trusts a tag that key signed, a blank line, the other pinned key's line, and the
             tag key's line with no options, with cert-authority and under another principal; planted, one naming
             a key outside the pin fails, naming its line and fingerprint, and one missing fails; six lines that
             ssh-keygen here reads as naming a key the pin lacks, trusting that key's signature through the file,
             with the pinned key in a quoted option, in quoted principals, after an escaped quote, between unit
             separators or no-break spaces, or after the planted key and a carriage return, at which ssh-keygen
             ends the principals, each failing, naming its line, as do two naming such a key under a short type
             name (ED25519, ed25519) with the pinned key in the comment; with keys made here, a manifest signed by
             a key the pin lacks fails its signature check although the commit's anchor/allowed_signers names that
             key, and a tag signed by such a key fails its tag check although that file names it first, while a
             manifest and a tag signed by the pinned key pass;
  stages     through run_leg(), against a repository made here: a commit holding no anchor/ passes at no stage,
             and one holding anchor/allowed_signers and no manifest passes at the anchor stage, its keys checked;
             planted: a key the pin lacks added where no commit of the history holds a manifest fails the key
             check alone; the anchor's manifest removed, and anchor/ removed, each fail the manifests' check
             alone, naming the manifest; both faults of check 4's plant Y, the manifest removed and a key the pin
             lacks added, fail both checks, naming the key and the manifest; and the manifest removed, read from a
             shallow clone, is infrastructure, never a pass;
  kinds      through run_leg(), on an anchor made here, its manifest signed and its tag made by the pinned key:
             planted, the manifest renamed predicates-01.manifest or under the Arabic-Indic digit one, made a
             folder, a link that leads nowhere or a submodule, each failing for the manifest that is gone, and a
             stray predicates-02.manifest beside it, no anchor's, checked as the anchor's own commit is, as is the
             commit that removes it again; anchor/allowed_signers, the signature, a timestamp token and the chains
             each made a link to a copy, and anchor/ made a link to a folder holding anchor/allowed_signers and a
             manifest, each failing the checks that read through it, naming the link; anchor/ made a link, inside
             the commit, to a folder holding the anchor's files and no allowed_signers, at a commit whose history
             holds no manifest, the signature the pinned key's or a key's the pin lacks, and at one that held
             anchor/allowed_signers (check 6's AL1 to AL3), anchor/ made a submodule, a link at the root of a
             commit holding no anchor/, a link and a submodule three folders down beside the anchor, and a payload
             link at the release stage, each failing the check that the commit holds no link and no submodule,
             naming it, as each link and submodule above does too; and bagit.txt added, whose checks stop on an
             error, which fails that commit, naming it, while the leg goes on to every other commit, as does
             bagit.txt with data/ a file, and bagit.txt with data/ a link to a folder this runner cannot enter
             (check 7's finding), in a leg with the anchor's commit after it, which keeps its result;
  runner     planted, ssh-keygen missing from PATH or there and not executable, and git missing from PATH: the
             leg ends on RunnerFault, and ci/run_checks.py exits 2, naming the runner's fault, with no result
             written, which publish records as infrastructure beside two legs that passed, so the next run checks
             the commit again; and OPENSSL naming a path that holds nothing, or a bare name that no entry of PATH
             holds, a candidate passed over; and where the line lies: start() raises an error naming the folder a
             command runs in, data/ made a link to a folder this runner cannot enter, as it is, with its tool
             there or missing, and the result schema's check fails on that folder, naming the error, while a tool
             missing in a folder it can enter is RunnerFault; and (the root's ruling 9 (iv)) under a stand-in for
             a Python whose error entering a missing folder carries no filename, start() raises that error as it
             is, and bagit.txt with no data/ fails its commit, naming the error, while the leg goes on to the
             anchor's commit;
  path       (the root's ruling 9 (ii)) planted: a commit holding its own executable ssh-keygen, which says every
             signature is good, beside a changed manifest, with '.', an empty entry or tools/ (a folder of the
             commit) first on PATH, fails its signature check, the runner's ssh-keygen refusing the manifest; with
             '.' first on a PATH that holds no other ssh-keygen, the leg ends on RunnerFault and ci/run_checks.py
             exits 2 with no result, which publish records as infrastructure; TMPDIR naming '.', which tempfile
             keeps relative on Python 3.11 and older, leaves the anchor's commit as it is, the leg naming its own
             folder by its absolute path; --python python3, with '.' first and a python3 in the folder the runner
             runs from, is the python an absolute entry names, and where no absolute entry holds a python3, with
             '.' first or no relative entry at all, is a python the runner cannot start, exit 2 with no result
             written and that folder's python3 never started; and OPENSSL naming ./openssl, a stand-in OpenSSL 3
             there, is started by its absolute path, so both timestamp checks start it, never the openssl the
             commit holds;
  config     (the root's ruling 9 (iii)) planted, each where git would read it, a gpg.ssh.program that does not
             exist: in HOME's .gitconfig, in the XDG configuration, in a file GIT_CONFIG_GLOBAL names, in
             GIT_CONFIG_PARAMETERS and in a git stand-in's system configuration; a global url rewrite sending the
             origin's address to another repository, whose anchor tag a key the pin lacks signed; a global
             core.symlinks false, on the commit whose anchor/ is a link; an attributes file turning every file's
             line endings to CRLF, which git reads whatever configuration it reads: the global one in HOME and in
             the XDG folder, the system one of a git first on PATH that reads it, a copy of a git that finds its
             files from where it is run, and an info/attributes among that git's templates, which it copies into
             each repository it makes; a post-checkout hook among those templates that changes the anchor's
             manifest; and GIT_DIR naming another clone of the origin, and GIT_TEMPLATE_DIR naming a folder whose
             post-checkout hook changes the anchor's manifest: each leaves the commit's record as it is with none,
             check for check, the anchor's tag check passing;
  fetch      a commit the clone lacks and its origin holds is fetched; one the origin answers for and does not hold
             fails, naming it; and with the origin unreadable a commit's fetch is infrastructure, never a fail;
  blocks     the fenced blocks of a page are read and digested as ci/verifying-blocks.json keys them, every block of
             the classified page found there; an attested dispatch's placeholders are filled from attest.json and
             the journal's event ids, and one with no repository is refused, naming it;
  publish    a record for each commit from three legs, its time the forge's Date, its result the worst leg's; a leg
             with no result recorded as infrastructure; a leg that is not falden-status-leg/1 refused as a leg and
             recorded as one with no readable result; the index and the README's table updated, newest first, a ref
             holding Markdown escaped; a record holding a token's shape refused with nothing written; a record path
             already taken refused;
  canary     no release tag from 1.0 on: nothing checked, nothing read from the network, nothing published; the
             newest release tag found among several; an archive member outside its folder, or a link, refused;
             a run that stops on an exception is still a result: the pack repository's refs unread and no release
             in the records, nothing published (exit 1, publish=false); the refs unread and a release in the
             records, published as infrastructure naming it; a release found and its clone unread, published as
             infrastructure; an answer in a shape the code does not read (a Zenodo archive with no links, as
             zenodo_copy() raises on it), a fail named by its type, the checks made before it kept, which the
             publish step writes as a record; and main() writes publish=true and the result when that happens
             after a release is found; a Zenodo archive and a vault tarball holding the release clone's
             tagmanifest-sha256.txt pass that check, and planted, each resealed as a valid bag of other bytes
             fails it, naming both digests;
  settings   while the tree is the first commit's, before any record, settings/SHA256SUMS lists every other file
             of it, each digest matching, and nothing else.

    python3 ci/tests/unit_test.py
"""
import contextlib
import errno
import hashlib
import io
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
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
import run_checks as R  # noqa: E402

FAILED = []
SHA = {n: (c * 40) for n, c in (("main", "a"), ("tag", "b"), ("tagobj", "c"), ("pr", "d"), ("other", "e"))}
# Tools a commit holds of its own (the root's ruling 9 (ii) for P12-26): an ssh-keygen that says every signature is
# good, and an openssl that says every token verifies; and a stand-in OpenSSL 3 the runner names, which says none does.
OWN_KEYGEN = ("#!/bin/sh\necho 'Good \"falden-fixture-anchor\" signature for falden-fixture-release with ED25519 key, "
              "said by an ssh-keygen the commit holds'\nexit 0\n")
OWN_OPENSSL = "#!/bin/sh\necho 'Verification: OK, said by an openssl the commit holds'\nexit 0\n"
RUNNER_OPENSSL = ('#!/bin/sh\nif [ "$1" = version ]; then echo "OpenSSL 3.0.0 (a stand-in the runner names)"; exit 0; fi\n'
                  "echo 'Verification: FAILED, said by the openssl the runner names'\nexit 1\n")


def prop(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        FAILED.append(name)
        if detail:
            print(f"          {str(detail)[:900]}")


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t, self.slept = t, []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def recorded(answers, sent):
    """A transport answering from `answers` ({url: (status, headers, body)}), recording what was sent."""
    def transport(method, url, headers, follow=True):
        sent.append((method, url, dict(headers)))
        if url not in answers:
            raise OSError(f"no recorded answer for {url}")
        status, h, body = answers[url]
        return status, dict(h), body if isinstance(body, bytes) else json.dumps(body).encode()
    return transport


DATE = "Wed, 14 Oct 2026 08:00:00 GMT"


def forge_tests():
    try:
        F.refuse_tokens({"GITHUB_TOKEN": "x"})
        prop("forge: a token in the environment stops a run", False)
    except F.TokenInEnvironment as e:
        prop("forge: a token in the environment stops a run, naming it", "GITHUB_TOKEN" in str(e))
    prop("forge: an empty token variable, as the workflows set them, does not",
         F.refuse_tokens({"GITHUB_TOKEN": "", "GH_TOKEN": ""}) is None)
    sent, clock = [], Clock()
    url = "https://api.github.com/zen"
    fg = F.Forge(transport=recorded({url: (200, {"Date": DATE}, b"ok")}, sent), clock=clock, sleep=clock.sleep, say=lambda m: None)
    for _ in range(60):
        fg.get(url)
    prop("forge: 60 requests to the API in an hour go without a wait, and no Authorization header is sent",
         clock.slept == [] and not any("Authorization" in h for _m, _u, h in sent))
    fg.get(url)
    prop("forge: the 61st within the hour waits for the hour to pass", len(clock.slept) == 1 and 3590 < clock.slept[0] <= 3601,
         clock.slept)
    sent, clock = [], Clock()
    reset = clock.t + 900
    fg = F.Forge(transport=recorded({url: (200, {"Date": DATE, "x-ratelimit-remaining": "0", "x-ratelimit-reset": str(reset)},
                                           b"ok")}, sent), clock=clock, sleep=clock.sleep, say=lambda m: None)
    fg.get(url)
    fg.get(url)
    prop("forge: after GitHub says no request remains, the next waits for the reset it names",
         len(clock.slept) == 1 and 900 <= clock.slept[0] <= 902, clock.slept)
    clock = Clock()
    fg = F.Forge(transport=recorded({url: (403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(clock.t + 7200)},
                                           b"{}")}, []), clock=clock, sleep=clock.sleep, say=lambda m: None, max_wait=3900)
    try:
        fg.get(url)
        prop("forge: a wait past the run's limit is refused", False)
    except F.Unreachable as e:
        prop("forge: a wait past the run's limit is refused, not slept", "past the 3900 s" in str(e), str(e))
    clock = Clock()
    fg = F.Forge(transport=recorded({}, []), clock=clock, sleep=clock.sleep, say=lambda m: None)
    try:
        fg.get("https://api.github.com/missing")
        prop("forge: a read that fails three times is Unreachable", False)
    except F.Unreachable as e:
        prop("forge: a read that fails three times is Unreachable, infrastructure", "after 3 tries" in str(e), str(e))


def detect_tests():
    refs = [(SHA["main"], "refs/heads/main"), (SHA["tagobj"], "refs/tags/anchor/predicates-1"),
            (SHA["tag"], "refs/tags/anchor/predicates-1^{}"), (SHA["pr"], "refs/pull/1/head"), (SHA["main"], "HEAD")]
    repo = {"full_name": D.PACK_REPOSITORY, "private": False, "id": 1}
    fg = F.Forge(transport=recorded({f"https://api.github.com/repos/{D.PACK_REPOSITORY}": (200, {"Date": DATE}, repo)}, []))
    empty = {"records": []}
    got = D.detect(empty, forge=fg, ls=lambda url: refs)
    prop("detect: each commit a branch or tag points at is named, the tag peeled, pull request refs left out",
         got["any"] and got["commits"] == [{"commit": SHA["main"], "refs": ["refs/heads/main"]},
                                           {"commit": SHA["tag"], "refs": ["refs/tags/anchor/predicates-1"]}]
         and got["observed"] == DATE, got)
    done = {"records": [{"workflow": "pack-checks", "commit": SHA["main"], "refs": ["refs/heads/main"],
                         "result": "pass"}]}
    got = D.detect(done, forge=fg, ls=lambda url: refs)
    prop("detect: a commit with a pass recorded with the same refs is not named again",
         [c["commit"] for c in got["commits"]] == [SHA["tag"]], got)
    for name, results, again in (("a fail recorded", ["fail"], False),
                                 ("planted: one infrastructure record alone", ["infrastructure"], True),
                                 ("planted: two infrastructure records alone", ["infrastructure"] * 2, True),
                                 ("three infrastructure records", ["infrastructure"] * 3, False),
                                 ("two infrastructure records and then a pass", ["infrastructure"] * 2 + ["pass"], False)):
        index = {"records": [{"workflow": "pack-checks", "commit": SHA["main"], "refs": ["refs/heads/main"], "result": r}
                             for r in results]}
        got = D.detect(index, forge=fg, ls=lambda url: refs)
        named = SHA["main"] in [c["commit"] for c in got["commits"]]
        prop(f"detect: {name}: the commit is {'named again at the next run' if again else 'not named again'}",
             named is again, got)
    got = D.detect(done, ref="main", forge=fg, ls=lambda url: refs)
    prop("detect: a dispatch's ref is named whatever the records say", got["commits"] == [{"commit": SHA["main"],
                                                                                          "refs": ["refs/heads/main"]}], got)
    got = D.detect(done, ref="anchor/predicates-1", forge=fg, ls=lambda url: refs)
    prop("detect: a dispatch's tag resolves to its commit", got["commits"][0]["commit"] == SHA["tag"], got)
    got = D.detect(done, ref="no-such-ref", forge=fg, ls=lambda url: refs)
    prop("detect: a dispatch's ref that names nothing is refused", "error" in got, got)
    fg2 = F.Forge(transport=recorded({f"https://api.github.com/repos/{D.PACK_REPOSITORY}":
                                      (200, {"Date": DATE}, dict(repo, private=True))}, []))
    try:
        D.detect(empty, forge=fg2, ls=lambda url: refs)
        prop("detect: a private repository is refused", False)
    except ValueError as e:
        prop("detect: a private repository is refused, naming why", "not the public pack repository" in str(e))


def fetch_tests(t):
    """A commit's fetch, against local repositories: README.md says a download that still fails after its retries
    is infrastructure, never a pass or a fail of the pack."""
    env = F.git_env()

    def git(*a):
        return subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.name=unit test", "-c",
                               "user.email=unit-test@example.invalid", *a], env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL)
    src, clone = os.path.join(t, "fetch-origin"), os.path.join(t, "fetch-clone")
    git("init", "-q", "-b", "main", src)
    open(os.path.join(src, "f.txt"), "w").write("one\n")
    git("-C", src, "add", "f.txt")
    git("-C", src, "commit", "-q", "-m", "one")
    git("clone", "-q", src, clone)
    open(os.path.join(src, "f.txt"), "w").write("two\n")
    git("-C", src, "commit", "-q", "-am", "two")
    second = git("-C", src, "rev-parse", "HEAD").stdout.strip()
    got = R.fetch_commit(clone, second, env, pause=0)
    prop("fetch: a commit the clone lacks and its origin holds is fetched",
         got == (None, "") and git("-C", clone, "cat-file", "-e", second).returncode == 0, got)
    got = R.fetch_commit(clone, "f" * 40, env, pause=0)
    prop("fetch: a commit the origin answers for and does not hold fails, naming it",
         got[0] == "fail" and "the repository does not hold " + "f" * 40 in got[1], got)
    git("-C", clone, "remote", "set-url", "origin", os.path.join(t, "no-such-origin"))
    got = R.fetch_commit(clone, "e" * 40, env, pause=0)
    prop("fetch: planted: the origin unreadable: a commit's fetch is infrastructure, never a fail of the pack",
         got[0] == "infrastructure" and "could not be read" in got[1], got)


def attempt(fn, *a, **k):
    """(fn's value, None), or (None, the exception it raised): a property is held on what the code does, and code
    that has no such function, or stops, fails the property rather than the run."""
    try:
        return fn(*a, **k), None
    except Exception as e:  # noqa: BLE001
        return None, e


class NoFilename:
    """A stand-in for the subprocess module of a Python whose error entering a folder that is missing carries no
    filename (Python 3.9.6 to 3.14.6 here each name the folder): its run() raises that error so, and everything else
    is the module's own (the root's ruling 9 (iv) for P12-26)."""
    def __getattr__(self, name):
        return getattr(subprocess, name)

    @staticmethod
    def run(cmd, cwd=None, **kw):
        if cwd is not None and not os.path.isdir(cwd):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))  # no filename
        return subprocess.run(cmd, cwd=cwd, **kw)


def keys_tests(t):
    """The anchor stage trusts only the release keys this repository pins (ci/release-keys.json)."""
    env = F.git_env()
    pin_path = os.path.join(CI, "release-keys.json")
    doc = json.load(open(pin_path, encoding="utf-8"))
    got, err = attempt(R.pinned_keys) if hasattr(R, "pinned_keys") else (None, "no pinned_keys()")
    prop("keys: ci/release-keys.json pins the two keys of the pack's anchor/allowed_signers at cf42ad6, the release "
         "key alone marked for the tags", err is None and [k["name"] for k in got] ==
         ["falden-fixture-release", "falden-fixture-recovery"] and [k["tags"] for k in got] == [True, False]
         and doc["source"]["commit"] == "cf42ad65c52a27df82137e78e7e72420ea615515", err or got)
    kd = os.path.join(t, "keys")
    os.makedirs(kd)

    def make_key(name):
        path = os.path.join(kd, name)
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", name, "-f", path], check=True,
                       capture_output=True, stdin=subprocess.DEVNULL)
        typ, blob = open(path + ".pub").read().split()[:2]
        said = subprocess.run(["ssh-keygen", "-l", "-E", "sha256", "-f", path + ".pub"], capture_output=True,
                              text=True, stdin=subprocess.DEVNULL).stdout.split()
        return {"path": path, "key": f"{typ} {blob}", "sha256": said[1]}
    pinned, other = make_key("pinned-key"), make_key("planted-key")
    fp, err = attempt(R.fingerprint, pinned["key"].split()[1]) if hasattr(R, "fingerprint") else (None, "none")
    prop("keys: a key's fingerprint is the one ssh-keygen -l prints", fp == pinned["sha256"], (fp, pinned["sha256"], err))

    def pin_file(name, keys):
        p = os.path.join(kd, name)
        json.dump({"format": "falden-status-keys/1", "keys": keys}, open(p, "w"))
        return p
    good = pin_file("pin.json", [{"name": "falden-fixture-release", "key": pinned["key"], "sha256": pinned["sha256"],
                                  "tags": True}])
    for name, keys, want in (
            ("planted: a pin whose fingerprint is not its key's", [{"name": "x", "key": pinned["key"],
                                                                    "sha256": other["sha256"], "tags": True}], "is "),
            ("planted: a pin with no key marked for the tags", [{"name": "x", "key": pinned["key"],
                                                                 "sha256": pinned["sha256"], "tags": False}], "tags")):
        got, err = attempt(R.pinned_keys, pin_file("bad.json", keys)) if hasattr(R, "pinned_keys") else (None, None)
        prop(f"keys: {name}: refused, naming why", isinstance(err, ValueError) and want in str(err), (got, err))
    wt = os.path.join(t, "keys-commit", "tree")
    os.makedirs(os.path.join(wt, "anchor"))
    signers = os.path.join(wt, "anchor", "allowed_signers")

    def names(*keys):
        open(signers, "w").write("".join(f'falden-fixture-release namespaces="falden-fixture-anchor" {k["key"]} '
                                         f'{os.path.basename(k["path"])}\n' for k in keys))
    pin = R.pinned_keys(good) if hasattr(R, "pinned_keys") else []
    for name, keys, ok in (("anchor/allowed_signers naming the pinned key", [pinned], True),
                           ("planted: anchor/allowed_signers naming the pinned key and one outside the pin",
                            [pinned, other], False)):
        names(*keys)
        got, err = attempt(R.key_set, wt, pin) if hasattr(R, "key_set") else (None, "no key_set()")
        detail = (got or {}).get("detail", "")
        held = got is not None and got["result"] == ("pass" if ok else "fail") and (
            ok or ("line 2" in detail and other["sha256"] in detail))
        prop(f"keys: {name}: {'passes' if ok else 'fails, naming the line and fingerprint'}",
             held, err or got)
    # The forms the pack's file may take, each read as ssh-keygen reads it, after line 1, the tag key's plain line.
    pt, pb = pinned["key"].split()
    ns = 'namespaces="falden-fixture-anchor"'
    plain = f"falden-fixture-release {ns} {pinned['key']} pinned-key\n"
    open(signers, "w").write(plain + f"# the release keys\n\nfalden-fixture-release {pinned['key']}\n"
                             f"falden-fixture-release\t{ns}\t{pt}\t{pb}\tpinned-key\n"
                             f"  falden-fixture-release cert-authority,{ns} {pinned['key']}\n")
    got, err = attempt(R.key_set, wt, pin) if hasattr(R, "key_set") else (None, "no key_set()")
    prop("keys: anchor/allowed_signers with the pinned key's plain line first, then a comment, a blank line, and the "
         "pinned key with no options, with tabs between its fields and with two options: passes, 4 keys",
         got is not None and got["result"] == "pass" and got["detail"].startswith("4 keys"), err or got)
    line_one_tests(t, kd, wt, signers, pinned, other, pin_file, make_key)
    # Lines that ssh-keygen reads as naming the key the pin lacks, with the pinned key written where ssh-keygen reads
    # no key (P12-26's check of round 3 found the first): each fails, naming its line, while ssh-keygen here, given
    # the same file, trusts a manifest the planted key signed, so that each is a key the pin lacks reaching a reader.
    signed = os.path.join(kd, "planted.manifest")
    open(signed, "w").write("# a manifest the planted key signed\n")
    subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", other["path"], "-n", "falden-fixture-anchor", signed],
                   check=True, capture_output=True, stdin=subprocess.DEVNULL)
    for name, line in (
            ("the pinned key inside a quoted option",
             f'falden-fixture-release namespaces="falden-fixture-anchor,z {pinned["key"]} z" {other["key"]} planted\n'),
            ("the pinned key inside quoted principals",
             f'"falden-fixture-release,z {pinned["key"]} z" {ns} {other["key"]} planted\n'),
            ("the pinned key after an escaped quote inside a quoted option",
             f'falden-fixture-release namespaces="falden-fixture-anchor,z\\" {pinned["key"]} " {other["key"]} planted\n'),
            ("the pinned key between unit separators (0x1f), which str.split() takes for spaces",
             f"falden-fixture-release,z\x1f{pt}\x1f{pb}\x1fz {ns} {other['key']} planted\n"),
            ("the pinned key between no-break spaces (U+00A0), which str.split() takes for spaces",
             f"falden-fixture-release,z\u00a0{pt}\u00a0{pb}\u00a0z {ns} {other['key']} planted\n"),
            ("the planted key after a carriage return, at which ssh-keygen ends the principals, the pinned key after it",
             f"falden-fixture-release\r{other['key']} {pinned['key']} planted\n")):
        open(signers, "wb").write((plain + line).encode("utf-8"))
        with open(signed, "rb") as fh:
            v = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", "falden-fixture-release", "-n",
                                "falden-fixture-anchor", "-s", signed + ".sig"], stdin=fh, capture_output=True,
                               text=True, errors="replace")
        trusts = v.returncode == 0 and "Good" in v.stdout + v.stderr
        got, err = attempt(R.key_set, wt, pin) if hasattr(R, "key_set") else (None, "no key_set()")
        prop(f"keys: planted: a line naming a key the pin lacks, {name}: fails, naming line 2, while ssh-keygen here "
             f"trusts that key through the same file", trusts and got is not None and got["result"] == "fail"
             and "line 2 " in got["detail"], err or {"ssh-keygen trusts the planted key": trusts, "key_set": got})
    for short in ("ED25519", "ed25519"):
        open(signers, "w").write(plain + f"falden-fixture-release {ns} {short} {other['key'].split()[1]} "
                                         f"{pinned['key']}\n")
        got, err = attempt(R.key_set, wt, pin) if hasattr(R, "key_set") else (None, "no key_set()")
        prop(f"keys: planted: a line naming a key the pin lacks under the short type name {short}, the pinned key in "
             f"its comment: fails, naming line 2", got is not None and got["result"] == "fail"
             and "line 2 " in got["detail"], err or got)
    os.remove(signers)
    got, err = attempt(R.key_set, wt, pin) if hasattr(R, "key_set") else (None, "no key_set()")
    prop("keys: planted: no anchor/allowed_signers: fails", got is not None and got["result"] == "fail", err or got)

    # The signature and the tag, verified with the pinned keys alone, against keys made here.
    def git(repo, *a):
        return subprocess.run(["git", "-C", repo, "-c", "user.name=unit test", "-c", "user.email=unit-test@example.invalid",
                               "-c", "commit.gpgsign=false", *a], env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL)
    clone = os.path.join(t, "keys-clone")
    git(t, "init", "-q", "-b", "main", clone)
    open(os.path.join(clone, "f.txt"), "w").write("x\n")
    git(clone, "add", "f.txt")
    git(clone, "commit", "-q", "-m", "one")
    man = os.path.join(wt, "anchor", "predicates-1.manifest")
    open(man, "w").write("# commit " + "a" * 40 + "\n")
    saved = getattr(R, "KEYS", None)  # code with no pin has none
    R.KEYS = good
    try:
        for signer, ok in ((pinned, True), (other, False)):
            names(signer)
            subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", signer["path"], "-n", "falden-fixture-anchor", man],
                           check=True, capture_output=True, stdin=subprocess.DEVNULL)
            os.replace(man + ".sig", os.path.join(wt, "anchor", "predicates-1.sig"))
            git(clone, "-c", "gpg.format=ssh", "-c", f"user.signingkey={signer['path']}", "tag", "-s", "-f", "-m",
                "unit test", "anchor/predicates-1", "HEAD")
            got, err = attempt(R.anchor_checks, clone, wt, env, (None, "no OpenSSL 3 here"))
            by = {c["name"]: c["result"] for c in got or []}
            sig = by.get("anchor #1: its signature, with ssh-keygen -Y verify")
            tag = by.get("anchor #1: its tag anchor/predicates-1, with git verify-tag")
            want = "pass" if ok else "fail"
            if ok:
                prop("keys: a manifest signed by the pinned key: its signature check passes", sig == want, err or by)
                prop("keys: a tag signed by the pinned key: its tag check passes", tag == want, err or by)
            else:
                prop("keys: planted: a manifest signed by a key the pin lacks, which the commit's anchor/allowed_signers "
                     "names: its signature check fails", sig == want, err or by)
                prop("keys: planted: a tag signed by a key the pin lacks, which the commit's anchor/allowed_signers "
                     "names first: its tag check fails", tag == want, err or by)
    finally:
        R.KEYS = saved
    return {"pinned": pinned, "other": other, "good": good}


# The reader's tag check, the pack's VERIFYING.md:643 and :644 as the pack prints them, run in a tree that holds
# anchor/allowed_signers, with the signers file moved from /tmp into the test's own folder and the clone named by -C.
READER_TAG = ("printf 'release@falden.ai namespaces=\"git\" %s\\n' \"$(awk 'NR==1 {print $3, $4}' "
              "anchor/allowed_signers)\" > \"$SIGNERS\"\n"
              "git -C \"$CLONE\" -c gpg.ssh.allowedSignersFile=\"$SIGNERS\" verify-tag anchor/predicates-1\n")


def reader_tag_trusts(tree, clone, signers):
    """Whether a reader's tag check, made by the pack's VERIFYING.md command from `tree`'s anchor/allowed_signers,
    admits the tag anchor/predicates-1 of `clone`."""
    env = dict(F.git_env(), SIGNERS=signers, CLONE=clone)
    r = subprocess.run(["bash", "-c", READER_TAG], cwd=tree, env=env, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, errors="replace")
    return r.returncode == 0 and 'Good "git" signature' in r.stdout + r.stderr


def line_one_tests(t, kd, wt, signers, pinned, other, pin_file, make_key):
    """Line 1 of anchor/allowed_signers (the root's ruling 7 (iii) for P12-26): the pack's VERIFYING.md makes a
    reader's tag check from line 1's third and fourth fields, so line 1 must be the plain line of the key the pin
    marks for the tags. Every key of each file below is pinned; each other line 1 fails, naming line 1, and the
    first is one a reader's tag check, made from the file by that command, trusts a tag the planted key signed."""
    recovery = make_key("recovery-key")
    pin2 = R.pinned_keys(pin_file("pin2.json", [
        {"name": "falden-fixture-release", "key": pinned["key"], "sha256": pinned["sha256"], "tags": True},
        {"name": "falden-fixture-recovery", "key": recovery["key"], "sha256": recovery["sha256"], "tags": False}]))
    ns = 'namespaces="falden-fixture-anchor"'
    plain = f"falden-fixture-release {ns} {pinned['key']} pinned-key\n"
    rec = f"falden-fixture-release {ns} {recovery['key']} recovery-key\n"
    clone = os.path.join(t, "reader-clone")
    env = F.git_env()

    def git(*a):
        return subprocess.run(["git", "-C", clone, "-c", "user.name=unit test", "-c", "user.email=unit-test@example.invalid",
                               "-c", "commit.gpgsign=false", *a], env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL)
    os.makedirs(clone)
    git("init", "-q", "-b", "main")
    open(os.path.join(clone, "f.txt"), "w").write("x\n")
    git("add", "f.txt")
    git("commit", "-q", "-m", "one")
    git("-c", "gpg.format=ssh", "-c", f"user.signingkey={other['path']}", "tag", "-s", "-m", "a tag the planted key "
        "signed", "anchor/predicates-1", "HEAD")
    tag_signers = os.path.join(kd, "reader-tag-signers")
    open(signers, "w").write(plain + rec)
    got, err = attempt(R.key_set, wt, pin2)
    prop("keys: line 1 the release key's plain line, then the recovery key's: passes, 2 keys",
         got is not None and got["result"] == "pass" and got["detail"].startswith("2 keys"), err or got)
    for name, text, reader in (
            ("a comment whose third and fourth fields are the planted key",
             f"# falden-fixture-release {other['key']} planted\n" + plain + rec, True),
            ("a blank line", "\n" + plain + rec, False),
            ("the other pinned key's plain line, the recovery key's", rec + plain, False),
            ("the release key's line with no options", f"falden-fixture-release {pinned['key']} pinned-key\n" + plain + rec,
             False),
            ("the release key's line with another option, cert-authority",
             f"falden-fixture-release cert-authority,{ns} {pinned['key']} pinned-key\n" + rec, False),
            ("the release key's line under another principal",
             f"falden-fixture-recovery {ns} {pinned['key']} pinned-key\n" + plain + rec, False)):
        open(signers, "w").write(text)
        got, err = attempt(R.key_set, wt, pin2)
        trusts = reader_tag_trusts(os.path.dirname(os.path.dirname(signers)), clone, tag_signers) if reader else True
        prop(f"keys: planted: line 1 {name}, every key the file names pinned: fails, naming line 1"
             + (", while a reader's tag check made from the file by the pack's VERIFYING.md command trusts a tag the "
                "planted key signed" if reader else ""),
             got is not None and got["result"] == "fail" and got["detail"].startswith("line 1 ") and trusts,
             err or {"key_set": got, "a reader's tag check trusts the planted key's tag": trusts})


def stage_tests(t, keys):
    """What a commit is checked for, through run_leg(), against a repository made here (the root's ruling 7 for
    P12-26): the keys anchor/allowed_signers names, at every stage and with or without an anchor manifest (i); and
    every anchor manifest a commit's history held (ii), a history the clone cannot show being infrastructure."""
    env = F.git_env()
    origin = os.path.join(t, "stage-origin")
    os.makedirs(origin)

    def git(*a):
        return subprocess.run(["git", "-C", origin, "-c", "commit.gpgsign=false", "-c", "user.name=unit test", "-c",
                               "user.email=unit-test@example.invalid", *a], env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL).stdout.strip()

    def at(rel):
        return os.path.join(origin, *rel.split("/"))

    def write(rel, text, mode="w"):
        os.makedirs(os.path.dirname(at(rel)), exist_ok=True)
        open(at(rel), mode).write(text)

    def commit(base, name, *changes):
        if base:
            git("checkout", "-q", "--detach", base)
        for change in changes:
            change()
        git("add", "-A")
        git("commit", "-q", "-m", name)
        sha = git("rev-parse", "HEAD")
        git("branch", "-f", f"stage/{name}", sha)
        return sha
    ns = 'namespaces="falden-fixture-anchor"'
    plain = f"falden-fixture-release {ns} {keys['pinned']['key']} pinned-key\n"
    unpinned = f"falden-fixture-release {ns} {keys['other']['key']} planted-key\n"
    git("init", "-q", "-b", "main")
    c0 = commit(None, "a-readme", lambda: write("README.md", "a pack\n"))
    c1 = commit(c0, "the-allowed-signers", lambda: write("anchor/allowed_signers", plain))
    c1y = commit(c1, "a-key-the-pin-lacks-before-any-manifest", lambda: write("anchor/allowed_signers", unpinned, "a"))
    c2 = commit(c1, "anchor-1", lambda: write("anchor/predicates-1.manifest", "# commit " + "a" * 40 + "\n"))
    c3 = commit(c2, "the-manifest-removed", lambda: os.remove(at("anchor/predicates-1.manifest")))
    c4 = commit(c2, "anchor-removed", lambda: shutil.rmtree(at("anchor")))
    c5 = commit(c2, "the-manifest-removed-and-a-key-the-pin-lacks-added",
                lambda: os.remove(at("anchor/predicates-1.manifest")),
                lambda: write("anchor/allowed_signers", unpinned, "a"))
    shallow = os.path.join(t, "stage-shallow")
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", "stage/the-manifest-removed", "file://" + origin,
                    shallow], env=env, capture_output=True, stdin=subprocess.DEVNULL)
    saved = getattr(R, "KEYS", None)
    R.KEYS = keys["good"]
    try:
        res, err = attempt(R.run_leg, [{"commit": c, "refs": []} for c in (c0, c1, c1y, c3, c4, c5)], "unit test",
                           sys.executable, origin, say=lambda m: None)
        res2, err2 = attempt(R.run_leg, [{"commit": c3, "refs": []}], "unit test, a shallow clone", sys.executable,
                             shallow, say=lambda m: None)
    finally:
        R.KEYS = saved
    wf = "the repository holds no workflow"
    links = "the commit holds no link and no submodule"
    keyset = "anchor/allowed_signers: every key it names is pinned in ci/release-keys.json"
    kept = "anchor/: every anchor manifest a commit it descends from held, it holds too"
    gone = "anchor/predicates-1.manifest is gone"

    def view(r, sha):
        c = next((x for x in (r or {}).get("commits", []) if x["commit"] == sha), {})
        checks = c.get("checks", [])
        return (c.get("stage"), c.get("result"), [k["name"] for k in checks],
                sorted(k["name"] for k in checks if k["result"] == "fail"), {k["name"]: k["detail"] for k in checks},
                {k["name"]: k["result"] for k in checks})
    fp = keys["other"]["sha256"]
    for name, sha, stage, result, names, failing, said in (
            ("a commit holding no anchor/, as the pack's first commit: passes at no stage, its history holding no "
             "manifest", c0, "none", "pass", [wf, links, kept], [], {kept: "no commit of its history"}),
            ("a commit holding anchor/allowed_signers and no manifest, as the pack's second and third: passes at the "
             "anchor stage, its keys checked", c1, "anchor", "pass", [wf, links, kept, keyset], [], {keyset: "1 keys"}),
            ("planted: a key the pin lacks added to anchor/allowed_signers at a commit whose history holds no "
             "manifest: fails the key check alone, at the anchor stage, naming the key", c1y, "anchor", "fail",
             [wf, links, kept, keyset], [keyset], {keyset: fp}),
            ("planted: the anchor's manifest removed: fails the manifests' check alone, naming the manifest", c3,
             "anchor", "fail", [wf, links, kept, keyset], [kept], {kept: gone}),
            ("planted: anchor/ removed: fails the manifests' check alone, at no stage, naming the manifest", c4, "none",
             "fail", [wf, links, kept], [kept], {kept: gone}),
            ("planted: the anchor's manifest removed and a key the pin lacks added, check 4's plant Y: fails the key "
             "check, naming the key, and the manifests' check, naming the manifest", c5, "anchor", "fail",
             [wf, links, kept, keyset], sorted([keyset, kept]), {keyset: fp, kept: gone})):
        got = view(res, sha)
        prop(f"stages: {name}", err is None and got[:4] == (stage, result, names, failing)
             and all(v in got[4].get(k, "") for k, v in said.items()), err or got)
    got = view(res2, c3)
    prop("stages: planted: the anchor's manifest removed, its commit read from a shallow clone of the repository: "
         "the manifests' check is infrastructure, never a pass, its history one the clone cannot show",
         err2 is None and got[1] == "infrastructure" and got[5].get(kept) == "infrastructure"
         and "shallow" in got[4].get(kept, ""), err2 or got)


def kind_tests(t, keys):
    """What the anchor stage reads, through run_leg(), against a repository made here: an anchor manifest is a file
    named anchor/predicates-<N>.manifest, its number written as the pack writes it, and each file the anchor checks
    read is the commit's own, never a link, nor under one, nor a folder; and a check that stops on an error fails its
    commit, naming the error, while the leg goes on to the next. Every plant is on an anchor made here, its manifest
    signed and its tag made by the pinned key, with stand-ins for the timestamp tokens and their chains."""
    env = F.git_env()
    origin = os.path.join(t, "kind-origin")
    os.makedirs(origin)

    def git(*a):
        return subprocess.run(["git", "-C", origin, "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", "-c",
                               "user.name=unit test", "-c", "user.email=unit-test@example.invalid", *a], env=env,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()

    def at(rel):
        return os.path.join(origin, *rel.split("/"))

    def write(rel, data):
        os.makedirs(os.path.dirname(at(rel)), exist_ok=True)
        open(at(rel), "wb" if isinstance(data, bytes) else "w").write(data)

    def copy(rel, to):
        write(to, open(at(rel), "rb").read())

    def link(rel, target):
        """`rel` made a link to `target`, a path relative to the link's folder."""
        if os.path.lexists(at(rel)):
            os.remove(at(rel))
        os.symlink(target, at(rel))

    def commit(base, name, *changes):
        if base:
            git("checkout", "-q", "--detach", base)
        for change in changes:
            change()
        git("add", "-A", "-f")  # -f: a global ignore file may list *.pem
        git("commit", "-q", "-m", name)
        sha = git("rev-parse", "HEAD")
        git("branch", "-f", f"kind/{name}", sha)
        return sha
    pinned, man = keys["pinned"], "anchor/predicates-1.manifest"
    plain = f'falden-fixture-release namespaces="falden-fixture-anchor" {pinned["key"]} pinned-key\n'

    def anchor_one():
        write(man, "# commit " + "a" * 40 + "\n")
        subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", pinned["path"], "-n", "falden-fixture-anchor", at(man)],
                       check=True, capture_output=True, stdin=subprocess.DEVNULL)
        os.replace(at(man) + ".sig", at("anchor/predicates-1.sig"))
        for f in ("predicates-1.tsr", "predicates-1.tsr2", "tsa-ca.pem"):
            write(f"anchor/{f}", f"a stand-in for {f}, made here\n")

    def gitlink(rel, sha):
        """`rel` made a submodule at `sha`: an empty folder at its path keeps git add -A from dropping it, as a
        submodule that is not checked out is."""
        os.makedirs(at(rel))
        git("update-index", "--add", "--cacheinfo", f"160000,{sha},{rel}")

    def anchor_elsewhere(folder, signer, base_sha):
        """anchor/ made a link, inside the commit, to `folder`, which holds anchor #1's manifest, its signature by
        `signer`, the timestamp stand-ins and the chains, and no allowed_signers (check 6's plants AL1 to AL3)."""
        def fn():
            def blob(rel):
                return subprocess.run(["git", "-C", origin, "show", f"{base_sha}:{rel}"], env=env, capture_output=True,
                                      stdin=subprocess.DEVNULL, check=True).stdout
            for f in ("predicates-1.manifest", "predicates-1.tsr", "predicates-1.tsr2", "tsa-ca.pem"):
                write(f"{folder}/{f}", blob(f"anchor/{f}"))
            subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-f", signer["path"], "-n", "falden-fixture-anchor",
                            at(f"{folder}/predicates-1.manifest")], check=True, capture_output=True,
                           stdin=subprocess.DEVNULL)
            os.replace(at(f"{folder}/predicates-1.manifest.sig"), at(f"{folder}/predicates-1.sig"))
            if os.path.lexists(at("anchor")):
                shutil.rmtree(at("anchor"))
            os.symlink(folder, at("anchor"))
        return fn
    git("init", "-q", "-b", "main")
    c0 = commit(None, "a-readme", lambda: write("README.md", "a pack\n"))
    c1 = commit(c0, "the-allowed-signers", lambda: write("anchor/allowed_signers", plain))
    c2 = commit(c1, "anchor-1", anchor_one)
    git("-c", "gpg.format=ssh", "-c", f"user.signingkey={pinned['path']}", "tag", "-s", "-m", "anchor #1, made here",
        "anchor/predicates-1", c2)
    stray = commit(c2, "a-stray-predicates-02-beside-the-manifest", lambda: copy(man, "anchor/predicates-02.manifest"))
    p = {
        "renamed": commit(c2, "the-manifest-renamed-predicates-01",
                          lambda: os.rename(at(man), at("anchor/predicates-01.manifest"))),
        "digit": commit(c2, "the-manifest-renamed-under-an-arabic-indic-digit",
                        lambda: os.rename(at(man), at("anchor/predicates-\u0661.manifest"))),
        "folder": commit(c2, "the-manifest-made-a-folder", lambda: os.remove(at(man)),
                         lambda: write(man + "/f", "x\n")),
        "dangling": commit(c2, "the-manifest-made-a-link-that-leads-nowhere", lambda: link(man, "nowhere")),
        # An empty folder at a gitlink's path keeps git add -A from dropping it, as a submodule not checked out is.
        "submodule": commit(c2, "the-manifest-made-a-submodule", lambda: os.remove(at(man)),
                            lambda: os.makedirs(at(man)),
                            lambda: git("update-index", "--add", "--cacheinfo", f"160000,{c0},{man}")),
        "stray": stray,
        "stray removed": commit(stray, "the-stray-removed", lambda: os.remove(at("anchor/predicates-02.manifest"))),
        "sig": commit(c2, "the-signature-made-a-link", lambda: copy("anchor/predicates-1.sig", "elsewhere/f.sig"),
                      lambda: link("anchor/predicates-1.sig", "../elsewhere/f.sig")),
        "tsr": commit(c2, "a-timestamp-token-made-a-link", lambda: copy("anchor/predicates-1.tsr", "elsewhere/f.tsr"),
                      lambda: link("anchor/predicates-1.tsr", "../elsewhere/f.tsr")),
        "ca": commit(c2, "the-chains-made-a-link", lambda: copy("anchor/tsa-ca.pem", "elsewhere/f.pem"),
                     lambda: link("anchor/tsa-ca.pem", "../elsewhere/f.pem")),
        "signers": commit(c1, "anchor-allowed-signers-made-a-link",
                          lambda: copy("anchor/allowed_signers", "elsewhere/s"),
                          lambda: link("anchor/allowed_signers", "../elsewhere/s")),
        # The folder holds anchor #1's manifest and signature too, which the anchor checks list through no link.
        "anchor": commit(c0, "anchor-a-link-to-a-folder-holding-allowed-signers-and-anchor-1",
                         lambda: write("elsewhere/allowed_signers", plain),
                         lambda: write("elsewhere/predicates-1.manifest", "# commit " + "a" * 40 + "\n"),
                         lambda: link("anchor", "elsewhere")),
        "bagit": commit(c1, "bagit-txt-added", lambda: write("bagit.txt", "BagIt-Version: 1.0\n")),
        # The root's ruling 8 (i): a link or a submodule anywhere in the tree, at each stage and depth.
        "al1": commit(c0, "anchor-a-link-to-a-folder-holding-anchor-1-and-no-allowed-signers",
                      anchor_elsewhere("elsewhere1", pinned, c2)),
        "al2": commit(c0, "anchor-a-link-to-a-folder-holding-anchor-1-signed-by-a-key-the-pin-lacks",
                      anchor_elsewhere("elsewhere2", keys["other"], c2)),
        "al3": commit(c1, "anchor-replaced-by-a-link-to-such-a-folder", anchor_elsewhere("elsewhere3", keys["other"], c2)),
        "anchor submodule": commit(c0, "anchor-made-a-submodule", lambda: gitlink("anchor", c0)),
        "root link": commit(c0, "a-link-at-the-root", lambda: os.symlink("README.md", at("notes.txt"))),
        "deep link": commit(c2, "a-link-three-folders-down", lambda: write("docs/a/b/real.txt", "x\n"),
                            lambda: os.makedirs(at("docs/a/b/c")),
                            lambda: os.symlink("../real.txt", at("docs/a/b/c/link.txt"))),
        "deep submodule": commit(c2, "a-submodule-three-folders-down", lambda: gitlink("x/y/z", c0)),
        "release link": commit(c1, "bagit-txt-and-a-payload-link", lambda: write("bagit.txt", "BagIt-Version: 1.0\n"),
                               lambda: write("data/real.txt", "x\n"), lambda: os.symlink("real.txt", at("data/x.txt"))),
        # The root's ruling 8 (ii), kin of the bagit.txt plant: data/ a file, which the release checks run in.
        "data a file": commit(c1, "bagit-txt-and-data-a-file", lambda: write("bagit.txt", "BagIt-Version: 1.0\n"),
                              lambda: write("data", "not a folder\n")),
    }
    todo = [c2] + list(p.values())
    # Check 7's finding, in a leg of its own with the anchor's commit after it: bagit.txt and data/ a link to a folder
    # this runner cannot enter (mode 000 while the leg runs), the folder the crash adapter's check runs in.
    locked = os.path.join(t, "kind-locked")
    os.makedirs(locked)
    shut = commit(c1, "bagit-txt-and-data-a-link-to-a-folder-this-runner-cannot-enter",
                  lambda: write("bagit.txt", "BagIt-Version: 1.0\n"), lambda: os.symlink(locked, at("data")))
    saved = (getattr(R, "KEYS", None), getattr(R, "OFFLINE", None))
    R.KEYS, R.OFFLINE = keys["good"], True  # offline: the release stage's install of bagit is skipped, and said so
    try:
        res, err = attempt(R.run_leg, [{"commit": c, "refs": []} for c in todo], "unit test, kinds", sys.executable,
                           origin, say=lambda m: None)
        os.chmod(locked, 0)
        try:
            kept_out = not os.access(locked, os.X_OK)  # a user who enters any folder, as root does, cannot plant it
            res2, err2 = attempt(R.run_leg, [{"commit": c, "refs": []} for c in (shut, c2)],
                                 "unit test, kinds, a folder this runner cannot enter", sys.executable, origin,
                                 say=lambda m: None)
        finally:
            os.chmod(locked, 0o700)
    finally:
        R.KEYS, R.OFFLINE = saved
    wf = "the repository holds no workflow"
    links = "the commit holds no link and no submodule"
    keyset = "anchor/allowed_signers: every key it names is pinned in ci/release-keys.json"
    kept = "anchor/: every anchor manifest a commit it descends from held, it holds too"
    sig = "anchor #1: its signature, with ssh-keygen -Y verify"
    tsr, tsr2 = (f"anchor #1: its timestamp token anchor/predicates-1.{x}, with openssl ts -verify (OpenSSL 3)"
                 for x in ("tsr", "tsr2"))
    tag = "anchor #1: its tag anchor/predicates-1, with git verify-tag"
    stopped = "the checks of this commit, run to their end"
    gone = "anchor/predicates-1.manifest is gone"

    def view(sha, leg="the kinds leg"):
        c = next((x for x in ((res if leg == "the kinds leg" else leg) or {}).get("commits", []) if x["commit"] == sha),
                 {})
        checks = c.get("checks", [])
        return {"stage": c.get("stage"), "result": c.get("result"), "names": [k["name"] for k in checks],
                "failing": sorted(k["name"] for k in checks if k["result"] == "fail"),
                "said": {k["name"]: k["detail"] for k in checks}, "by": {k["name"]: k["result"] for k in checks}}
    base = view(c2)
    prop("kinds: the anchor made here, its manifest signed and its tag made by the pinned key: its signature and tag "
         "checks pass, and its tree holds no link and no submodule, 8 checks", err is None
         and base["by"].get(sig) == "pass" and base["by"].get(tag) == "pass" and base["by"].get(links) == "pass"
         and len(base["names"]) == 8, err or base)

    def holds(name, got, failing, said, same_names=True):
        prop(f"kinds: planted: {name}", err is None and got["failing"] == sorted(failing)
             and (not same_names or got["names"] == base["names"])
             and all(v in got["said"].get(k, "") for k, v in said.items()), err or got)
    plus = set(base["failing"])
    for key, name in (("renamed", "the anchor's manifest renamed anchor/predicates-01.manifest"),
                      ("digit", "the anchor's manifest renamed under the Arabic-Indic digit one, which Python's \\d "
                                "reads as 1")):
        got = view(p[key])
        holds(f"{name}: no anchor's name, so fails the manifests' check alone, naming the manifest, with no anchor "
              f"to check", got, [kept], {kept: gone}, same_names=False)
        prop(f"kinds: planted: {name}: its checks are the workflow's, the links', the manifests' and the key check",
             err is None and got["names"] == [wf, links, kept, keyset], err or got)
    for key, name, what, kind in (("folder", "the anchor's manifest made a folder", "is a folder", None),
                                  ("dangling", "the anchor's manifest made a link that leads nowhere", "is a link",
                                   "a link"),
                                  ("submodule", "the anchor's manifest made a submodule", "is a folder", "a submodule")):
        holds(f"{name}: fails the manifests' check and the signature check, each naming the manifest"
              + (f", and the links' check, naming it as {kind}," if kind else "") + " and nothing else", view(p[key]),
              plus | {kept, sig} | ({links} if kind else set()),
              dict({kept: gone, sig: f"anchor/predicates-1.manifest {what}"},
                   **({links: f"anchor/predicates-1.manifest is {kind}"} if kind else {})))
    for key, name in (("stray", "a stray anchor/predicates-02.manifest beside the manifest"),
                      ("stray removed", "that stray removed again")):
        got = view(p[key])
        prop(f"kinds: planted: {name}: no anchor's name, so the commit is checked as the anchor's own commit is, "
             f"check for check", err is None and [got[k] for k in ("stage", "result", "names", "failing")]
             == [base[k] for k in ("stage", "result", "names", "failing")], err or got)
    via_link = ", and the anchor stage reads no file through a link"
    holds("the signature made a link to a copy of it: fails the signature check and both token checks, which read it, "
          "each naming the link, and the links' check", view(p["sig"]), plus | {sig, tsr, tsr2, links},
          {sig: "anchor/predicates-1.sig is a link" + via_link, tsr: "anchor/predicates-1.sig is a link",
           tsr2: "anchor/predicates-1.sig is a link", links: "anchor/predicates-1.sig is a link"})
    holds("a timestamp token made a link to a copy of it: fails that token's check, naming the link, and the links' "
          "check", view(p["tsr"]), plus | {tsr, links},
          {tsr: "anchor/predicates-1.tsr is a link", links: "anchor/predicates-1.tsr is a link"})
    holds("the chains made a link to a copy of them: fails both token checks, which read them, naming the link, and "
          "the links' check", view(p["ca"]), plus | {tsr, tsr2, links},
          {tsr: "anchor/tsa-ca.pem is a link", tsr2: "anchor/tsa-ca.pem is a link", links: "anchor/tsa-ca.pem is a link"})
    for key, name, said, held in (("signers", "anchor/allowed_signers made a link to a copy of it",
                                   "anchor/allowed_signers is a link", "anchor/allowed_signers is a link"),
                                  ("anchor", "anchor/ made a link to a folder holding anchor/allowed_signers and an "
                                             "anchor manifest, at a commit that held no anchor/",
                                   "anchor/allowed_signers lies under anchor, which is a link", "anchor is a link")):
        got = view(p[key])
        holds(f"{name}: fails the key check and the links' check, at the anchor stage, each naming the link", got,
              [keyset, links], {keyset: said, links: held}, same_names=False)
    # The root's ruling 8 (i): a link or a submodule anywhere in the tree fails, at every stage, whatever the history,
    # named by the one check that reads git ls-tree -r of the commit. Check 6's plants AL1 to AL3 first: on fix round
    # 6's code each passed, two checks, no anchor check run.
    for key, name, at_base, held, stage in (
            ("al1", "anchor/ made a link, inside the commit, to a folder holding anchor #1's manifest, signature, tokens "
                    "and chains and no allowed_signers, at a commit whose history holds no manifest (check 6's AL1)",
             c0, "anchor is a link", "anchor"),
            ("al2", "the same, the signature made by a key the pin lacks (check 6's AL2)", c0, "anchor is a link",
             "anchor"),
            ("al3", "anchor/ replaced by such a link at a commit that held anchor/allowed_signers and no manifest "
                    "(check 6's AL3)", c1, "anchor is a link", "anchor"),
            ("anchor submodule", "anchor/ made a submodule, at a commit whose history holds no manifest", c0,
             "anchor is a submodule", "anchor"),
            ("root link", "a link at the root, at the first commit, which holds no anchor/", c0,
             "notes.txt is a link", "none")):
        got = view(p[key])
        prop(f"kinds: planted: {name}: fails the links' check alone, naming it, at "
             + ("no stage" if stage == "none" else "the anchor stage") + ", the checks the workflow's, the links' and "
             "the manifests'", err is None and got["stage"] == stage and got["failing"] == [links]
             and got["names"] == [wf, links, kept] and held + " (1 in all)" == got["said"].get(links), err or got)
    for key, name, held in (("deep link", "a link three folders down, beside the anchor", "docs/a/b/c/link.txt is a link"),
                            ("deep submodule", "a submodule three folders down, beside the anchor",
                             "x/y/z is a submodule")):
        holds(f"{name}: fails the links' check, naming it, and nothing else the anchor's own commit passes", view(p[key]),
              plus | {links}, {links: held + " (1 in all)"})
    got = view(p["release link"])
    prop("kinds: planted: bagit.txt and a payload file that is a link: at the release stage, the links' check fails, "
         "naming the link", err is None and got["stage"] == "release" and got["result"] == "fail"
         and got["by"].get(links) == "fail" and got["said"].get(links) == "data/x.txt is a link (1 in all)", err or got)
    got = view(p["bagit"])
    prop("kinds: planted: bagit.txt added at the anchor stage, which takes the commit to the release stage with no "
         "data/ to run in: its checks stop on an error, which fails the commit, naming it, and the leg goes on to "
         "every other commit", err is None and got["stage"] == "release" and got["result"] == "fail"
         and got["by"].get(stopped) == "fail" and "No such file or directory" in got["said"].get(stopped, "")
         and len((res or {}).get("commits", [])) == len(todo), err or got)
    got = view(p["data a file"])
    prop("kinds: planted: bagit.txt and data/ a file, the folder the release checks run in: the error that raises is "
         "what the commit holds, not a tool the runner cannot start, so it fails the commit, naming it", err is None
         and got["stage"] == "release" and got["result"] == "fail" and got["by"].get(stopped) == "fail"
         and "Not a directory" in got["said"].get(stopped, ""), err or got)
    got, after = view(shut, res2), view(c2, res2)
    prop("kinds: planted: bagit.txt and data/ a link to a folder this runner cannot enter, the folder the crash "
         "adapter's check runs in (check 7's finding): entering it raises an error what the commit holds causes, not a "
         "tool the runner cannot start, so that commit fails the links' check, naming the link, and the stopped check, "
         "naming the error, and the leg goes on to the anchor's commit after it, which keeps its result check for "
         "check", kept_out and err is None and err2 is None and got["stage"] == "release" and got["result"] == "fail"
         and got["failing"] == sorted([links, stopped]) and got["names"] == [wf, links, kept, keyset, stopped]
         and got["said"].get(links) == "data is a link (1 in all)"
         and "Permission denied" in got["said"].get(stopped, "")
         and [after[k] for k in ("stage", "result", "names", "failing")]
         == [base[k] for k in ("stage", "result", "names", "failing")],
         {"kept out of the folder": kept_out, "error": err2, "plant": got, "the anchor's commit after it": after})

    # Commits holding tools of their own, for the PATH plants of path_tests() (the root's ruling 9 (ii) for P12-26).
    def own(rel, text):
        def fn():
            write(rel, text)
            os.chmod(at(rel), 0o755)
        return fn

    def changed():
        write(man, open(at(man), encoding="utf-8").read() + "# a line the signature does not cover\n")
    own_keygen = commit(c2, "its-own-ssh-keygen-at-the-root-and-the-manifest-changed", own("ssh-keygen", OWN_KEYGEN),
                        changed)
    own_in_tools = commit(c2, "its-own-ssh-keygen-in-tools-and-the-manifest-changed",
                          own("tools/ssh-keygen", OWN_KEYGEN), changed)
    own_openssl = commit(c2, "its-own-openssl-at-the-root", own("openssl", OWN_OPENSSL))
    git("checkout", "-q", "--detach", c2)  # a leg's clone of the origin is at the anchor's commit, which holds no tool
    return {"origin": origin, "anchor": c2, "bagit": p["bagit"], "anchor link": p["anchor"], "own keygen": own_keygen,
            "own keygen in tools": own_in_tools, "own openssl": own_openssl}


def runner_tests(t, keys, kinds):
    """A runner fault is infrastructure, not a verdict (the root's ruling 8 (ii) for P12-26): when the runner cannot
    start a tool it needs, the leg ends with no result written, which the publish step records as infrastructure for
    that leg, so the six-hourly runs check the commit again; an error raised by what the commit holds stays that
    commit's fail (kinds). Each plant runs the anchor made in kinds through run_leg() and main(), on a PATH of a folder
    made here that holds what the leg starts but the tool the plant takes away."""
    tools = os.path.join(t, "runner-tools")
    have = {n: shutil.which(n) for n in ("git", "ssh", "ssh-keygen", "bash", "sh")}

    def path_without(name, how="missing"):
        d = os.path.join(tools, f"{how}-{name}")
        os.makedirs(d)
        for n, where in have.items():
            if n != name and where:
                os.symlink(where, os.path.join(d, n))
        if how == "not executable":
            open(os.path.join(d, name), "w").write("#!/bin/sh\nexit 0\n")
            os.chmod(os.path.join(d, name), 0o644)
        return d
    commits = [{"commit": kinds["anchor"], "refs": ["refs/heads/main"]}]
    saved = (getattr(R, "KEYS", None), dict(os.environ))
    R.KEYS = keys["good"]
    for k in F.TOKEN_VARIABLES:
        os.environ.pop(k, None)
    try:
        # Each fault is named by the operating system's text, not the exception's name (see the bagit.txt plant).
        for name, how, want in (("ssh-keygen", "missing", "No such file or directory"),
                                ("ssh-keygen", "not executable", "Permission denied"),
                                ("git", "missing", "No such file or directory")):
            os.environ["PATH"] = path_without(name, how)
            got, err = attempt(R.run_leg, commits, "unit test, runner", sys.executable, kinds["origin"],
                               say=lambda m: None)
            fault = getattr(R, "RunnerFault", None)
            prop(f"runner: planted: {name} {how} on PATH: the leg ends with no result, the runner's fault named, "
                 f"never a fail of the commit", fault is not None and isinstance(err, fault) and got is None
                 and name in str(err) and want in str(err), err or got)
            out = os.path.join(t, f"runner-leg-{how}-{name}.json")
            os.environ["TODO"] = json.dumps(commits)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc, err = attempt(R.main, ["--commits-env", "TODO", "--leg", "unit test, runner", "--python",
                                           sys.executable, "--source", kinds["origin"], "--out", out])
            prop(f"runner: planted: {name} {how} on PATH: ci/run_checks.py exits 2, naming the runner's fault, and "
                 f"writes no result", err is None and rc == 2 and not os.path.exists(out) and name in buf.getvalue()
                 and "the runner's fault" in buf.getvalue(), err or (rc, os.path.exists(out), buf.getvalue()[-400:]))
        # OpenSSL's candidates: one the runner cannot start is passed over, as one that is not OpenSSL 3 is.
        os.environ["PATH"] = path_without("openssl")
        os.environ["OPENSSL"] = os.path.join(t, "no-such-openssl")
        got, err = attempt(R.openssl3, R.leg_env(sys.executable, os.path.join(t, "runner-openssl")), False)
        prop("runner: planted: OPENSSL naming a path that holds nothing: that candidate is passed over, and an OpenSSL "
             "3 is found or its absence said, never a fault that ends the leg", err is None and got is not None
             and (got[0] is None or got[1].startswith("OpenSSL 3")), err or got)
        # A bare name that no entry of the leg's PATH holds, which openssl3() looks up there and finds nothing for: that
        # candidate is passed over too (the round 9 check's K8), never started as nothing, an error that would stop the
        # commit's checks.
        os.environ["OPENSSL"] = "no-such-openssl-made-here"
        got, err = attempt(R.openssl3, R.leg_env(sys.executable, os.path.join(t, "runner-openssl-bare")), False)
        prop("runner: planted: OPENSSL a bare name that no entry of PATH holds: that candidate is passed over, and an "
             "OpenSSL 3 is found or its absence said, never an error that stops the commit's checks", err is None
             and got is not None and (got[0] is None or got[1].startswith("OpenSSL 3")), err or got)
    finally:
        R.KEYS = saved[0]
        os.environ.clear()
        os.environ.update(saved[1])
    # Where the line lies (check 7's finding): a command runs in the commit's checkout or a folder of it. An error that
    # names that folder, one Python could not enter to start the command, is what the commit holds, raised as it is;
    # an error that names the tool is the runner's. A checkout made here: data/ a link to a folder of mode 000.
    tree, locked = os.path.join(t, "runner-tree"), os.path.join(t, "runner-locked")
    os.makedirs(tree)
    os.makedirs(locked)
    os.symlink(locked, os.path.join(tree, "data"))
    fault = getattr(R, "RunnerFault", None)
    os.chmod(locked, 0)
    try:
        kept_out = not os.access(locked, os.X_OK)  # a user who enters any folder, as root does, cannot plant it
        for name, cmd, cwd, want in (
                ("a command run in data/, a link to a folder this runner cannot enter: the PermissionError is raised "
                 "as it is, naming the folder, never RunnerFault", ["true"], os.path.join(tree, "data"), "folder"),
                ("the same with its tool missing too: the folder's error comes first, raised as it is",
                 ["no-such-tool-made-here"], os.path.join(tree, "data"), "folder"),
                ("a tool missing, run in a folder of the checkout this runner can enter: RunnerFault, naming the tool",
                 ["no-such-tool-made-here"], tree, "tool")):
            got, err = (attempt(R.start, cmd, cwd, capture_output=True, stdin=subprocess.DEVNULL)
                        if hasattr(R, "start") else (None, "no start()"))  # code before fix round 7 has none
            ok = (isinstance(err, PermissionError) and getattr(err, "filename", None) == cwd if want == "folder" else
                  fault is not None and isinstance(err, fault) and "no-such-tool-made-here" in str(err))
            prop(f"runner: start(): planted: {name}", kept_out and ok,
                 {"kept out of the folder": kept_out, "raised": repr(err), "returned": got})
        got, err = attempt(R.result_schema, tree, F.git_env())
        prop("runner: the result schema's check, planted: data/ a link to a folder this runner cannot enter: the check "
             "fails, naming the error, and raises nothing", kept_out and err is None and got is not None
             and got["result"] == "fail" and "Permission denied" in got["detail"],
             {"kept out of the folder": kept_out, "raised": repr(err), "returned": got})
    finally:
        os.chmod(locked, 0o700)
    # start()'s test that the folder a command runs in is a folder (the root's ruling 9 (iv) for P12-26), held by a
    # stand-in for a Python whose error entering a missing folder carries no filename, which the test of the error's
    # name cannot read as the commit's: the error is raised as it is, so the commit fails, naming it, and the leg goes
    # on; without the folder test it would be RunnerFault, and the leg would end.
    saved = (R.subprocess, getattr(R, "KEYS", None), getattr(R, "OFFLINE", None))
    R.subprocess, R.KEYS, R.OFFLINE = NoFilename(), keys["good"], True
    try:
        nowhere = os.path.join(t, "runner-no-such-folder")
        got, err = attempt(R.start, ["true"], nowhere, capture_output=True, stdin=subprocess.DEVNULL)
        prop("runner: start(): planted: a stand-in for a Python whose error entering a missing folder carries no "
             "filename: the error is raised as it is, never RunnerFault", isinstance(err, OSError)
             and err.errno == errno.ENOENT and getattr(err, "filename", None) is None
             and not (fault is not None and isinstance(err, fault)),
             {"raised": repr(err), "returned": got})
        res, err = attempt(R.run_leg, [{"commit": kinds["bagit"], "refs": []}, {"commit": kinds["anchor"], "refs": []}],
                           "unit test, a Python whose folder error names no file", sys.executable, kinds["origin"],
                           say=lambda m: None)
    finally:
        R.subprocess, R.KEYS, R.OFFLINE = saved
    cs = {c["commit"]: c for c in (res or {}).get("commits", [])}
    b, a = cs.get(kinds["bagit"], {}), cs.get(kinds["anchor"], {})
    stopped = {k["name"]: k for k in b.get("checks", [])}.get("the checks of this commit, run to their end", {})
    prop("runner: planted: under that stand-in, bagit.txt added with no data/ to run in: the commit fails, its checks "
         "stopping on the error, named, and the leg goes on to the anchor's commit, 8 checks", err is None
         and b.get("result") == "fail" and stopped.get("result") == "fail"
         and "No such file or directory" in stopped.get("detail", "") and a.get("stage") == "anchor"
         and len(a.get("checks", [])) == 8, err or {"bagit.txt": b, "the anchor's commit": a})
    # The leg that never arrived, as the publish step records it beside two that passed, and the next run's detect.
    passing = []
    for i in range(2):
        doc = {"format": R.LEG_FORMAT, "leg": {"name": f"leg {i}"}, "result": "pass",
               "commits": [{"commit": kinds["anchor"], "refs": ["refs/heads/main"], "stage": "anchor", "result": "pass",
                            "checks": [{"name": "a check", "result": "pass", "detail": "", "seconds": 0}]}]}
        path = os.path.join(t, f"runner-pass-{i}.json")
        json.dump(doc, open(path, "w"))
        passing.append(P.read_leg(path))
    missing = P.read_leg(os.path.join(t, "runner-leg-missing-ssh-keygen.json"))
    recs = P.pack_records(commits, DATE, passing + [missing], 3, "Thu, 15 Oct 2026 08:00:00 GMT",
                          {"id": "1", "attempt": "1", "event": "schedule", "url": "u"})
    rec = recs[0][1]
    index = {"records": [{"workflow": "pack-checks", "commit": kinds["anchor"], "refs": ["refs/heads/main"],
                          "result": rec["result"]}]}
    again = (kinds["anchor"], ("refs/heads/main",)) not in D.recorded(index)
    prop("runner: that leg's missing result is recorded as infrastructure beside two legs that passed, and the next "
         "six-hourly run checks the commit again", missing is None and rec["result"] == "infrastructure"
         and [e["result"] for e in rec["legs"]] == ["pass", "pass", "infrastructure"] and again,
         {"result": rec["result"], "legs": [e["result"] for e in rec["legs"]], "checked again": again})


def leg_view(res, sha):
    """(stage, result, [(check, result)]) of `sha` in a leg's result, or None when the leg holds no such commit."""
    c = next((x for x in (res or {}).get("commits", []) if x["commit"] == sha), None)
    return None if c is None else (c["stage"], c["result"], [(k["name"], k["result"]) for k in c["checks"]])


def path_tests(t, keys, kinds):
    """The runner's PATH (the root's ruling 9 (ii) for P12-26): a leg runs no program from an empty or relative PATH
    entry. Each plant is a commit of the origin made in kinds, checked through run_leg() or main() on the runner's own
    PATH with one entry put first: a commit holding its own executable ssh-keygen, which says every signature is good,
    beside a changed manifest, fails its signature check with '.', an empty entry or tools/ (a folder of the commit)
    first; with '.' first on a PATH that holds no other ssh-keygen, the leg ends on RunnerFault; --python python3 is
    found on an absolute entry, never in the folder the runner runs from; and OPENSSL naming ./openssl starts that file
    by its absolute path, never the commit's own openssl by the same name."""
    sig = "anchor #1: its signature, with ssh-keygen -Y verify"
    tsr, tsr2 = (f"anchor #1: its timestamp token anchor/predicates-1.{x}, with openssl ts -verify (OpenSSL 3)"
                 for x in ("tsr", "tsr2"))
    fault = getattr(R, "RunnerFault", None)
    saved = (getattr(R, "KEYS", None), dict(os.environ), os.getcwd())
    runner_path = saved[1].get("PATH", os.defpath)
    R.KEYS = keys["good"]
    for k in F.TOKEN_VARIABLES + ("OPENSSL",):
        os.environ.pop(k, None)

    def leg(sha, name="unit test, path"):
        return attempt(R.run_leg, [{"commit": sha, "refs": []}], name, sys.executable, kinds["origin"],
                       say=lambda m: None)
    try:
        base, err = leg(kinds["anchor"])
        base = leg_view(base, kinds["anchor"])
        base_failing = sorted(n for n, r in (base or (None, None, []))[2] if r == "fail")
        prop("path: the anchor's commit on the runner's own PATH: its signature check passes", err is None
             and base is not None and dict(base[2]).get(sig) == "pass", err or base)
        for name, sha, first in (("'.'", kinds["own keygen"], "."), ("an empty entry", kinds["own keygen"], ""),
                                 ("tools, a folder of the commit,", kinds["own keygen in tools"], "tools")):
            os.environ["PATH"] = first + os.pathsep + runner_path
            got, err = leg(sha)
            os.environ["PATH"] = runner_path
            c = next((x for x in (got or {}).get("commits", []) if x["commit"] == sha), {})
            by = {k["name"]: k for k in c.get("checks", [])}
            failing = sorted(n for n, k in by.items() if k["result"] == "fail")
            prop(f"path: planted: the commit's own executable ssh-keygen beside a changed manifest, {name} first on "
                 f"PATH: the signature check starts the runner's ssh-keygen, which refuses the manifest, and fails, "
                 f"and nothing else fails that the anchor's commit passes", err is None
                 and by.get(sig, {}).get("result") == "fail"
                 and "an ssh-keygen the commit holds" not in by.get(sig, {}).get("detail", "")
                 and failing == sorted(set(base_failing) | {sig}), err or c)
        # The only ssh-keygen behind a dropped entry: a tool the runner cannot start, infrastructure, never a pass.
        tools = os.path.join(t, "path-tools-no-ssh-keygen")
        os.makedirs(tools)
        for n in ("git", "ssh", "bash", "sh"):
            where = shutil.which(n, path=runner_path)
            if where:
                os.symlink(where, os.path.join(tools, n))
        os.environ["PATH"] = "." + os.pathsep + tools
        got, err = leg(kinds["own keygen"])
        out = os.path.join(t, "path-leg-dot-no-ssh-keygen.json")
        os.environ["TODO"] = json.dumps([{"commit": kinds["own keygen"], "refs": ["refs/heads/main"]}])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc, err2 = attempt(R.main, ["--commits-env", "TODO", "--leg", "unit test, path", "--python", sys.executable,
                                        "--source", kinds["origin"], "--out", out])
        os.environ["PATH"] = runner_path
        prop("path: planted: '.' first on a PATH that holds no other ssh-keygen, the commit holding its own: the leg "
             "ends on RunnerFault, naming ssh-keygen, never a pass", fault is not None and isinstance(err, fault)
             and got is None and "ssh-keygen" in str(err), err or got)
        prop("path: planted: the same through ci/run_checks.py: exit 2, naming the runner's fault, no result written",
             err2 is None and rc == 2 and not os.path.exists(out) and "the runner's fault" in buf.getvalue(),
             err2 or (rc, os.path.exists(out), buf.getvalue()[-400:]))
        passing = []
        for i in range(2):
            path = os.path.join(t, f"path-pass-{i}.json")
            json.dump({"format": R.LEG_FORMAT, "leg": {"name": f"leg {i}"}, "result": "pass", "commits": [
                {"commit": kinds["own keygen"], "refs": ["refs/heads/main"], "stage": "anchor", "result": "pass",
                 "checks": [{"name": "a check", "result": "pass", "detail": "", "seconds": 0}]}]}, open(path, "w"))
            passing.append(P.read_leg(path))
        recs = P.pack_records([{"commit": kinds["own keygen"], "refs": ["refs/heads/main"]}], DATE,
                              passing + [P.read_leg(out)], 3, "Thu, 15 Oct 2026 08:00:00 GMT",
                              {"id": "1", "attempt": "1", "event": "schedule", "url": "u"})
        prop("path: that leg's missing result is recorded as infrastructure beside two legs that passed, never a pass",
             recs[0][1]["result"] == "infrastructure"
             and [e["result"] for e in recs[0][1]["legs"]] == ["pass", "pass", "infrastructure"], recs[0][1]["result"])
        # TMPDIR naming '.', which tempfile keeps relative in the name of the leg's own folder on Python 3.11 and older.
        dot = os.path.join(t, "path-tmpdir-dot")
        os.makedirs(dot)
        saved_tempdir = tempfile.tempdir
        tempfile.tempdir = "."
        os.chdir(dot)
        try:
            got, err = leg(kinds["anchor"])
        finally:
            tempfile.tempdir = saved_tempdir
            os.chdir(saved[2])
        view = leg_view(got, kinds["anchor"])
        prop("path: planted: TMPDIR naming '.', which tempfile keeps relative in the name of the leg's own folder on "
             "Python 3.11 and older: the leg names its folder by its absolute path, and the anchor's commit keeps its "
             "record, check for check, its signature check passing", err is None and view == base
             and dict((view or (None, None, []))[2]).get(sig) == "pass", err or {"with": view, "without": base})
        # --python python3, with '.' first and a python3 in the folder the runner runs ci/run_checks.py from.
        here = os.path.join(t, "path-runner-folder")
        marker = os.path.join(t, "path-the-runner-folder-python3-ran")
        pybin = os.path.join(t, "path-python-bin")
        os.makedirs(here)
        os.makedirs(pybin)
        os.symlink(sys.executable, os.path.join(pybin, "python3"))
        spy = os.path.join(here, "python3")
        open(spy, "w").write(f"#!/bin/sh\necho ran >> {shlex.quote(marker)}\nexec {shlex.quote(sys.executable)} "
                             f'"$@"\n')
        os.chmod(spy, 0o755)
        os.environ["PATH"] = "." + os.pathsep + pybin + os.pathsep + runner_path
        os.environ["TODO"] = json.dumps([{"commit": kinds["anchor"], "refs": []}])
        out = os.path.join(t, "path-leg-python.json")
        os.chdir(here)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc, err = attempt(R.main, ["--commits-env", "TODO", "--leg", "unit test, path", "--python", "python3",
                                           "--source", kinds["origin"], "--checks", "workflow", "--out", out])
        finally:
            os.chdir(saved[2])
            os.environ["PATH"] = runner_path
        doc = json.load(open(out)) if os.path.exists(out) else {}
        prop("path: planted: --python python3 with '.' first on PATH and a python3 in the folder the runner runs from: "
             "the leg's python is the one an absolute entry names, never that folder's", err is None and rc == 0
             and not os.path.exists(marker) and doc.get("leg", {}).get("python") == f"Python {platform.python_version()}",
             err or {"exit": rc, "that folder's python3 ran": os.path.exists(marker), "leg": doc.get("leg")})
        # --python python3 where no absolute entry of PATH holds a python3 and the folder the runner runs from does,
        # behind '.' or behind no entry at all: a python the runner cannot start, never that folder's (the round 9
        # check's K6, a python named as it is when no absolute entry holds it).
        nopy = os.path.join(t, "path-tools-no-python3")
        os.makedirs(nopy)
        for n in ("git", "ssh", "ssh-keygen", "bash", "sh"):
            where = shutil.which(n, path=runner_path)
            if where:
                os.symlink(where, os.path.join(nopy, n))
        os.environ["TODO"] = json.dumps([{"commit": kinds["anchor"], "refs": []}])
        for i, (how, path) in enumerate((("'.' first", "." + os.pathsep + nopy), ("no relative entry", nopy))):
            folder = os.path.join(t, f"path-runner-folder-no-python3-{i}")
            ran = os.path.join(t, f"path-the-runner-folder-python3-ran-{i}")
            os.makedirs(folder)
            open(os.path.join(folder, "python3"), "w").write(
                f"#!/bin/sh\necho ran >> {shlex.quote(ran)}\nexec {shlex.quote(sys.executable)} \"$@\"\n")
            os.chmod(os.path.join(folder, "python3"), 0o755)
            out = os.path.join(t, f"path-leg-no-python3-{i}.json")
            buf = io.StringIO()
            os.environ["PATH"] = path
            os.chdir(folder)
            try:
                with contextlib.redirect_stdout(buf):
                    rc, err = attempt(R.main, ["--commits-env", "TODO", "--leg", "unit test, path", "--python",
                                               "python3", "--source", kinds["origin"], "--checks", "workflow", "--out",
                                               out])
            finally:
                os.chdir(saved[2])
                os.environ["PATH"] = runner_path
            prop(f"path: planted: --python python3 on a PATH whose absolute entries hold no python3, {how}, and a "
                 f"python3 in the folder the runner runs from: the runner cannot start the leg's python, exit 2 with no "
                 f"result written, and that folder's python3 never starts", err is None and rc == 2
                 and not os.path.exists(out) and not os.path.exists(ran)
                 and "the runner cannot start python3" in buf.getvalue() and "the runner's fault" in buf.getvalue(),
                 err or {"exit": rc, "written": os.path.exists(out), "that folder's python3 ran": os.path.exists(ran),
                         "said": buf.getvalue()[-400:]})
        # OPENSSL naming ./openssl, a stand-in OpenSSL 3 in the folder the runner runs from, and the commit's own.
        stand = os.path.join(t, "path-openssl-folder")
        os.makedirs(stand)
        open(os.path.join(stand, "openssl"), "w").write(RUNNER_OPENSSL)
        os.chmod(os.path.join(stand, "openssl"), 0o755)
        os.environ["OPENSSL"] = os.path.join(".", "openssl")
        os.chdir(stand)
        try:
            got, err = leg(kinds["own openssl"])
            named, err2 = attempt(R.openssl3, R.leg_env(sys.executable, os.path.join(t, "path-openssl-leg")), False)
        finally:
            os.chdir(saved[2])
            os.environ.pop("OPENSSL", None)
        c = next((x for x in (got or {}).get("commits", []) if x["commit"] == kinds["own openssl"]), {})
        by = {k["name"]: k for k in c.get("checks", [])}
        prop("path: planted: OPENSSL naming ./openssl, a stand-in OpenSSL 3 in the folder the runner runs from, the "
             "commit holding an openssl of its own that says every token verifies: openssl3() names that stand-in by "
             "its absolute path, and both timestamp checks start it and fail, never the commit's", err is None
             and err2 is None and named is not None and os.path.isabs(named[0])
             and os.path.realpath(named[0]) == os.path.realpath(os.path.join(stand, "openssl"))
             and named[1] == "OpenSSL 3.0.0 (a stand-in the runner names)"
             and all(by.get(x, {}).get("result") == "fail" and "the openssl the runner names" in by[x]["detail"]
                     for x in (tsr, tsr2)), err or err2 or {"openssl3()": named, "checks": by})
    finally:
        R.KEYS = saved[0]
        os.environ.clear()
        os.environ.update(saved[1])
        os.chdir(saved[2])


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
        git, probe = os.path.join(root, "bin", "git"), os.path.join(root, "probe")
        subprocess.run([git, "init", "-q", probe], env=env, capture_output=True, stdin=subprocess.DEVNULL)
        said = subprocess.run([git, "-C", probe, "check-attr", "text", "--", "f"], env=env, capture_output=True,
                              text=True, stdin=subprocess.DEVNULL).stdout.strip()
        held = [rel for rel in template or {} if os.path.isfile(os.path.join(probe, ".git", *rel.split("/")))]
        if (attributes is None or said == "f: text: set") and len(held) == len(template or {}):
            return os.path.join(root, "bin"), None
        tried.append(f"a repository a copy of {real} makes reads {said!r} and holds {held} of {sorted(template or {})}")
    return None, "no git here reads the files beside it that it is given: " + ("; ".join(tried) or "no git found")


def config_tests(t, keys, kinds):
    """The runner's git configuration (the root's ruling 9 (iii) for P12-26): no git command of a leg reads it. Each
    plant puts one configuration where git would read it, checks the anchor's commit through run_leg(), and must leave
    its record, check for check, as it is with none, the tag check passing: a global configuration (HOME's .gitconfig)
    naming a gpg.ssh.program that does not exist, the same in the XDG configuration, in a file GIT_CONFIG_GLOBAL names
    and in GIT_CONFIG_PARAMETERS, and in the system configuration of a git stand-in; a global configuration sending the
    origin's address to another repository, whose anchor tag a key the pin lacks signed; and one with core.symlinks
    false, under which a checkout writes a link as a file, on the commit whose anchor/ is a link. And the runner's
    attributes files, which git reads whatever configuration it reads (the round 9 check's finding 1): one holding
    `* text eol=crlf`, which turns every file's line endings to CRLF in a checkout, as the global attributes file in
    HOME (.config/git/attributes) and in the XDG folder, as the system one of a git first on PATH that reads it, and
    as an info/attributes among that git's templates, which it copies into each repository it makes; and a
    post-checkout hook among those templates, which changes the anchor's manifest (runner_git()). And two GIT_
    variables of the runner's that name no configuration (the round 9 check's K13): GIT_DIR naming another clone of
    the origin, and GIT_TEMPLATE_DIR naming a folder whose post-checkout hook changes the anchor's manifest."""
    tag = "anchor #1: its tag anchor/predicates-1, with git verify-tag"
    origin, anchor, link_commit = kinds["origin"], kinds["anchor"], kinds["anchor link"]
    saved = (getattr(R, "KEYS", None), getattr(R, "OFFLINE", None), dict(os.environ))
    R.KEYS, R.OFFLINE = keys["good"], True
    for k in F.TOKEN_VARIABLES + ("XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_PARAMETERS"):
        os.environ.pop(k, None)
    env = F.git_env()

    def git(repo, *a):
        return subprocess.run(["git", "-C", repo, "-c", "user.name=unit test", "-c", "user.email=unit-test@example.invalid",
                               "-c", "commit.gpgsign=false", *a], env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL)
    other = os.path.join(t, "config-other")
    subprocess.run(["git", "clone", "-q", origin, other], env=env, capture_output=True, stdin=subprocess.DEVNULL)
    git(other, "-c", "gpg.format=ssh", "-c", f"user.signingkey={keys['other']['path']}", "tag", "-s", "-f", "-m",
        "anchor #1, signed by a key the pin lacks", "anchor/predicates-1", anchor)
    missing_program = '[gpg "ssh"]\n\tprogram = /nonexistent/ssh-keygen\n'

    def file_of(name, text):
        p = os.path.join(t, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
        return p
    empty_home = os.path.join(t, "config-home-empty")
    os.makedirs(empty_home)
    standin = os.path.join(t, "config-git-standin")
    os.makedirs(standin)
    system = file_of("config-system-gitconfig", missing_program)
    open(os.path.join(standin, "git"), "w").write(f"#!/bin/sh\nGIT_CONFIG_SYSTEM={shlex.quote(system)} exec "
                                                  f"{shlex.quote(shutil.which('git'))} \"$@\"\n")
    os.chmod(os.path.join(standin, "git"), 0o755)
    crlf = "* text eol=crlf\n"
    hook = ("#!/bin/sh\nif [ -f anchor/predicates-1.manifest ]; then\n"
            "  echo '# a line a hook of the runner wrote' >> anchor/predicates-1.manifest\nfi\n")
    hooks = os.path.join(t, "config-template", "hooks")
    os.makedirs(hooks)
    open(os.path.join(hooks, "post-checkout"), "w").write(hook)
    os.chmod(os.path.join(hooks, "post-checkout"), 0o755)

    def first_on_path(name, **files):
        """PATH with a git of the runner's own first (runner_git()), or why it cannot be made here."""
        got, why = runner_git(t, f"config-git-{name}", **files)
        return {"PATH": got + os.pathsep + saved[2].get("PATH", os.defpath)} if got else why
    plants = (
        ("a global configuration, HOME's .gitconfig, naming a gpg.ssh.program that does not exist", anchor,
         {"HOME": os.path.dirname(file_of("config-home-program/.gitconfig", missing_program))}),
        ("the same in the XDG configuration, $XDG_CONFIG_HOME/git/config, with no .gitconfig in HOME", anchor,
         {"HOME": empty_home, "XDG_CONFIG_HOME": os.path.dirname(os.path.dirname(
             file_of("config-xdg/git/config", missing_program)))}),
        ("the same in a file the runner's environment names as GIT_CONFIG_GLOBAL", anchor,
         {"GIT_CONFIG_GLOBAL": file_of("config-global-file", missing_program)}),
        ("the same in GIT_CONFIG_PARAMETERS, as git -c passes a setting on", anchor,
         {"GIT_CONFIG_PARAMETERS": "'gpg.ssh.program'='/nonexistent/ssh-keygen'"}),
        ("the same in the system configuration of a git stand-in, which sets GIT_CONFIG_SYSTEM before it starts git",
         anchor, {"PATH": standin + os.pathsep + saved[2].get("PATH", os.defpath)}),
        ("a global configuration sending the origin's address to another repository, whose anchor tag a key the pin "
         "lacks signed", anchor, {"HOME": os.path.dirname(file_of("config-home-url/.gitconfig",
                                                                    f'[url "{other}"]\n\tinsteadOf = {origin}\n'))}),
        ("a global configuration with core.symlinks false, under which a checkout writes a link as a file, on the "
         "commit whose anchor/ is a link", link_commit,
         {"HOME": os.path.dirname(file_of("config-home-symlinks/.gitconfig", "[core]\n\tsymlinks = false\n"))}),
        ("a global attributes file, HOME's .config/git/attributes, holding * text eol=crlf, which turns every file's "
         "line endings to CRLF in a checkout", anchor,
         {"HOME": os.path.dirname(os.path.dirname(os.path.dirname(
             file_of("config-home-attributes/.config/git/attributes", crlf))))}),
        ("the same in the XDG folder, $XDG_CONFIG_HOME/git/attributes, with no attributes file in HOME", anchor,
         {"HOME": empty_home, "XDG_CONFIG_HOME": os.path.dirname(os.path.dirname(
             file_of("config-xdg-attributes/git/attributes", crlf)))}),
        ("the same as the system attributes file of a git first on PATH that reads it", anchor,
         first_on_path("system-attributes", attributes=crlf)),
        ("the same as an info/attributes among the templates of a git first on PATH, which it copies into each "
         "repository it makes", anchor, first_on_path("template-attributes", template={"info/attributes": (crlf, 0o644)})),
        ("a post-checkout hook among the templates of a git first on PATH, which changes the anchor's manifest", anchor,
         first_on_path("template-hook", template={"hooks/post-checkout": (hook, 0o755)})),
        ("GIT_DIR naming another clone of the origin", anchor, {"GIT_DIR": os.path.join(other, ".git")}),
        ("GIT_TEMPLATE_DIR naming a folder whose post-checkout hook changes the anchor's manifest", anchor,
         {"GIT_TEMPLATE_DIR": os.path.dirname(hooks)}))
    try:
        base = {}
        for sha in (anchor, link_commit):
            got, err = attempt(R.run_leg, [{"commit": sha, "refs": []}], "unit test, config", sys.executable, origin,
                               say=lambda m: None)
            base[sha] = leg_view(got, sha)
        prop("config: the anchor's commit with no planted configuration: its tag check passes", err is None
             and dict(base[anchor][2]).get(tag) == "pass", base[anchor])
        for name, sha, plant in plants:
            said = (f"config: planted: {name}: the commit's record is as it is with none, check for check"
                    + (", its tag check passing" if sha == anchor else ""))
            if isinstance(plant, str):  # a plant this machine cannot make fails, naming why
                prop(said, False, plant)
                continue
            os.environ.update(plant)
            try:
                got, err = attempt(R.run_leg, [{"commit": sha, "refs": []}], "unit test, config", sys.executable,
                                   origin, say=lambda m: None)
            finally:
                os.environ.clear()
                os.environ.update(saved[2])
                for k in F.TOKEN_VARIABLES + ("XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_PARAMETERS"):
                    os.environ.pop(k, None)
            view = leg_view(got, sha)
            prop(said, err is None and view == base[sha] and (sha != anchor or dict(view[2]).get(tag) == "pass"),
                 err or {"with": view, "without": base[sha]})
    finally:
        R.KEYS, R.OFFLINE = saved[0], saved[1]
        os.environ.clear()
        os.environ.update(saved[2])


def blocks_tests(t):
    page = "intro\n```\necho one\n```\ntext\n```\nprintf 'two'\nls\n```\n"
    found = R.fenced(page)
    prop("blocks: each fenced block is read with the line of its fence",
         found == [(2, "echo one\n"), (6, "printf 'two'\nls\n")], found)
    cls = R.load_blocks()
    prop("blocks: ci/verifying-blocks.json keys every block by the sha256 of its text, 64 hex each",
         all(len(k) == 64 for k in cls) and len(cls) >= 14)
    w = os.path.join(t, "wt", "data", "witness")
    os.makedirs(w)
    json.dump({"format": "falden-witness-attest/1", "phase": "live", "events": [],
               "dispatches": [{"event_id": "sdlc-1.7", "dispatch_id": "sdlc-1.7.d1", "ref": "refs/heads/main",
                               "outcome": "attested", "attested": {"bundle": "attest/x/b.sigstore.json", "digest": "f" * 64},
                               "acquisitions": [{"bundle": "attest/x/b.sigstore.json", "trusted_root": "trusted_root/r.jsonl"}]}]},
              open(os.path.join(w, "attest.json"), "w"))
    open(os.path.join(w, "journal.jsonl"), "w").write(json.dumps({"format": "falden-journal/1", "lineage": "sdlc-1"}) + "\n"
                                                      + json.dumps({"seq": 7, "repo": "falden-fixtures/x", "kind": "push"}) + "\n")
    got, problems = R.bundles(os.path.join(t, "wt"))
    prop("blocks: an attested dispatch's placeholders come from attest.json and the journal's event ids",
         not problems and got == [{"<bundle>": "witness/attest/x/b.sigstore.json", "<owner>/<repository>": "falden-fixtures/x",
                                   "<ref>": "refs/heads/main", "<digest>": "f" * 64,
                                   "<trusted root file>": "witness/trusted_root/r.jsonl"}], (got, problems))
    open(os.path.join(w, "journal.jsonl"), "w").write(json.dumps({"lineage": "sdlc-1"}) + "\n")
    got, problems = R.bundles(os.path.join(t, "wt"))
    prop("blocks: planted: a dispatch whose event the journal does not name is refused, naming what it lacks",
         got == [] and any("<owner>/<repository>" in p for p in problems), problems)


def legs(results):
    out = []
    for i, r in enumerate(results):
        out.append({"format": R.LEG_FORMAT, "leg": {"name": f"leg {i}", "python": "Python 3.9.6"}, "result": r,
                    "commits": [{"commit": SHA["main"], "refs": ["refs/heads/main"], "stage": "anchor", "result": r,
                                 "checks": [{"name": "a check", "result": r, "detail": "x", "seconds": 1.0}]}]})
    return out


def publish_tests(t):
    root = os.path.join(t, "status")
    os.makedirs(os.path.join(root, "records"))
    shutil.copy(os.path.join(ROOT, "README.md"), os.path.join(root, "README.md"))
    json.dump({"format": P.RECORD_FORMAT, "records": []}, open(os.path.join(root, "records", "index.json"), "w"))
    run = {"id": "1", "attempt": "1", "event": "schedule", "url": "u"}
    commits = [{"commit": SHA["main"], "refs": ["refs/heads/main"]}]
    for n, (time, results) in enumerate((("Wed, 14 Oct 2026 08:00:00 GMT", ["pass", "pass", "pass"]),
                                         ("Wed, 14 Oct 2026 14:00:00 GMT", ["pass", "fail", "infrastructure"]))):
        d = os.path.join(t, f"legs-{n}")
        for i, leg in enumerate(legs(results)):
            os.makedirs(os.path.join(d, f"leg-{i}"))
            json.dump(leg, open(os.path.join(d, f"leg-{i}", "leg.json"), "w"))
        recs = P.pack_records(commits, DATE, [P.read_leg(p) for p in sorted(
            os.path.join(d, x, "leg.json") for x in os.listdir(d))], 3, time, run)
        P.write(root, recs)
    index = json.load(open(os.path.join(root, "records", "index.json")))
    readme = open(os.path.join(root, "README.md")).read()
    first = json.load(open(os.path.join(root, index["records"][0]["path"])))
    prop("publish: one record for each commit, its time the forge's Date, its result the worst leg's",
         [r["result"] for r in index["records"]] == ["pass", "fail"] and first["time"] == "Wed, 14 Oct 2026 08:00:00 GMT"
         and first["format"] == P.RECORD_FORMAT and len(first["legs"]) == 3, index)
    rows = [ln for ln in readme.split(P.BEGIN)[1].split(P.END)[0].splitlines() if ln.startswith("| Wed")]
    prop("publish: the README's table lists the records newest first", len(rows) == 2 and "14:00:00" in rows[0], rows)
    d = os.path.join(t, "legs-missing")
    os.makedirs(os.path.join(d, "leg-0"))
    json.dump(legs(["pass"])[0], open(os.path.join(d, "leg-0", "leg.json"), "w"))
    os.makedirs(os.path.join(d, "leg-1"))
    open(os.path.join(d, "leg-1", "leg.json"), "w").write('{"format": "something else"}')
    recs = P.pack_records(commits, DATE, [P.read_leg(os.path.join(d, x, "leg.json")) for x in ("leg-0", "leg-1")], 3,
                          "Thu, 15 Oct 2026 08:00:00 GMT", run)
    rec = recs[0][1]
    prop("publish: a leg that is not falden-status-leg/1, and one that never arrived, are recorded as legs with no "
         "readable result, infrastructure", P.read_leg(os.path.join(d, "leg-1", "leg.json")) is None
         and [e["result"] for e in rec["legs"]] == ["pass", "infrastructure", "infrastructure"]
         and rec["result"] == "infrastructure", [e["result"] for e in rec["legs"]])
    odd = [{"commit": SHA["other"], "refs": ["refs/tags/x|y](http://evil)`<b>"]}]
    recs = P.pack_records(odd, DATE, [P.read_leg(os.path.join(d, "leg-0", "leg.json"))], 1, "Fri, 16 Oct 2026 08:00:00 GMT", run)
    P.write(root, recs)
    readme = open(os.path.join(root, "README.md")).read()
    prop("publish: a ref holding Markdown reaches the table escaped: no added column, link or tag",
         "x_y_(http://evil)__b_" in readme and "](http://evil)" not in readme and "<b>" not in readme)
    bad = [("records/pack-checks/x.json", dict(rec, legs=[dict(rec["legs"][0], tools={"x": "ghp_" + "A" * 36})]))]
    before = sorted(os.listdir(os.path.join(root, "records", "pack-checks")))
    try:
        P.write(root, bad)
        prop("publish: planted: a record holding a token's shape is refused", False)
    except P.Refused as e:
        prop("publish: planted: a record holding a token's shape is refused, nothing written",
             "token's shape" in str(e) and sorted(os.listdir(os.path.join(root, "records", "pack-checks"))) == before)
    try:
        P.write(root, [(index["records"][0]["path"], rec)])
        prop("publish: planted: a record path already taken is refused", False)
    except P.Refused as e:
        prop("publish: planted: a record path already taken is refused", "already recorded" in str(e))


def canary_tests(t):
    sent = []
    fg = F.Forge(transport=recorded({}, sent))
    res = C.run_canary(fg, lambda url: [(SHA["main"], "refs/heads/main"), (SHA["tagobj"], "refs/tags/v0.9.0"),
                                         (SHA["tag"], "refs/tags/anchor/predicates-1")], "unused", t, say=lambda m: None)
    prop("canary: no release tag from 1.0 on: nothing checked, nothing read, nothing published",
         res["publish"] is False and res["checks"] == [] and sent == [], res)
    refs = [(SHA["tagobj"], "refs/tags/v1.0.0"), (SHA["main"], "refs/tags/v1.0.0^{}"), (SHA["other"], "refs/tags/v1.10.0"),
            (SHA["tag"], "refs/tags/v1.9.3"), (SHA["pr"], "refs/tags/v2.0.0-rc1")]
    prop("canary: the newest release tag is found among several, by version, not by text",
         C.newest_release(refs) == ("v1.10.0", SHA["other"]), C.newest_release(refs))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("../outside.txt", "x")
    try:
        C.safe_extract(buf.getvalue(), "zip", os.path.join(t, "z"))
        prop("canary: planted: a zip member outside its folder is refused", False)
    except ValueError:
        prop("canary: planted: a zip member outside its folder is refused", True)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        ti = tarfile.TarInfo("bag/link")
        ti.type, ti.linkname = tarfile.SYMTYPE, "/etc/passwd"
        tf.addfile(ti)
    try:
        C.safe_extract(buf.getvalue(), "tar", os.path.join(t, "s"))
        prop("canary: planted: a tarball holding a link is refused", False)
    except ValueError:
        prop("canary: planted: a tarball holding a link is refused", True)
    stopped_tests(t)
    tagmanifest_tests(t)


def stopped_tests(t):
    """A run that stops on an exception: recorded, and published only when a release is known (R3)."""
    def index_with(name, records):
        p = os.path.join(t, name)
        json.dump({"format": P.RECORD_FORMAT, "records": records}, open(p, "w"))
        return p
    empty = index_with("index-empty.json", [])
    released = index_with("index-released.json", [
        {"workflow": "pack-checks", "commit": SHA["tag"], "refs": ["refs/heads/main", "refs/tags/v1.2.0"]},
        {"workflow": "canary", "commit": SHA["other"], "refs": ["refs/tags/v1.10.0"]},
        {"workflow": "pack-checks", "commit": SHA["pr"], "refs": ["refs/tags/v2.0.0-rc1"]}])

    def unreadable(url):
        raise F.Unreachable(f"git ls-remote {url}: could not resolve host")
    fg = F.Forge(transport=recorded({}, []))
    res = C.canary_result(fg, unreadable, "unused", t, index_path=empty, say=lambda m: None)
    prop("canary: the pack repository's refs unread and no release in the records: nothing published",
         res["publish"] is False and res["release"] is None and res["result"] == "infrastructure"
         and res["checks"][-1]["name"] == "the reads", res)
    res = C.canary_result(fg, unreadable, "unused", t, index_path=released, say=lambda m: None)
    prop("canary: the refs unread and the records name releases: published as infrastructure, naming the newest by "
         "version, from the records", res["publish"] is True and res["release"] == {"tag": "v1.10.0", "commit": SHA["other"]}
         and res["result"] == "infrastructure" and "records hold" in res["checks"][-1]["detail"], res)
    tags = [(SHA["tagobj"], "refs/tags/v1.0.0"), (SHA["main"], "refs/tags/v1.0.0^{}")]
    res = C.canary_result(fg, lambda url: tags, os.path.join(t, "no-such-repository"), t, index_path=empty,
                          say=lambda m: None)
    prop("canary: a release found and its clone unread: published as infrastructure, naming that release",
         res["publish"] is True and res["release"] == {"tag": "v1.0.0", "commit": SHA["main"]}
         and res["result"] == "infrastructure" and "git clone --branch v1.0.0" in res["checks"][-1]["detail"], res)
    # An answer in a shape the code does not read: a Zenodo record whose one zip has no links.
    rec = "https://zenodo.org/api/records/1234568"
    fz = F.Forge(transport=recorded({rec: (200, {"Date": DATE}, {"files": [{"key": "falden-fixture-pack-v1.0.0.zip"}]})},
                                    []), sleep=lambda s: None, say=lambda m: None)
    try:
        C.zenodo_copy(fz, {"dois": ["10.5281/zenodo.1234567", "10.5281/zenodo.1234568"]}, t, (None, "offline"))
        raised = None
    except Exception as e:  # noqa: BLE001
        raised = e
    state = {"release": {"tag": "v1.0.0", "commit": SHA["main"]}, "expected": True,
             "checks": [C.item("the clone of v1.0.0: fixpack verify", "pass")]}
    res = C.stopped(raised, state, fz, index_path=empty) if raised is not None else {}
    prop("canary: planted: a Zenodo archive with no links, which zenodo_copy() raises KeyError on: a fail named by its "
         "type, published, the checks made before it kept", isinstance(raised, KeyError) and res.get("publish") is True
         and res.get("result") == "fail" and res["checks"][0]["result"] == "pass"
         and res["checks"][-1]["name"] == "the canary's run" and "KeyError: 'links'" in res["checks"][-1]["detail"],
         (repr(raised), res))
    recs = P.canary_record(res, DATE, {"id": "1", "attempt": "1", "event": "schedule", "url": "u"}) if res else []
    rec = recs[0][1] if recs else {}
    prop("canary: that result is written as a record by the publish step: a fail, naming v1.0.0 and the canary's run",
         rec.get("result") == "fail" and rec.get("subject", {}).get("release", {}).get("tag") == "v1.0.0"
         and [c["name"] for c in rec.get("checks", [])][-1:] == ["the canary's run"], rec)
    # main(), as the workflow runs it: what GITHUB_OUTPUT and the result file hold when a run stops.
    saved = (C.run_canary, C.D.ls_remote, dict(os.environ), C.INDEX)
    C.INDEX = empty  # main() reads the records it is given, here none
    for k in F.TOKEN_VARIABLES:
        os.environ.pop(k, None)

    def boom(forge, ls, clone_from, tmp, say=print, state=None):
        state["release"] = {"tag": "v1.0.0", "commit": SHA["main"]}
        state["expected"] = True
        state.setdefault("checks", []).append(C.item("the clone of v1.0.0: fixpack verify", "pass"))
        raise KeyError("fetch_url")
    try:
        for name, patch, want in (("a release found, then an answer it does not read", ("run_canary", boom), "true"),
                                  ("the pack repository's refs unread, no release in the records",
                                   ("ls_remote", unreadable), "false")):
            if patch[0] == "run_canary":
                C.run_canary = patch[1]
            else:
                C.D.ls_remote = patch[1]
            gho, out = os.path.join(t, f"gho-{want}.txt"), os.path.join(t, f"canary-{want}.json")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = C.main(["--out", out, "--github-output", gho])
            C.run_canary, C.D.ls_remote = saved[0], saved[1]
            held = open(gho).read().strip() if os.path.exists(gho) else ""
            got = json.load(open(out)) if os.path.exists(out) else {}
            prop(f"canary: main(), {name}: exit 1, publish={want}, the result written",
                 rc == 1 and held == f"publish={want}" and got.get("result") in ("fail", "infrastructure")
                 and got.get("publish") is (want == "true"), (rc, held, got))
    finally:
        C.run_canary, C.D.ls_remote, C.INDEX = saved[0], saved[1], saved[3]
        os.environ.clear()
        os.environ.update(saved[2])


def tagmanifest_tests(t):
    """Each archive copy is held to the release clone's tag manifest (the root's ruling 2 of P12-26 round 3)."""
    clone = os.path.join(t, "tm-clone")
    os.makedirs(os.path.join(clone, "data"))
    open(os.path.join(clone, "bagit.txt"), "w").write("BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8\n")
    open(os.path.join(clone, "data", "x.txt"), "w").write("x\n")
    open(os.path.join(clone, "bag-info.txt"), "w").write("Payload-Oxum: 2.1\n")

    def sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    open(os.path.join(clone, "manifest-sha256.txt"), "w").write(f"{sha(os.path.join(clone, 'data', 'x.txt'))}  data/x.txt\n")

    def seal(root):
        open(os.path.join(root, "tagmanifest-sha256.txt"), "w").write("".join(
            f"{sha(os.path.join(root, f))}  {f}\n" for f in ("bag-info.txt", "bagit.txt", "manifest-sha256.txt")))
    seal(clone)
    want = sha(os.path.join(clone, "tagmanifest-sha256.txt"))
    other = os.path.join(t, "tm-resealed")
    shutil.copytree(clone, other)
    open(os.path.join(other, "bag-info.txt"), "a").write("External-Description: changed after the release\n")
    seal(other)
    changed = sha(os.path.join(other, "tagmanifest-sha256.txt"))

    def zipped(root):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for d, _dirs, fs in os.walk(root):
                for f in fs:
                    p = os.path.join(d, f)
                    z.write(p, os.path.join("falden-fixtures-falden-fixture-pack-0123456", os.path.relpath(p, root)))
        return buf.getvalue()

    def tarred(root):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            tf.add(root, arcname="swh-dir")
        return buf.getvalue()
    exp = {"dois": ["10.5281/zenodo.1234567", "10.5281/zenodo.1234568"], "swhids": ["swh:1:snp:" + "3" * 40],
           "tagmanifest": want}
    rec, base, dirid = "https://zenodo.org/api/records/1234568", "https://archive.softwareheritage.org/api/1", "4" * 40
    raw = f"{base}/vault/flat/swh:1:dir:{dirid}/raw/"

    def answers(zip_of, tar_of):
        return {rec: (200, {"Date": DATE}, {"files": [{"key": "falden-fixture-pack-v1.0.0.zip",
                                                       "links": {"self": rec + "/files/x.zip/content"}}]}),
                rec + "/files/x.zip/content": (200, {"Date": DATE}, zipped(zip_of)),
                f"{base}/snapshot/{'3' * 40}/": (200, {"Date": DATE}, {"branches": {"refs/tags/v1.0.0": {
                    "target": dirid, "target_type": "directory"}}}),
                f"{base}/vault/flat/swh:1:dir:{dirid}/": (200, {"Date": DATE}, {"status": "done", "fetch_url": raw}),
                raw: (200, {"Date": DATE}, tarred(tar_of))}
    label = {"zenodo": "the Zenodo record 1234568's archive: its tagmanifest-sha256.txt is the release clone's",
             "swh": "the Software Heritage vault tarball: its tagmanifest-sha256.txt is the release clone's"}
    for zip_of, tar_of, ok in ((clone, clone, True), (other, other, False)):
        fg = F.Forge(transport=recorded(answers(zip_of, tar_of), []), sleep=lambda s: None, say=lambda m: None)
        for kind, run in (("zenodo", lambda: C.zenodo_copy(fg, exp, os.path.join(t, f"tm-z-{ok}"), (None, "offline"))),
                          ("swh", lambda: C.swh_copy(fg, exp, "v1.0.0", os.path.join(t, f"tm-s-{ok}"),
                                                     (None, "offline")))):
            got, err = attempt(run)
            item = next((c for c in got or [] if c["name"] == label[kind]), None)
            held = item is not None and item["result"] == ("pass" if ok else "fail") and (
                ok or (want in item["detail"] and changed in item["detail"]))
            copy = "a Zenodo archive" if kind == "zenodo" else "a vault tarball"
            prop(f"canary: {copy} holding the release clone's tag manifest passes the check that holds it to the clone"
                 if ok else f"canary: planted: {copy} resealed as a valid bag of other bytes fails the check that "
                            f"holds it to the release clone, naming both digests",
                 held, err or [c["name"] + ": " + c["result"] for c in got or []])


def tree_files(root):
    """The files a commit of this tree holds: git's list in a checkout, else every file but .git and bytecode."""
    r = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard"], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    if r.returncode == 0 and r.stdout.strip():
        return sorted(ln for ln in r.stdout.splitlines() if os.path.isfile(os.path.join(root, ln)))
    out = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".git", "__pycache__")]
        out += [os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/") for f in fs]
    return sorted(out)


def settings_tests():
    index = json.load(open(os.path.join(ROOT, "records", "index.json"), encoding="utf-8"))
    if index.get("records"):
        print("  ----  settings: the tree holds records, so it is no longer the first commit's, which SHA256SUMS lists")
        return
    listed = {}
    for ln in open(os.path.join(ROOT, "settings", "SHA256SUMS"), encoding="utf-8").read().splitlines():
        digest, path = ln.split("  ", 1)
        listed[path] = digest
    files = [f for f in tree_files(ROOT) if f != "settings/SHA256SUMS"]
    changed = [f for f in files if f in listed and
               listed[f] != hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest()]
    prop(f"settings: SHA256SUMS lists every other file of the first commit's tree ({len(files)}), each digest "
         f"matching, and nothing else", sorted(listed) == files and not changed,
         {"unlisted": sorted(set(files) - set(listed)), "not in the tree": sorted(set(listed) - set(files)),
          "changed": changed})


def main():
    with tempfile.TemporaryDirectory(prefix="status-unit-") as t:
        forge_tests()
        detect_tests()
        fetch_tests(t)
        keys = keys_tests(t)
        stage_tests(t, keys)
        kinds = kind_tests(t, keys)
        runner_tests(t, keys, kinds)
        path_tests(t, keys, kinds)
        config_tests(t, keys, kinds)
        blocks_tests(t)
        publish_tests(t)
        canary_tests(t)
        settings_tests()
    if FAILED:
        print(f"  status-unit-test: {len(FAILED)} propert{'y' if len(FAILED) == 1 else 'ies'} failed")
        return 1
    print("  status-unit-test: every property holds and every plant was refused, offline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
