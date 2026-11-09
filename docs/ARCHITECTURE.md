## Git layer: git2 crate vs. shell `git`

Owner: Person 2 (`apps/desktop/src-tauri/src/git.rs`)

### Options compared

| | `git2` crate (libgit2 bindings) | Shell `git` via `std::process::Command` |
|---|---|---|
| Setup | Adds a C dependency (libgit2, and OpenSSL on some platforms). This can slow builds and cause cross-OS issues. | No extra crate. It only needs `git` on the user's PATH. |
| API | Typed Rust API, but verbose (index, trees, signatures, oids). | Plain commands we already know: `git add -A`, `git commit`, `git diff`. |
| Behavior | Close to git but not identical (some config, hooks and attributes behave differently). | Exactly what the student's own git does. Easy to reproduce by hand. |
| Error handling | Typed errors. | Exit code plus stderr text, which we must parse. |
| Performance | Fast, in-process. | Process spawn per call (about tens of ms), fine for our budget (< 500 ms). |
| Debugging | Harder to reproduce a bug without writing Rust. | Copy the failing command into a terminal. |
| Dependency risk | None at runtime (compiled in). | Git must be installed on the user's machine. |

### Decision: shell `git`

We call the `git` CLI from Rust. Reasons: easier to debug and test on three OSes, no libgit2 build problems, behavior matches what students and teammates see in their own terminal, and our operations are few and simple. Our budget (git ops < 500 ms on 500 commits) is achievable with process spawning.

Trade-offs we accept: git must be installed (the app checks `git --version` at startup and shows a clear error if missing), and we parse command output. All calls go through one helper in `git.rs` that sets the working directory, captures stdout/stderr, and returns a typed error. We always run with `-c core.hooksPath=/dev/null`-style isolation as needed so a student's hooks don't interfere, and we never run git with user-supplied strings unescaped (arguments are passed as separate args, never through a shell).

If benchmarks in Week 12 show shell spawning misses the budget, we can revisit `git2` behind the same function signatures.

### What is a "day checkpoint"?

A day checkpoint is a git commit that marks the exact state of the student's project at the **start of a day**, so we can (a) diff what they did that day and (b) restore that state if they violate the rules.

**When it is created**
- On project creation: `init_project_repo` runs `git init` and makes the first commit (the empty or starter project) as the checkpoint for Day 1.
- After a day is reviewed and accepted, `commit_checkpoint(day)` snapshots the work as the baseline for the next day.

**What it contains**
- A commit of the whole working tree (`git add -A`, respecting `.gitignore`).
- Commit message: `checkpoint: day N`.
- A lightweight tag `checkpoint/day-N` pointing at the commit, so we can find it without parsing history.
- Never included: `.env`, secrets, `node_modules`, `pb_data/` (covered by the project's `.gitignore`).

**How the diff works**
- `get_diff_since_last_checkpoint` runs `git diff <latest checkpoint tag>` (including untracked files by staging them in a temporary index) and returns it to the review agent.

**How reset works**
- `reset_to_checkpoint(day)` restores the working tree to the tagged commit: `git reset --hard checkpoint/day-N` followed by `git clean -fd` to remove new untracked files.
- This is destructive. The policy for uncommitted changes (stash vs. abort) is decided in Week 3 and will be documented here. Until then, a reset triggered by a violation proceeds and the violation is logged first.
- If the repo is corrupted, recovery (Week 3) re-inits from the last good checkpoint.