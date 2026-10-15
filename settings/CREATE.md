# How this repository was created

These are the commands that created `falden-fixtures/falden-fixture-pack-status`, from the files in
this folder, each followed by the read-back that shows it in force. They are run once, by an owner
of the `falden-fixtures` organization, with `gh` logged in as that owner. Nothing in this repository
runs them.

| file | what it sets |
|---|---|
| `repo.json` | the repository: public, its description, and issues, projects, the wiki and discussions off |
| `actions-permissions.json` | Actions on, with every action required to be pinned by its full commit |
| `workflow-permissions.json` | a workflow's token reads only, unless its job declares more, and Actions may not create or approve pull requests |
| `rulesets/1-main-no-force-push-no-delete.json` | `main` may not be force-pushed or deleted, by anyone: the ruleset has no bypass |
| `seed-commit-message.txt` | the message of the repository's first commit |
| `SHA256SUMS` | the sha256 of every other file of the first commit, as `shasum -a 256 -c` reads it, written by `git ls-files \| grep -vx settings/SHA256SUMS \| xargs shasum -a 256 > settings/SHA256SUMS` once every file is staged |

The first commit holds exactly the reviewed tree of this repository's files. Its author and committer
are `Falden <info@falden.ai>`, and it is not signed. A record is committed later by a workflow's
publish job, with the job's own token.

## The commands

`S` is a checkout of these files at the reviewed commit `REVIEWED`, and `TREE` the tree that review
names. If the block is pasted into zsh, `setopt interactivecomments` comes first, on its own line.
Each step is pasted and read in turn: a step that fails stops the creation there.

```sh
ORG=falden-fixtures; REPO=falden-fixture-pack-status
S=<the checkout>; REVIEWED=<the reviewed commit>; TREE=<the tree the review names>
gh auth status                            # an owner of falden-fixtures, with the repo and workflow scopes
# workflow missing: gh auth refresh -h github.com -s workflow first. Step 3 pushes files under
# .github/workflows/, which GitHub refuses from an OAuth token without that scope (git uses gh's login
# for github.com once gh auth setup-git has run).

# 0. the files are the reviewed ones
test "$(git -C "$S" rev-parse "$REVIEWED^{tree}")" = "$TREE" && echo "the reviewed tree"
(cd "$S" && git show "${REVIEWED}:settings/SHA256SUMS" | shasum -a 256 -c --quiet) && echo "every file as reviewed"

# 1. the repository, empty
gh api -X POST "orgs/$ORG/repos" --input "$S/settings/repo.json" \
  --jq '{full_name,visibility,default_branch,description,has_issues,has_projects,has_wiki,has_discussions}'

# 2. its Actions settings, before any workflow lands
gh api -X PUT "repos/$ORG/$REPO/actions/permissions" --input "$S/settings/actions-permissions.json"
gh api "repos/$ORG/$REPO/actions/permissions"                     # enabled true, sha_pinning_required true
gh api -X PUT "repos/$ORG/$REPO/actions/permissions/workflow" --input "$S/settings/workflow-permissions.json"
gh api "repos/$ORG/$REPO/actions/permissions/workflow"            # read, false

# 3. the first commit, the reviewed tree alone, unsigned, then the push
C=$(git -C "$S" -c user.name=Falden -c user.email=info@falden.ai -c commit.gpgsign=false \
      commit-tree --no-gpg-sign "$TREE" -F "$S/settings/seed-commit-message.txt")
git --no-pager -C "$S" log -1 --format='%an <%ae> | %cn <%ce> | %G? | %T' "$C"   # Falden <info@falden.ai> twice, N, the tree
git -C "$S" push "https://github.com/$ORG/$REPO.git" "${C}:refs/heads/main"

# 4. the ruleset, read back
gh api -X POST "repos/$ORG/$REPO/rulesets" --input "$S/settings/rulesets/1-main-no-force-push-no-delete.json" \
  --jq '{id,name,target,enforcement,bypass_actors}'

# 5. read-backs for the record
curl -sI "https://github.com/$ORG/$REPO" | head -1                # anonymous: 200
gh api "repos/$ORG/$REPO" --jq '{visibility,has_issues,has_projects,has_wiki,has_discussions}'
gh api "repos/$ORG/$REPO/rulesets" --jq '.[] | {id,name,target,enforcement,source_type}'   # this one, source_type Repository
gh api "repos/$ORG/$REPO/commits/main" --jq '{sha,tree:.commit.tree.sha,author:.commit.author,verified:.commit.verification.verified}'

# 6. the first check, at once, rather than at the next six-hour mark
gh workflow run pack-checks.yml --repo "$ORG/$REPO"
gh run list --repo "$ORG/$REPO" --workflow pack-checks.yml --limit 1
```

At each release of the pack, the release step runs the pack checks on the new tag at once:

```sh
gh workflow run pack-checks.yml --repo falden-fixtures/falden-fixture-pack-status -f ref=<the release tag>
```

If the record that run commits is infrastructure, a check that could not be run, the same line is
sent again: the six-hourly runs check such a commit again only until it holds three infrastructure
records, and after that only this line does.

GitHub turns a public repository's scheduled workflows off after 60 days without activity in it, and
before the first release no record may be committed for that long. If `gh workflow list --all` shows
either workflow disabled, both are turned on again before that line runs:

```sh
gh workflow enable pack-checks.yml --repo falden-fixtures/falden-fixture-pack-status
gh workflow enable canary.yml --repo falden-fixtures/falden-fixture-pack-status
```

## What is from GitHub's documentation, not seen here

The repository did not exist when these commands were written, and none was run against GitHub
then. `sha_pinning_required` in step 2 is the setting GitHub's REST reference names for "require
actions to be pinned to a full-length commit SHA"; if GitHub answers that it does not know the field,
the setting is made on the repository's Settings > Actions > General page instead, and the read-back
is that page. A scheduled workflow first runs within GitHub's schedule after the push. That a
record's commit, made with a publish job's `GITHUB_TOKEN`, counts as the activity that keeps the
schedules on is not seen here either; `gh workflow list --all` shows each workflow's state.
