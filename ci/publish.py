#!/usr/bin/env python3
"""The records (REG-416): what a run found, written as falden-status-record/1, listed in records/index.json and in
the README's table. The publish job runs this, then ci/push.sh commits it with the job's own token.

    ci/publish.py --fetch-date FILE
        the forge's time for the record: the Date header of one anonymous read of GitHub, written to FILE
    ci/publish.py --workflow pack-checks --legs DIR --legs-expected N --commits-env VAR --observed-env VAR --time-file FILE
        one record for each commit detect named, from the legs' results under DIR
    ci/publish.py --workflow canary --canary FILE --time-file FILE
        one record of the canary's result

A record's time is the forge's Date header, never the runner's clock. A leg's result is data from a job that ran the
pack's own code, so it is read as untrusted: its shape is checked, its text bounded, and a leg whose result is
missing or unreadable is recorded as infrastructure for that platform. Nothing is written that holds a token's
shape (a GitHub token, an AWS key, a private key block, x-access-token): the run stops instead. A record's commit
and refs reach the README's table escaped, so no ref name can add a column, a link or markup.
"""
import argparse
import email.utils
import glob
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import forge as F  # noqa: E402

RECORD_FORMAT = "falden-status-record/1"
LEG_FORMAT = "falden-status-leg/1"
CANARY_FORMAT = "falden-status-canary/1"
PACK = "falden-fixtures/falden-fixture-pack"
RESULTS = ("pass", "fail", "skipped", "infrastructure")
SECRET = re.compile(r"gh[opusr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|x-access-token|"
                    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----")
BEGIN, END = "<!-- records:begin -->", "<!-- records:end -->"
LIMITS = {"commits": 50, "checks": 300, "text": 1500, "name": 300}


class Refused(Exception):
    pass


def text(v, n=LIMITS["text"]):
    return v if isinstance(v, str) and len(v) <= n else (v[:n] if isinstance(v, str) else "")


def read_leg(path):
    """A leg's result, its shape checked and its text bounded, or None when it cannot be read as one."""
    try:
        with open(path, encoding="utf-8") as fh:
            leg = json.load(fh)
    except (OSError, ValueError, RecursionError):
        return None
    if not (isinstance(leg, dict) and leg.get("format") == LEG_FORMAT and isinstance(leg.get("commits"), list)
            and len(leg["commits"]) <= LIMITS["commits"] and isinstance(leg.get("leg"), dict)):
        return None
    out = {"name": text(leg["leg"].get("name"), LIMITS["name"]) or "unnamed",
           "tools": {k: text(v, 200) for k, v in leg["leg"].items() if k != "name" and isinstance(v, str)},
           "result": leg.get("result") if leg.get("result") in RESULTS else "infrastructure", "commits": {}}
    for c in leg["commits"]:
        if not (isinstance(c, dict) and re.fullmatch(r"[0-9a-f]{40}", str(c.get("commit")))
                and isinstance(c.get("checks"), list) and len(c["checks"]) <= LIMITS["checks"]):
            return None
        checks = []
        for k in c["checks"]:
            if not (isinstance(k, dict) and k.get("result") in RESULTS):
                return None
            checks.append({"name": text(k.get("name"), LIMITS["name"]), "result": k["result"],
                           "detail": text(k.get("detail")), "seconds": k.get("seconds") if isinstance(
                               k.get("seconds"), (int, float)) else None})
        out["commits"][c["commit"]] = {"stage": text(c.get("stage"), 40),
                                       "result": c.get("result") if c.get("result") in RESULTS else "infrastructure",
                                       "checks": checks}
    return out


def overall(results):
    rs = set(results)
    return "fail" if "fail" in rs else "infrastructure" if "infrastructure" in rs or not rs else "pass"


def stamp(date):
    """YYYYMMDDTHHMMSSZ from an HTTP Date header."""
    t = email.utils.parsedate_to_datetime(date)
    return t.strftime("%Y%m%dT%H%M%SZ")


def run_info(env=None):
    env = os.environ if env is None else env
    rid = env.get("GITHUB_RUN_ID", "")
    repo = env.get("GITHUB_REPOSITORY", "falden-fixtures/falden-fixture-pack-status")
    return {"id": rid, "attempt": env.get("GITHUB_RUN_ATTEMPT", ""), "event": env.get("GITHUB_EVENT_NAME", ""),
            "url": f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{rid}" if rid else ""}


def pack_records(commits, observed, legs, expected, time, run):
    """[(path, record)] for each commit detect named, from the legs' results (None for one that is missing)."""
    out = []
    readable = [x for x in legs if x is not None]
    missing = expected - len(readable)
    for c in commits:
        entries = []
        for leg in readable:
            got = leg["commits"].get(c["commit"])
            entries.append({"leg": leg["name"], "tools": leg["tools"],
                            "result": got["result"] if got else "infrastructure",
                            "stage": got["stage"] if got else "unknown",
                            "checks": got["checks"] if got else [{"name": "this commit's checks", "result":
                                                                  "infrastructure", "detail": "the leg ran and holds no "
                                                                  "result for this commit", "seconds": None}]})
        for i in range(max(0, missing)):
            entries.append({"leg": f"a leg with no readable result ({i + 1} of {missing})", "tools": {},
                            "result": "infrastructure", "stage": "unknown",
                            "checks": [{"name": "the leg's result", "result": "infrastructure",
                                        "detail": "no result arrived, or it could not be read as falden-status-leg/1",
                                        "seconds": None}]})
        stages = sorted({e["stage"] for e in entries if e["stage"] != "unknown"})
        rec = {"format": RECORD_FORMAT, "workflow": "pack-checks", "time": time,
               "subject": {"repository": PACK, "commit": c["commit"], "refs": list(c.get("refs", [])),
                           "observed": observed},
               "stage": stages[0] if len(stages) == 1 else ("mixed: " + ", ".join(stages)) if stages else "unknown",
               "result": overall(e["result"] for e in entries), "legs": entries, "run": run}
        out.append((f"records/pack-checks/{stamp(time)}-{c['commit'][:12]}.json", rec))
    return out


def canary_record(res, time, run):
    if not (isinstance(res, dict) and res.get("format") == CANARY_FORMAT and isinstance(res.get("checks"), list)):
        raise Refused("the canary's result is not falden-status-canary/1")
    rel = res.get("release") if isinstance(res.get("release"), dict) else {}
    checks = [{"name": text(k.get("name"), LIMITS["name"]), "result": k.get("result") if k.get("result") in RESULTS
               else "infrastructure", "detail": text(k.get("detail"))} for k in res["checks"][:LIMITS["checks"]]
              if isinstance(k, dict)]
    rec = {"format": RECORD_FORMAT, "workflow": "canary", "time": time,
           "subject": {"repository": PACK, "release": {"tag": text(rel.get("tag"), 60), "commit": text(rel.get("commit"), 40)}},
           "stage": "release", "result": overall(k["result"] for k in checks), "checks": checks, "run": run}
    return [(f"records/canary/{stamp(time)}.json", rec)]


def md(s):
    """`s` safe in a Markdown table cell: no pipe, backtick, bracket, angle bracket or line break survives."""
    return re.sub(r"[|`\[\]<>\r\n\\]", "_", str(s))


def table(index):
    rows = sorted(index["records"], key=lambda r: (email.utils.parsedate_to_datetime(r["time"]), r["path"]), reverse=True)
    if not rows:
        return "No record yet."
    lines = ["| time (the forge's Date) | workflow | pack commit | refs | stage | result | record |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r.get("commit") or ""
        link = f"[`{md(c[:12])}`](https://github.com/{PACK}/commit/{md(c)})" if re.fullmatch(r"[0-9a-f]{40}", c) else ""
        lines.append(f"| {md(r['time'])} | {md(r['workflow'])} | {link} | {md(', '.join(r.get('refs', [])))} | "
                     f"{md(r.get('stage', ''))} | **{md(r['result'])}** | [{md(r['path'].rsplit('/', 1)[-1])}]({md(r['path'])}) |")
    return "\n".join(lines)


def write(root, records):
    """Write the records, add them to records/index.json and redraw the README's table. Refused when a record holds
    a token's shape, or names a path a record already has."""
    for path, rec in records:
        blob = json.dumps(rec, indent=1, sort_keys=False)
        if SECRET.search(blob):
            raise Refused(f"{path}: the record holds a token's shape; nothing is written")
        if os.path.exists(os.path.join(root, path)):
            raise Refused(f"{path} is already recorded")
    ip = os.path.join(root, "records", "index.json")
    index = json.load(open(ip, encoding="utf-8"))
    for path, rec in records:
        os.makedirs(os.path.dirname(os.path.join(root, path)), exist_ok=True)
        with open(os.path.join(root, path), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
            fh.write("\n")
        subj = rec["subject"]
        index["records"].append({"workflow": rec["workflow"], "time": rec["time"],
                                 "commit": subj.get("commit") or (subj.get("release") or {}).get("commit"),
                                 "refs": subj.get("refs") or ([f"refs/tags/{subj['release']['tag']}"]
                                                               if subj.get("release", {}).get("tag") else []),
                                 "stage": rec["stage"], "result": rec["result"], "path": path})
    with open(ip, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1)
        fh.write("\n")
    rp = os.path.join(root, "README.md")
    readme = open(rp, encoding="utf-8").read()
    i, j = readme.find(BEGIN), readme.find(END)
    if i < 0 or j < i:
        raise Refused("README.md has no records table between its markers")
    readme = readme[:i + len(BEGIN)] + "\n" + table(index) + "\n" + readme[j:]
    with open(rp, "w", encoding="utf-8") as fh:
        fh.write(readme)
    return index


def main(argv, env=None):
    env = os.environ if env is None else env
    ap = argparse.ArgumentParser(prog="ci/publish.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--fetch-date")
    ap.add_argument("--workflow", choices=("pack-checks", "canary"))
    ap.add_argument("--legs")
    ap.add_argument("--legs-expected", type=int, default=0)
    ap.add_argument("--commits-env", default="COMMITS")
    ap.add_argument("--observed-env", default="OBSERVED")
    ap.add_argument("--canary")
    ap.add_argument("--time-file")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    if a.fetch_date:
        try:
            F.refuse_tokens(env)
            answer = F.Forge().get("https://api.github.com/zen", accept="text/plain")
        except (F.TokenInEnvironment, F.Unreachable) as e:
            print(f"  publish: {e}")
            return 2
        if not answer.date:
            print("  publish: the forge's answer carried no Date header")
            return 2
        open(a.fetch_date, "w").write(answer.date + "\n")
        print(f"  publish: the forge's time for the record: {answer.date}")
        return 0
    try:
        time = open(a.time_file).read().strip()
        stamp(time)
    except (OSError, TypeError, ValueError) as e:
        print(f"  publish: the forge's time cannot be read from {a.time_file}: {e}")
        return 2
    run = run_info(env)
    try:
        if a.workflow == "pack-checks":
            commits = json.loads(env.get(a.commits_env, "[]"))
            if not (isinstance(commits, list) and all(isinstance(c, dict) and re.fullmatch(r"[0-9a-f]{40}", str(c.get("commit")))
                                                      for c in commits)):
                raise Refused(f"{a.commits_env} is not detect's list of commits")
            paths = sorted(glob.glob(os.path.join(a.legs, "**", "leg.json"), recursive=True))
            legs = [read_leg(p) for p in paths]
            records = pack_records(commits, env.get(a.observed_env, ""), legs, max(a.legs_expected, len(legs)), time, run)
        else:
            records = canary_record(json.load(open(a.canary, encoding="utf-8")), time, run)
        write(a.root, records)
    except (Refused, OSError, ValueError) as e:
        print(f"  publish: {e}")
        return 1
    for path, rec in records:
        print(f"  publish: {path}: {rec['result']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
