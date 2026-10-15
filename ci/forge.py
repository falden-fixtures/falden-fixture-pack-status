"""The status repository's one door to the network for its reads: anonymous, counted and dated (REG-416).

ANONYMOUS. A read here carries no credential: no Authorization header is ever sent, and refuse_tokens() stops a
program before its first read when GH_TOKEN, GITHUB_TOKEN or another token variable is set in its environment,
which the workflows' read steps set empty. git is run with no credential helper and no prompt (git_env()).

COUNTED. GitHub gives an anonymous caller 60 requests an hour to its REST API. Forge counts its own requests to
api.github.com and, before the 61st within an hour of the first, waits until that hour has passed; when an answer
says none remain (x-ratelimit-remaining 0), it waits until the reset the answer names, a second past it. A wait
longer than max_wait is refused rather than waited, so a job never outlives its own time limit asleep.

DATED. Every answer keeps its Date header, the forge's own clock, and a record's time is one of them (records'
format falden-status-record/1), never the runner's clock.

RETRIED. A read that fails to connect, times out or is answered 5xx is tried again, three tries in all with a
pause between; when every try fails, Unreachable is raised, which a caller records as infrastructure.

A transport is a function (method, url, headers) -> (status, headers, body); tests give one that answers from
recorded responses, and nothing then reaches the network.
"""
import os
import time
import urllib.error
import urllib.request

TOKEN_VARIABLES = ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN", "GITHUB_PAT",
                   "GH_PAT")
API_HOST = "api.github.com"
USER_AGENT = "falden-fixture-pack-status"
HOURLY = 60


class Unreachable(Exception):
    """Every try of a read failed: infrastructure, not a finding about the pack."""


class TokenInEnvironment(Exception):
    """A token is set where the reads are to be anonymous."""


def refuse_tokens(env=None):
    env = os.environ if env is None else env
    held = [k for k in TOKEN_VARIABLES if env.get(k)]
    if held:
        raise TokenInEnvironment(f"{', '.join(held)} is set; this program's reads are anonymous (REG-416), and the "
                                 f"workflow's read steps set it empty")


def git_env(env=None):
    """An environment for git that holds no token and asks for nothing: no credential helper reaches it."""
    out = {k: v for k, v in (os.environ if env is None else env).items() if k not in TOKEN_VARIABLES}
    out.update({"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "/bin/false", "SSH_ASKPASS": "/bin/false",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "credential.helper",
                "GIT_CONFIG_VALUE_0": ""})
    return out


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # a 3xx is answered to the caller, its Location read there
        return None


def urllib_transport(method, url, headers, follow=True, timeout=120):
    req = urllib.request.Request(url, method=method, headers=headers)
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read()


class Answer:
    def __init__(self, url, status, headers, body):
        self.url, self.status, self.headers, self.body = url, status, headers, body

    @property
    def date(self):
        return self.headers.get("date")

    def json(self):
        import json
        return json.loads(self.body.decode("utf-8"))


class Forge:
    def __init__(self, transport=urllib_transport, clock=time.time, sleep=time.sleep, tries=3, pause=10,
                 max_wait=3900, say=print):
        self.transport, self.clock, self.sleep = transport, clock, sleep
        self.tries, self.pause, self.max_wait, self.say = tries, pause, max_wait, say
        self.api_times = []  # when each request to api.github.com was sent
        self.dates = []      # every Date header an answer carried, in order
        self.requests = 0
        self.api_reset = None  # when GitHub said the hour's anonymous requests come back, if it said none remain

    def _wait(self, seconds, why):
        if seconds > self.max_wait:
            raise Unreachable(f"the next read would wait {seconds:.0f} s ({why}), past the {self.max_wait} s this "
                              f"run allows")
        if seconds > 0:
            self.say(f"  forge: waiting {seconds:.0f} s: {why}")
            self.sleep(seconds)

    def _before_api(self):
        if self.api_reset is not None:
            self._wait(self.api_reset - self.clock() + 1, "GitHub said no anonymous request remains until its reset")
            self.api_reset = None
        now = self.clock()
        self.api_times = [t for t in self.api_times if now - t < 3600]
        if len(self.api_times) >= HOURLY:
            self._wait(3600 - (now - self.api_times[0]) + 1, f"{HOURLY} anonymous requests to the API in the last "
                                                               f"hour, GitHub's limit")
            now = self.clock()
            self.api_times = [t for t in self.api_times if now - t < 3600]
        self.api_times.append(now)

    def get(self, url, accept="application/vnd.github+json", api_version=None, method="GET", follow=True):
        """The answer to an anonymous `method` of `url`, after its retries; Unreachable when every try failed.
        With follow false, a redirect is the answer, its Location in its headers."""
        headers = {"User-Agent": USER_AGENT, "Accept": accept}
        if api_version:
            headers["X-GitHub-Api-Version"] = api_version
        api = url.startswith(f"https://{API_HOST}/")
        last = None
        for attempt in range(1, self.tries + 1):
            if api:
                self._before_api()
            self.requests += 1
            try:
                status, h, body = self.transport(method, url, headers, follow=follow)
            except (OSError, ValueError) as e:  # urllib's URLError is an OSError; a timeout too
                last = f"{type(e).__name__}: {e}"
                status = None
            if status is not None:
                h = {k.lower(): v for k, v in h.items()}
                if h.get("date"):
                    self.dates.append(h["date"])
                if api and h.get("x-ratelimit-remaining") == "0":
                    self.api_reset = float(h.get("x-ratelimit-reset") or (self.clock() + 3600))
                    if status in (403, 429):
                        last = f"HTTP {status}, the anonymous rate limit"
                        continue  # the next try waits for the reset first (_before_api)
                if status < 500:
                    return Answer(url, status, h, body)
                last = f"HTTP {status}"
            if attempt < self.tries:
                self.sleep(self.pause * attempt)
        raise Unreachable(f"{method} {url}: {last}, after {self.tries} tries")
