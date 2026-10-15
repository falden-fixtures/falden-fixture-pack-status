#!/usr/bin/env python3
"""What the pack checks check this run (REG-416): the pack repository's refs, read anonymously, against the records.

    ci/detect.py --index records/index.json [--ref REF] [--github-output FILE]

The pack repository's branches and tags are read with `git ls-remote`, anonymously, and its record of itself with
one anonymous GET of the REST API, whose Date header is the time the refs were observed and whose id and
visibility say the repository is the public one checked. A commit a branch (refs/heads/*) or tag (refs/tags/*)
points at is checked until a record of a pass or a fail holds that commit with exactly those refs; pull request
refs and every other ref are not read. A record of infrastructure, a check that could not be run, is not final: a
commit whose records are all infrastructure is checked again at the next run, until it holds three (INFRA_TRIES),
and then it is left to a release's dispatch, which the release step sends again after an infrastructure record
(settings/CREATE.md). A ref given with --ref, a branch, a tag, a full ref or a 40-hex commit the repository holds,
is checked whatever the records say: that is a release's dispatch. Writes, for the next jobs, `any` (true when there
is something to check), `commits` (a JSON list of {"commit", "refs"}) and `observed` (the Date header), to
GITHUB_OUTPUT or to standard output. Exits 0 when the reads succeed, 1 when --ref names nothing the repository
holds, and 2 when a read fails after its retries: infrastructure, and nothing is checked.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forge as F  # noqa: E402

PACK_REPOSITORY = "falden-fixtures/falden-fixture-pack"
INFRA_TRIES = 3  # infrastructure records after which the six-hourly runs leave a commit to a dispatch


def ls_remote(url, runner=None):
    """[(sha, ref)] from `git ls-remote url`, peeled tags as `<tag>^{}`, after three tries; Unreachable else."""
    runner = runner or (lambda: subprocess.run(["git", "ls-remote", url], capture_output=True, text=True,
                                               env=F.git_env(), stdin=subprocess.DEVNULL, timeout=120))
    last = ""
    for _ in range(3):
        try:
            r = runner()
        except subprocess.TimeoutExpired:
            last = "timed out"
            continue
        if r.returncode == 0:
            out = []
            for ln in r.stdout.splitlines():
                m = re.fullmatch(r"([0-9a-f]{40})\t(\S+)", ln.strip())
                if m:
                    out.append((m.group(1), m.group(2)))
            return out
        last = (r.stderr or r.stdout).strip()[-300:]
    raise F.Unreachable(f"git ls-remote {url}: {last}")


def commits_of(refs):
    """{commit: sorted refs} for the branch and tag refs, each tag peeled to its commit."""
    peeled = {ref[:-3]: sha for sha, ref in refs if ref.endswith("^{}")}
    out = {}
    for sha, ref in refs:
        if ref.endswith("^{}") or not (ref.startswith("refs/heads/") or ref.startswith("refs/tags/")):
            continue
        commit = peeled.get(ref, sha)
        out.setdefault(commit, set()).add(ref)
    return {c: sorted(r) for c, r in out.items()}


def recorded(index):
    """{(commit, refs as a tuple)} the pack checks have checked: a record of a pass or a fail holds them, or
    INFRA_TRIES records whose result is anything else, infrastructure, do. A commit with fewer of those alone is
    checked again."""
    final, tries = set(), {}
    for r in index.get("records", []):
        if r.get("workflow") != "pack-checks" or not isinstance(r.get("commit"), str):
            continue
        key = (r["commit"], tuple(r.get("refs", [])))
        if r.get("result") in ("pass", "fail"):
            final.add(key)
        else:
            tries[key] = tries.get(key, 0) + 1
    return final | {k for k, n in tries.items() if n >= INFRA_TRIES}


def resolve(ref, refs):
    """The commit `ref` names among `refs`, as a full ref, a branch, a tag or a commit: (commit, refs) or None."""
    by = commits_of(refs)
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref, by.get(ref, [])
    for full in (ref, f"refs/heads/{ref}", f"refs/tags/{ref}"):
        for c, rs in by.items():
            if full in rs:
                return c, rs
    return None


def detect(index, ref=None, repo=PACK_REPOSITORY, forge=None, ls=None):
    """{"any", "commits", "observed", "repository_id"} for this run, or raises Unreachable."""
    forge = forge or F.Forge()
    refs = (ls or ls_remote)(f"https://github.com/{repo}")
    a = forge.get(f"https://api.github.com/repos/{repo}")
    if a.status != 200:
        raise F.Unreachable(f"GET /repos/{repo} answered {a.status}")
    info = a.json()
    if info.get("full_name") != repo or info.get("private") is not False:
        raise ValueError(f"/repos/{repo} names {info.get('full_name')!r}, private {info.get('private')!r}: not the "
                         f"public pack repository")
    by = commits_of(refs)
    if ref:
        hit = resolve(ref, refs)
        if hit is None:
            return {"error": f"{ref!r} names no branch, tag or commit of {repo}"}
        todo = [{"commit": hit[0], "refs": hit[1]}]
    else:
        done = recorded(index)
        todo = [{"commit": c, "refs": rs} for c, rs in sorted(by.items(), key=lambda x: x[1])
                if (c, tuple(rs)) not in done]
    return {"any": bool(todo), "commits": todo, "observed": a.date, "repository_id": info.get("id")}


def write_outputs(result, path):
    lines = [f"any={'true' if result['any'] else 'false'}", f"commits={json.dumps(result['commits'])}",
             f"observed={result['observed'] or ''}", f"repository_id={result.get('repository_id') or ''}"]
    text = "\n".join(lines) + "\n"
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)


def main(argv):
    ap = argparse.ArgumentParser(prog="ci/detect.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--index", required=True)
    ap.add_argument("--ref", default="")
    ap.add_argument("--github-output", default="")
    ap.add_argument("--repo", default=PACK_REPOSITORY)
    a = ap.parse_args(argv)
    try:
        F.refuse_tokens()
        with open(a.index, encoding="utf-8") as fh:
            index = json.load(fh)
        result = detect(index, a.ref.strip() or None, a.repo)
    except F.TokenInEnvironment as e:
        print(f"  detect: {e}")
        return 2
    except F.Unreachable as e:
        print(f"  detect: the pack repository could not be read, infrastructure: {e}")
        return 2
    except (OSError, ValueError) as e:
        print(f"  detect: {e}")
        return 2
    if "error" in result:
        print(f"  detect: {result['error']}")
        return 1
    print(f"  detect: {repo_line(result, a.repo)}")
    write_outputs(result, a.github_output)
    return 0


def repo_line(result, repo):
    if not result["any"]:
        return f"{repo} holds no commit left to check (observed {result['observed']})"
    return (f"{len(result['commits'])} commit(s) of {repo} to check, observed {result['observed']}: "
            + "; ".join(f"{c['commit'][:12]} ({', '.join(c['refs']) or 'named by commit'})" for c in result["commits"]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
