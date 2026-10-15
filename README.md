# falden-fixture-pack-status

This repository checks the published falden-fixture-pack from outside it and keeps a dated record of
each check. The pack repository, [`falden-fixtures/falden-fixture-pack`](https://github.com/falden-fixtures/falden-fixture-pack),
runs no GitHub Actions of its own, so the checks a reader of the pack would run are run here, on
GitHub's runners, and each result is committed here as a record.

## What is checked

**The pack checks** (`.github/workflows/pack-checks.yml`) read the pack repository's branches and
tags every six hours, at minute 17, without a token. A commit a branch or tag points at is checked
until a pass or a fail is recorded for it here; one whose records are all infrastructure, checks that
could not be run, is checked again at each of these runs until it holds three. A ref named when the
workflow is run by hand is checked whatever is recorded. What a commit is checked for follows from
what it holds:

* **Anchor stage**, a commit that holds `anchor/` and no `bagit.txt`, as the pack repository does
  until the pack is published: each anchor's signature with `ssh-keygen -Y verify`, both of its
  RFC 3161 timestamp tokens with `openssl ts -verify` under OpenSSL 3, the anchor tag's signature
  with `git verify-tag`, and that the repository holds no workflow. The signature and the tag are
  verified with the release keys this repository pins in `ci/release-keys.json`, never with keys a
  commit names: the two keys the pack repository's `anchor/allowed_signers` named at commit
  `cf42ad6` for an anchor's signature, and the release key alone for its tag. Each file these
  checks read is the commit's own: one that is a link, or lies under one, or is a folder fails the
  check that reads it, naming it, since a link can lead out of the commit to a file on the machine
  running the check that no reader's clone holds. A commit whose `anchor/allowed_signers` names a
  key the pin lacks fails, naming that key, whether or not it holds an anchor. A line of that file
  in a form that `ssh-keygen` could read differently from a
  split into fields fails as well, naming the line: one holding a character other than printable
  ASCII, a space or a tab, a quote in its principals, in its options a backslash or a quote still
  open at a space or tab, or a key type the split does not take for one, such as the short names
  `ED25519` and `ed25519`. Line 1 of that file must be the plain line of a key the pin marks for
  tags, `falden-fixture-release namespaces="falden-fixture-anchor"`, that key, and a comment or
  none, since the pack's `VERIFYING.md` makes a reader's tag check from line 1's third and fourth
  fields, and any other line 1 fails, naming line 1. A key is rotated by adding the new key to the
  pin first and to the pack's `anchor/allowed_signers` after, a new tag key going on line 1 there
  when it becomes the tag key. A key that signed an anchor the pack holds stays in both, pinned as
  it was, for as long as the pack holds that anchor, which is for good, since these checks verify
  each anchor with the pinned keys alone; only a key that signed no anchor leaves, the pack's file
  first and the pin after. At each step the pin holds every key the pack names, so a key reaches
  these checks only through a commit here.
* **Release stage**, a commit whose root holds `bagit.txt`: both manifests with `sha256sum -c`,
  `bagit` 1.9.0 `--validate`, `fixpack verify`, `fixpack witness`, the conformance suite, the crash
  adapter's exit code, the grade's result against its own schema, and the commands in the pack's
  `VERIFYING.md`. Each fenced block of that page is classified here by the sha256 of its text
  (`ci/verifying-blocks.json`): run on Linux, on macOS, once for each attested bundle, or not run,
  with the reason. A block this repository has not classified fails the check.

Whatever its stage, a commit fails when it no longer holds an anchor manifest,
`anchor/predicates-<N>.manifest`, that a commit it descends from held, naming the manifest, so no
anchor leaves the pack by a commit that drops it or `anchor/` itself. An anchor manifest is a file
under its number as the pack writes it, 1, 2 and so on: a link, a folder or a submodule by that name
is none, and nor is a name such as `predicates-01.manifest`. A commit whose history holds no
manifest, such as the pack repository's first three commits, passes this check, and for one whose
history cannot be read in full this check is infrastructure.

Whatever its stage and its history, a commit also fails when its tree holds a link or a submodule
anywhere, naming them. That check reads the commit's tree as git holds it, never the files a
checkout of it shows, since a link can lead out of the commit, and a submodule is another
repository's commit, whose files a clone of the pack does not hold.

Each commit is checked on Ubuntu 24.04 with Python 3.9 and with the latest Python release, and on
macOS 15 with the system's `/usr/bin/python3`. A download or an install that still fails after its
retries is recorded as infrastructure, never as a pass or a fail of the pack. A check that stops on
an error raised by what a commit holds, as when the folder a check runs in is a link to one the
runner cannot enter, fails that commit, naming the error, and the run goes on to the next commit. A
tool the runner cannot start, such as `git`, `ssh-keygen` or Python, is the runner's fault and not
the pack's: that platform writes no result, and the record shows it as infrastructure, never as a
pass or a fail of the pack. No tool is started from an entry of the runner's `PATH` that is empty,
`.` or another relative one, any of which can lead to a commit's own files, so a tool the runner
holds only behind such an entry is one it cannot start. The checks start `git`, and every command
of the pack's, with the runner's git configuration, git attributes and git templates set aside and
none of the runner's `GIT_` variables, so what a check needs is given on the command line. When
the pack repository cannot be read at all, no commit is checked and nothing is recorded: that run
shows as failed among this repository's Actions runs, and the next one reads the pack repository
again.

**The canary** (`.github/workflows/canary.yml`) runs on the 3rd of each month at 07:43 UTC, with
anonymous reads only, at most 60 an hour, waiting out GitHub's rate limit when it is reached. Once
the pack is released it checks that what the release recorded still holds, its expected values
read from a clone of the release: the subject repositories' branch heads against the sealed refs,
their `/activity` counts and newest entries, that each is archived, that each principal id still
names its login, that the DOI, the Software Heritage identifiers and the Rekor entries resolve, that
GitHub marks no deprecation on the API version the pack is keyed to, and the fixity of the three
public copies of the release, a clone of its tag, the Zenodo archive and a Software Heritage vault
tarball, each with `bagit --validate` and `fixpack verify`, with the Zenodo archive and the tarball
each held to the clone too: each must hold the clone's `tagmanifest-sha256.txt`, byte for byte.
Before the first release there is nothing for it to check, and it publishes nothing.

## Records

Each check writes one record under `records/`, in the format `falden-status-record/1`: what was
checked (the repository, the commit and the refs that point at it), each run's result by platform
and check, and the run that made it. A record's time is the `Date` header of GitHub's own answer, not
the runner's clock. `records/index.json` lists every record, and the table below shows them, newest
first.

<!-- records:begin -->
No record yet.
<!-- records:end -->

## How it writes

Each workflow's publish job alone may write this repository (`contents: write`), with the job's own
`GITHUB_TOKEN`, which reaches this repository only and expires when the job ends. Every other job
reads only. This repository holds no other credential, token or secret, and every action its
workflows use is pinned by its full commit.

GitHub turns off a public repository's scheduled workflows after 60 days without activity in it.
Each record is a commit, and from the pack's first release on the canary commits one every month,
whatever it finds. Whether GitHub counts a commit made with a job's own token as activity is not yet
known here; if it does not, the monthly records stop, and the missing month shows in the table
above. Before the first release, 60 days with no new commit in the pack repository leave nothing to
record, and GitHub may turn both off; the release step turns them on again before it runs the checks
on the new tag (`settings/CREATE.md`).

## Tests

`python3 ci/tests/unit_test.py` checks the code here offline, against answers made in the shape of
GitHub's, doi.org's, Zenodo's and Software Heritage's. `python3 ci/tests/dry_run.py` runs both
workflows' checks and the canary end to end on one machine, with no network, against a clone of the
pack repository and a bag of the pack. It plants these faults, and each must fail the check it
breaks, by name:

* at the anchor stage, the signature cut, a timestamp token swapped for one over other data, a
  workflow added, and three keys the pin lacks, each named in `anchor/allowed_signers`: one added
  there, one that signed the manifest and one that signed the tag; and six lines added there that
  name a key the pin lacks to `ssh-keygen` and the pinned release key to a split of the line into
  fields: the pinned key in a quoted option, in quoted principals, after an escaped quote, or
  between unit separators or no-break spaces, and a carriage return, at which `ssh-keygen` ends the
  principals; a key the pin lacks added there at `2b78c56`, which holds no anchor manifest; the
  anchor's manifest removed, alone and with a key the pin lacks added, and `anchor/` removed, each
  failing for the manifest that is gone, while the first, read from a shallow clone, is
  infrastructure instead; and six line 1s other than the release key's plain line, each in a file
  whose key lines name pinned keys alone: a comment whose third and fourth fields are a key the pin
  lacks, which a reader's tag check made from that line then trusts, a blank line, the recovery
  key's line, and the release key's line with no options, with another option or under another
  principal; the anchor's manifest renamed `predicates-01.manifest` or under the Arabic-Indic digit
  one, made a folder, a link that leads nowhere or a submodule, each failing for the manifest that
  is gone, and a stray `predicates-02.manifest` beside it, which is no anchor's and passes, as does
  the commit that removes it again; `anchor/allowed_signers`, the signature, a timestamp token and the
  authorities' chains, each made a link to its copy in the runner's own clone of the pack
  repository, and `anchor/` made such a link at the pack repository's first commit, each failing
  the checks that read through it, naming the link; `anchor/` made a link, inside the commit, to a
  folder holding anchor #1's files and no `allowed_signers`, at the first commit and at `2b78c56`,
  with anchor #1's signature or one by a key the pin lacks, `anchor/` made a submodule, a link at
  the root of the first commit, and a link and a submodule three folders down beside the anchor,
  each failing the check that the commit holds no link and no submodule, naming it, as each link
  and submodule above does too; and `bagit.txt` added, which takes the commit to the release stage
  with no `data/` to run in, whose checks stop on an error that fails the commit, naming it, as they
  do when `data/` is a link to a folder the runner cannot enter, which fails the check that the
  commit holds no link and no submodule as well, while the commit checked after it in the same run
  passes;
* at the release stage, a payload byte changed, a tag file removed, a `VERIFYING.md` block this
  repository has not classified, and a payload file made a link to its copy in the runner's own
  clone, failing that same check, `bagit` and `fixpack verify`, while `sha256sum -c` reads through
  the link and passes; and `data/` made a link to a folder the runner cannot enter, which fails
  that same check, while the error raised on entering it, where the crash adapter and the grade
  run, fails the commit too, naming it, and the release checked with it passes;
* on the runner, a `PATH` that holds no `ssh-keygen`, on which that platform writes no result and
  its record is infrastructure, and an `OPENSSL` that names no file, as a path or as a name no
  entry of `PATH` holds, which is passed over for another OpenSSL 3; a `PATH` whose first entry is
  `.`, empty or a folder of the commit, ahead of an executable `ssh-keygen` the commit holds, which
  says every signature is good, beside a changed manifest, each failing the signature check, and
  with no other `ssh-keygen` on that `PATH` the runner's fault above; and a global git
  configuration of the runner's that names a `gpg.ssh.program` that does not exist, or sends the
  pack repository's address to another repository, a git attributes file of the runner's that
  turns every file's line endings to CRLF, the global one, the system one or one among its git's
  templates, and a hook among those templates that changes the anchor's manifest, under each of
  which the commit passes as it does with none;
* in the canary, a moved branch head, a repository no longer archived, a renamed principal, a
  Deprecation header on the keyed API version, a changed `/activity` count, a Zenodo archive with a
  changed byte, and a Zenodo archive and a vault tarball each resealed after a change, a valid bag
  whose tag manifest is not the release's; a Zenodo record whose archive has no link and a Software
  Heritage answer with no download address, each of which stops the run, which must still be
  recorded with what it checked before it stopped; and a token in the environment stops the canary
  before any read.

`fixpack witness`, the conformance suite, the crash adapter's exit code, the result schema and the
`VERIFYING.md` blocks it runs are checked there on sound input only, with no fault planted but the
`data/` link above, on which neither the crash adapter nor the grade can start.

## Settings

`settings/` holds the settings this repository was created with, and `settings/CREATE.md` the
commands that created it, each with the read-back that shows it in force.

## License

`REUSE.toml` names the license of each file, and `LICENSES/` holds the texts. Falden, Inc. holds the
copyright in both.

- MIT: the code that runs the checks, `ci/` and `.github/`.
- CC BY 4.0: the records, `records/`, the settings, `settings/`, and every page here (`*.md`).
