# Agentic IDE: 3-Month Plan (3 People, Desktop App)

A **desktop app** (not a web app). Everything runs on your own PC.

- **Shell + UI:** Tauri (Rust) + React + TypeScript + Monaco editor
- **Agents:** two small local Python (FastAPI) services, started alongside the app
- **Database:** PocketBase, run locally as a single binary
- **Observability:** OpenTelemetry + Arize Phoenix (installed with `pip`, runs locally, no Docker)

No Docker, no cloud deployment, no scaling infrastructure. "Handling many requests" is tested locally in Week 11.

---

## 1. How this plan works

1. Each person uses an AI assistant (Claude, Claude Code, etc.) as a mentor.
2. Each week the person pastes **one prompt** (their own, from Section 6). Prompts are chained: each starts by continuing the previous week's work.
3. Before Week 0, each person pastes the **Master Prompt** (Section 5) once, at the start of their chat.
4. The goal is to **learn the workflow**: what to install and from where, which folder a file belongs in, how to run it, how to verify it, how to push it. The AI may write the code, but you must understand where it goes and why.

Weekly rhythm:

- **Mon (30 min):** each person says what demo-able thing they will ship this week.
- **Wed (15 min):** unblock or descope.
- **Fri (60 min):** demo, retro, and merge everything for the week's gate.
- **Daily:** review a teammate's PR within 4 hours.

---

## 2. Roles and responsibilities

### Person 1: Frontend + Evals/Observability
**Owns:** `apps/desktop/src/**`, `apps/desktop/package.json`, `.github/workflows/**`, `scripts/**`, `services/evals/**`, `packages/agent-obs/**`, `contracts/trace-schema.json`, `docs/EVALS.md`, `docs/FRICTION.md`.

- Build the whole app UI: Monaco editor, file tree, tabs, instructions sidebar, auth screens, profile, badges, certificates, settings, onboarding, multi-project dashboard.
- Own login/session handling in the app (PocketBase JS SDK).
- Own the **eval harness**: datasets, judges, regression gates in CI, weekly eval report.
- Own **observability**: a shared tracing package every agent uses, the Phoenix trace viewer, latency, cost, and failure-class reports, Sentry in the app.
- Own the local concurrency/load test in Week 11.
- Be the "outsider tester" in dogfood and bug-bash weeks.

### Person 2: Review Agent + Git Checkpointing
**Owns:** `services/review-agent/**`, `apps/desktop/src-tauri/src/git.rs`, `violations.rs`, `clipboard.rs`.

- Build the day-reviewer agent: it takes a diff plus the day's expected tasks, and returns notes, mistakes, solutions, and a violation flag.
- Build the Rust git layer: `init_project_repo`, `commit_checkpoint`, `get_diff_since_last_checkpoint`, `reset_to_checkpoint`, recovery from a corrupted repo, and the stash/abort policy.
- Build the paste-violation backend: `flag_violation` and, later, the clipboard-polling fallback and the unified detector.
- Own review-agent prompts, accuracy, latency, and robustness (empty, binary, and huge diffs).

### Person 3: Instructions Agent + PocketBase
**Owns:** `services/instructions-agent/**`, `pocketbase/**`.

- Build the instructions agent: `IDEA.md` goes in, a structured day-by-day `instructions.md` comes out (JSON via `instructor` + Pydantic).
- Own plan validation (stack selection, directory structure steps), regenerate-day/regenerate-plan, and instructions prompts.
- Own PocketBase: collections, migrations, multi-project schema, feedback and eval-run storage, badges and settings data, backup/export scripts.

### Shared (needs all three approvals on the PR)
`contracts/openapi.yaml`, `docs/ARCHITECTURE.md`, `docs/GIT_WORKFLOW.md`, `README.md`.

### Local ports (agreed once, never changed without telling the others)

| Thing | Port |
|---|---|
| PocketBase | 8090 |
| instructions-agent | 8001 |
| review-agent | 8002 |
| Phoenix (traces) | 6006 |

---

## 3. Folder structure

```
agentic-ide/
├── README.md
├── PLAN.md
├── .gitignore
├── .env.example                      # names of env vars only, never real keys
├── .github/
│   ├── CODEOWNERS
│   ├── pull_request_template.md
│   └── workflows/
│       ├── ci-desktop.yml            # P1: pnpm lint/typecheck + cargo check
│       ├── ci-python.yml             # P1: ruff + pytest for services
│       └── evals.yml                 # P1: eval smoke + regression gate
├── apps/
│   └── desktop/
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       ├── index.html
│       ├── src/                      # P1
│       │   ├── main.tsx
│       │   ├── App.tsx
│       │   ├── components/
│       │   │   ├── editor/           # Monaco, tabs
│       │   │   ├── filetree/
│       │   │   ├── sidebar/          # instructions view
│       │   │   ├── profile/          # badges, certificates, history
│       │   │   ├── settings/
│       │   │   └── onboarding/
│       │   ├── features/
│       │   │   ├── auth/
│       │   │   ├── projects/
│       │   │   ├── review/
│       │   │   ├── violations/
│       │   │   └── feedback/
│       │   ├── lib/                  # api client, tauri wrappers, pocketbase client, telemetry
│       │   ├── store/
│       │   └── styles/
│       └── src-tauri/
│           ├── Cargo.toml
│           ├── tauri.conf.json
│           └── src/
│               ├── main.rs           # P1
│               ├── lib.rs            # P1 (P2 adds one-line command registrations via tiny PRs)
│               ├── fs.rs             # P1
│               ├── git.rs            # P2
│               ├── violations.rs     # P2
│               └── clipboard.rs      # P2
├── services/
│   ├── instructions-agent/           # P3
│   │   ├── pyproject.toml
│   │   ├── app/
│   │   │   ├── main.py               # FastAPI app, /health
│   │   │   ├── routes/
│   │   │   ├── prompts/              # versioned prompt files (v1, v2, ...)
│   │   │   ├── schemas.py
│   │   │   └── llm.py
│   │   └── tests/
│   ├── review-agent/                 # P2 (same layout as above)
│   │   ├── pyproject.toml
│   │   ├── app/
│   │   └── tests/
│   └── evals/                        # P1
│       ├── pyproject.toml
│       ├── harness/                  # runner, scoring, reports
│       ├── judges/                   # LLM-as-judge rubrics
│       ├── datasets/
│       │   ├── instructions/         # IDEA.md samples + expected
│       │   └── review/               # diffs + expected
│       ├── reports/
│       └── run_evals.py
├── packages/
│   └── agent-obs/                    # P1: shared tracing helper used by both agents
│       ├── pyproject.toml
│       └── agent_obs/
├── pocketbase/                       # P3
│   ├── README.md
│   ├── pb_migrations/
│   ├── pb_hooks/
│   └── .gitignore                    # ignores the binary and pb_data/
├── contracts/
│   ├── openapi.yaml                  # shared
│   └── trace-schema.json             # P1
├── docs/
│   ├── IDEA.md
│   ├── ARCHITECTURE.md               # shared
│   ├── GIT_WORKFLOW.md               # shared
│   ├── EVALS.md                      # P1
│   ├── FRICTION.md                   # P1
│   └── ROADMAP.md
└── scripts/                          # P1
    ├── dev.sh                        # macOS/Linux: starts PB + both agents + Phoenix + app
    ├── dev.ps1                       # Windows equivalent
    └── hooks/
        └── pre-push                  # blocks pushes from main
```

---

## 4. Git workflow (everyone, every week)

**The one rule: nobody ever pushes directly to `main`.** All work goes on a branch, then a Pull Request (PR), reviewed by a teammate, then merged.

**Setup (once, after cloning):**
```bash
git config core.hooksPath scripts/hooks      # activates the pre-push safety hook
git config user.name "Your Name"
git config user.email "you@example.com"
gh auth login                                # GitHub CLI: https://cli.github.com
```

**Every task, in this exact order:**
```bash
git switch main
git pull                                      # always start from the latest main
git switch -c p2/week2-review-agent           # branch name: pX/weekN-short-topic
# ... do the work ...
git status                                    # see what changed
git add <specific files or folders>           # prefer specific paths over "git add ."
git commit -m "feat(review-agent): real day-reviewer with structured output"
git push -u origin p2/week2-review-agent      # first push of this branch
gh pr create --fill --base main               # opens the PR
```

**Then:**
1. A teammate reviews the PR within 4 hours (comments, then Approve).
2. CI must be green.
3. Merge with **Squash and merge**, then delete the branch.
4. Locally: `git switch main && git pull`, then start the next branch.

**If main moved while you worked:**
```bash
git fetch origin
git merge origin/main        # fix conflicts in VS Code, then: git add . && git commit
```

**Rules of thumb:**
- Keep PRs small (a day or two of work). Open one at least every 2 days.
- Only edit files you own (Section 2). If you need a change in someone else's folder, ask them or open a tiny PR and tag them.
- Never commit secrets: `.env`, API keys, `pb_data/`, the PocketBase binary. Use `.env.example` for variable names only.
- Commit message prefixes: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
- Changes to `contracts/openapi.yaml` need all three approvals.

**Branch protection note:** GitHub only enforces branch protection on **private** repos with a paid plan. Either make the repo public, or rely on the `pre-push` hook plus team discipline.

---

## 5. Master Prompt (paste once, at the very start of your chat)

Replace `[PERSON]` and `[ROLE]` with your values from Section 2.

```text
You are my senior mentor on a 3-person project: an "Agentic IDE" desktop app.
Stack: Tauri (Rust) + React + TypeScript + Monaco for the app; two local Python
FastAPI agent services; PocketBase as a local database; OpenTelemetry + Arize
Phoenix for observability. It is a desktop app that runs entirely on our own PCs.
No Docker, no cloud deployment.

I am [PERSON] and my role is [ROLE]. The team is:
- Person 1: Frontend + Evals/Observability
- Person 2: Review Agent + Git Checkpointing
- Person 3: Instructions Agent + PocketBase
The project follows the folder structure and ownership rules in PLAN.md
(sections 2 and 3). I will paste the folder structure if you ask for it.

How you must teach me:
1. My goal is to learn the WORKFLOW, not to type every line. You may write the
   code, but for every step tell me: what we are doing, why, which exact folder
   and file it belongs in (per the folder structure), the exact command to run,
   and how I verify it worked.
2. For anything I must install, give the official download link, the install
   command for my OS (ask my OS first), and a version check command.
3. Work in small numbered steps. After each group of steps, stop and ask me to
   confirm it worked before moving on. If something fails, help me read the
   error rather than guessing.
4. We work together on GitHub. NEVER let me commit or push to main. For every
   piece of work: git switch main, git pull, git switch -c pX/weekN-topic,
   commit small, git push -u origin <branch>, gh pr create. A teammate
   reviews, then squash-merge. Remind me of this at the end of every task and
   tell me which files I own vs. which belong to teammates.
5. Never put secrets (API keys, .env, pb_data) in git.
6. Each weekly prompt I send is a follow-up to the previous one. Keep the
   context of earlier weeks.

Confirm you understand, then ask me for my OS and whether Git and a GitHub
account are already set up.
```

---

## 6. Weekly prompts

Each prompt is a follow-up to the previous week's. Paste only your own.
Each ends with the **Git** step and a **Done when** check.

---

### Week 0: Setup and skeletons
**Friday gate:** all skeletons run on all 3 machines; `contracts/openapi.yaml` v0 agreed.
**Order matters:** Person 1 pushes the root skeleton on Monday/Tuesday. Persons 2 and 3 clone it after that.

#### Person 1, Week 0
```text
Week 0, Person 1. This is our first working session after the Master Prompt.

Part A: tools. Walk me through installing, with official links and version checks:
Git (https://git-scm.com/downloads), GitHub CLI (https://cli.github.com) then
`gh auth login`, VS Code, Node.js LTS (https://nodejs.org), pnpm
(https://pnpm.io/installation), Rust via rustup (https://rustup.rs), and the
Tauri v2 prerequisites for my OS (https://v2.tauri.app/start/prerequisites/).

Part B: repo. Create the GitHub repo "agentic-ide" and clone it. Create the exact
folder structure from Section 3 of PLAN.md (use .gitkeep files in empty folders).
Add README.md, PLAN.md, .gitignore (node, rust, python, .env, pb_data, PocketBase
binary), .env.example, .github/CODEOWNERS (our 3 GitHub usernames per folder
ownership), .github/pull_request_template.md, docs/IDEA.md (a stub),
docs/GIT_WORKFLOW.md (copy Section 4), and scripts/hooks/pre-push that blocks
pushes from main. This first commit is the only one allowed directly on main.
Push it, add Persons 2 and 3 as collaborators, then enable branch protection or
explain the alternative if my repo is private on a free plan.

Part C: app skeleton, on a branch. Create branch p1/week0-desktop-skeleton and
scaffold the Tauri v2 app (React + TypeScript) into apps/desktop with
`pnpm create tauri-app@latest`. Verify `pnpm tauri dev` opens a window.
Add .github/workflows/ci-desktop.yml (install, typecheck, cargo check).

Part D: observability groundwork. Create services/evals (uv project) and
packages/agent-obs (uv project) as empty skeletons. Draft contracts/trace-schema.json:
every agent call logs trace_id, agent, prompt_version, model, input, output,
tokens_in, tokens_out, latency_ms, error. Install Arize Phoenix with pip in a venv
and confirm `phoenix serve` opens on port 6006.

Git: do Part C and D on branches (p1/week0-desktop-skeleton, p1/week0-evals-skeleton),
open PRs, get a teammate review, squash-merge.
Done when: the app window opens, Phoenix UI loads, both PRs merged, CI green.
```

#### Person 2, Week 0
```text
Week 0, Person 2. This is my first working session after the Master Prompt.
Wait for Person 1 to push the root skeleton, then clone the repo.

Part A: tools. Walk me through installing, with official links and version checks:
Git (https://git-scm.com/downloads), GitHub CLI (https://cli.github.com) and
`gh auth login`, VS Code, Python 3.11+ (https://www.python.org/downloads/), uv
(https://docs.astral.sh/uv/getting-started/installation/), and Rust via rustup
(https://rustup.rs) since I will write Rust git code later. Then run the setup
steps from Section 4 of PLAN.md (hooksPath, user.name, user.email).

Part B: skeleton, on a branch. Create branch p2/week0-review-agent-skeleton.
In services/review-agent create a uv project with FastAPI and uvicorn, a
`app/main.py` with a GET /health endpoint, and a tests/ folder with one test
for /health. Run it on port 8002 and confirm it responds.

Part C: contract. Draft the POST /review endpoint in contracts/openapi.yaml:
request {diff, expected_tasks, project_id, day}, response {notes, mistakes,
solutions, violation}. Open a PR (this file needs all three approvals).

Part D: design note. In docs/ARCHITECTURE.md, add a section comparing the git2
Rust crate vs. calling the shell `git` command, pick one, and define what a
"day checkpoint" means (when it's created, what it contains, how reset works).

Git: branch p2/week0-review-agent-skeleton, PR, review, squash-merge.
Done when: /health works, the contract PR is approved, the architecture section is merged.
```

#### Person 3, Week 0
```text
Week 0, Person 3. This is my first working session after the Master Prompt.
Wait for Person 1 to push the root skeleton, then clone the repo.

Part A: tools. Walk me through installing, with official links and version checks:
Git (https://git-scm.com/downloads), GitHub CLI (https://cli.github.com) and
`gh auth login`, VS Code, Python 3.11+ (https://www.python.org/downloads/), and uv
(https://docs.astral.sh/uv/getting-started/installation/). Then run the setup
steps from Section 4 of PLAN.md (hooksPath, user.name, user.email).

Part B: PocketBase. Download the binary for my OS from https://pocketbase.io/docs/
into the pocketbase/ folder (it must be git-ignored). Run `./pocketbase serve`,
create my admin account at http://127.0.0.1:8090/_/, and create collections:
projects, days, violations, feedback, eval_runs (plus the built-in users).
Export the schema as a migration into pocketbase/pb_migrations/ so teammates can
reproduce it. Write pocketbase/README.md (exact setup steps).

Part C: skeleton, on a branch. Create branch p3/week0-instructions-skeleton.
In services/instructions-agent create a uv project with FastAPI and uvicorn, an
`app/main.py` with GET /health, and one pytest for it. Run it on port 8001.

Part D: contract. Draft POST /instructions/generate in contracts/openapi.yaml:
request {idea_md, project_id}, response {days: [{day, title, tasks[], ...}]}.
Open a PR (needs all three approvals).

Git: branches p3/week0-pocketbase and p3/week0-instructions-skeleton, PRs, review, squash-merge.
Done when: PocketBase admin loads, a teammate can recreate the DB from the README alone, /health works, contract approved.
```

---

### Week 1: First slice
**Friday gate:** a real `IDEA.md` renders as `instructions.md` in the app (integration checkpoint).

#### Person 1, Week 1
```text
Continuing from Week 0 (tools installed, repo and Tauri skeleton merged, Phoenix
running). Week 1, Person 1.

Track A: frontend. On a new branch p1/week1-editor-shell:
1. Add the Monaco editor (@monaco-editor/react) in apps/desktop/src/components/editor/.
2. Verify Monaco's onDidPaste event fires and logs to the console.
3. Add the Tauri fs and dialog plugins (docs: https://v2.tauri.app/plugin/file-system/)
   and build a file tree in components/filetree/ that opens a chosen folder.
4. Add tabbed editing (one Monaco model per open file).
5. Add a sidebar in components/sidebar/ that renders instructions from a local mock JSON file.
Explain how Tauri permissions/capabilities work, since fs access needs them.

Track B: evals. On a separate branch p1/week1-eval-harness, in services/evals:
define the dataset format (JSONL: id, input, expected, tags) in datasets/instructions/
and datasets/review/, and write the first deterministic checks (does the output
match the schema; does a day-plan contain a stack-selection step and a
directory-structure step). Write scripts/dev.sh and dev.ps1 that start PocketBase,
both agents, Phoenix, then the app.

Friday: wire the real instructions-agent (from Person 3) into the sidebar.

Git: two branches as named, small PRs, teammate reviews, squash-merge.
Done when: I can open a folder, edit in tabs, see a sidebar, and `scripts/dev.sh` starts everything.
```

#### Person 2, Week 1
```text
Continuing from Week 0 (review-agent skeleton on port 8002, /review contract
approved, git design note merged). Week 1, Person 2.

Track A: review agent stub. On branch p2/week1-review-stub: in
services/review-agent add Pydantic models matching the /review contract, and a
POST /review stub that returns mock {notes, mistakes, solutions, violation:false}.
Add a test. Then sketch the real day-reviewer prompt in app/prompts/review_v1.md:
required context is the diff plus the day's expected tasks (from instructions.md).

Track B: Rust git layer. On branch p2/week1-git-rs: in
apps/desktop/src-tauri/src/git.rs implement `init_project_repo` and
`commit_checkpoint` using the approach chosen in ARCHITECTURE.md, then
`get_diff_since_last_checkpoint`. Expose them as Tauri commands and tell me
exactly where to register them in lib.rs (a one-line change; coordinate with
Person 1). Test on a scratch repo outside the project (create a temp folder
with a few commits and verify diffs). Pair with Person 1 for 1 hour.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: /review stub responds, and from a scratch repo I can init, checkpoint, edit a file, and get a correct diff.
```

#### Person 3, Week 1
```text
Continuing from Week 0 (PocketBase running with collections, instructions-agent
/health works, contract approved). Week 1, Person 3.

On branch p3/week1-instructions-v1:
1. Set up an LLM API key from my provider's console (ask me which one), store it in a
   local .env (never commit it) and list the variable names in .env.example.
   Write app/llm.py as a small wrapper for the model call.
2. Write the first prompt in app/prompts/instructions_v1.md: IDEA.md -> instructions.md
   in a single LLM call, no structure yet. Test it with 3 different sample IDEA.md
   files and note inconsistencies in a scratch file under docs/ (not committed if messy).
3. Switch to structured output: add the `instructor` library plus a Pydantic
   response_model in app/schemas.py so the output is day-by-day JSON.
4. Implement POST /instructions/generate per the contract.
5. Add error handling and retries, plus 5 edge-case IDEA.md files saved in
   services/evals/datasets/instructions/ (tell Person 1 so you don't collide;
   they own that folder, so open a tiny PR or hand the files over).
Friday: run the agent locally so Person 1's app can call it.

Git: small PRs on branch(es) like p3/week1-instructions-v1, review, squash-merge.
Done when: POST /instructions/generate returns valid structured JSON for a real IDEA.md and retries on failure.
```

---

### Week 2: Full loop
**Friday gate:** idea → instructions → fake Day 1 → review → paste → reset + violation logged; evals ≥ 70%.

#### Person 1, Week 2
```text
Continuing from Week 1 (editor, file tree, tabs, sidebar working; eval harness
started; both agents reachable). Week 2, Person 1.

Track A: frontend. Branch p1/week2-auth-and-paste:
1. PocketBase auth: install the `pocketbase` JS SDK, build signup/login screens in
   features/auth/, and persist the session in the Tauri store plugin
   (https://v2.tauri.app/plugin/store/). Add token refresh, logout, and guarded routes.
2. When Monaco's onDidPaste fires, call Person 2's Tauri command flag_violation,
   then the review-agent, then reset via git (Person 2 builds the Rust side).
3. Add a profile page shell with empty states.

Track B: evals. Branch p1/week2-judges:
1. In services/evals/judges/ write an LLM-as-judge rubric for instructions
   (completeness, order, mandatory steps) and for reviews (did it catch the real
   bug, is it vague).
2. Hand-label 30 samples yourself and measure how closely the judge agrees with you.
3. Create packages/agent-obs with a `trace` decorator (OpenTelemetry to Phoenix),
   following contracts/trace-schema.json, and ask Persons 2 and 3 to import it.
4. Add services/evals smoke run to .github/workflows/evals.yml on every PR to a service.
Gate: both agents score ≥ 70%.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: login persists across app restarts, a paste triggers the violation flow, and the eval gate prints ≥ 70%.
```

#### Person 2, Week 2
```text
Continuing from Week 1 (/review stub, git.rs with init/checkpoint/diff). Week 2, Person 2.

Branch p2/week2-real-reviewer:
1. Build the real day-reviewer in services/review-agent: diff + expected tasks ->
   structured output matching the contract (use `instructor`). Version the prompt
   as review_v1.md.
2. Self-check it against the 10 sample diffs Person 1 keeps in
   services/evals/datasets/review/. Note failures.
3. Import `agent_obs` (from Person 1's packages/agent-obs) and trace every review call.

Branch p2/week2-reset-and-violation:
1. In src-tauri/src/git.rs finish `reset_to_checkpoint`; test on a real repo with
   real commits.
2. In violations.rs add the Tauri command `flag_violation` (called when a paste is detected).
3. Handle edge cases: empty diff, binary files.
4. Pair with Person 1 for the paste -> flag -> review -> reset wiring.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: a real diff produces a real structured review, paste -> reset works end to end, and review eval ≥ 70%.
```

#### Person 3, Week 2
```text
Continuing from Week 1 (generate endpoint with structured output). Week 2, Person 3.

Branch p3/week2-plan-validation:
1. Add day-plan validation in services/instructions-agent: reasonable length and
   mandatory stack-selection and directory-structure steps; retry or repair when missing.
2. Import `agent_obs` (Person 1's packages/agent-obs) and trace every generate call.
3. Iterate the prompt (instructions_v2.md) until the instructions eval from
   Person 1 scores ≥ 70%.

Branch p3/week2-schema:
1. PocketBase schema evolution as real data flows: projects.completed,
   violations.count, timestamps. Create migrations in pocketbase/pb_migrations/,
   commit them, and tell Persons 1 and 2 to pull and re-run them.
2. Make sure a violation record can be written (project_id, day, timestamp, source).

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: invalid plans get repaired, traces appear in Phoenix, schema migrations apply cleanly on a teammate's machine, instructions eval ≥ 70%.
```

---

### Week 3: Real data and hardening
**Friday gate:** profile live on real data; git edge cases handled.

#### Person 1, Week 3
```text
Continuing from Week 2 (auth, paste flow, judges, tracing package, eval smoke in CI).
Week 3, Person 1.

Track A: frontend. Branch p1/week3-profile-and-polish:
1. Wire the profile page to real PocketBase data (projects, violation history).
2. Editor save flow with an unsaved-changes indicator.
3. Keyboard shortcuts (save, command palette stub).
4. Loading and error states on every API call surface (create a shared pattern in lib/).

Track B: evals. Branch p1/week3-eval-growth:
1. Grow the instructions dataset to 25+ IDEA.md samples and the review dataset to
   20 diffs (ask Persons 2 and 3 for tricky cases; label them).
2. Confirm traces from both agents appear in Phoenix; build a saved Phoenix view
   that shows latency and errors per agent.
3. Write the first weekly report in docs/EVALS.md: scores, what failed, what changed.

Also review Person 2's reset UX and polish the violation feedback message.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: the profile shows real data, error states exist, EVALS.md has a first report with the new dataset sizes.
```

#### Person 2, Week 3
```text
Continuing from Week 2 (real reviewer, reset, flag_violation). Week 3, Person 2.

Branch p2/week3-git-hardening:
1. Policy for uncommitted changes at reset time: decide stash vs. abort, document it
   in ARCHITECTURE.md, and implement it in git.rs.
2. Corrupted-repo recovery: reinit from the last good checkpoint.
3. First-day-with-no-prior-commit edge case.
4. Add Rust tests for each case in apps/desktop/src-tauri (cargo test).

Branch p2/week3-review-quality:
1. Review the instructions prompt changes Person 3 made against eval regressions
   (pair-review their PR).
2. Check the review eval after Person 1 grows the dataset and fix the top failures.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: every git edge case has a passing test and the review eval is reported in EVALS.md.
```

#### Person 3, Week 3
```text
Continuing from Week 2 (validation, schema migrations, traced generate). Week 3, Person 3.

Branch p3/week3-instructions-quality:
1. Test instruction quality on 3 more idea types: an API, a CLI tool, and a game.
   Add them to the instructions dataset (hand them to Person 1 via a tiny PR).
2. Add a 'regenerate day plan' option: per day and for the full plan (new endpoint,
   update the contract with a PR everyone approves).
3. Re-run evals and fix regressions.

Branch p3/week3-backup:
1. Write a PocketBase backup/export script in pocketbase/ (plus README steps to restore).
2. Test a restore on a second machine or a fresh folder.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: regenerate works per-day and full-plan, the dataset has 25+ items, and a backup restores cleanly.
```

---

### Week 4: Month 1 dogfood
**Friday gate:** 2 clean full-day dogfood runs; evals ≥ 80%; all must-fix bugs ticketed.

#### Person 1, Week 4
```text
Continuing from Week 3 (profile, error states, bigger datasets, first EVALS.md).
Week 4, Person 1.

Mon-Tue, branch p1/week4-dogfood-fixes: fix the friction items the team logged (UI
blockers first). Create GitHub Issues for each bug with labels (must-fix / later).
Wed: act as the student for a real mini-project day (use the full loop from
IDEA.md to review) and log every friction point in docs/FRICTION.md.
Thu: also log friction in the others' areas; fix mine.
Fri: turn failed runs into new eval cases (branch p1/week4-eval-from-dogfood),
re-run the eval suite, and compare to the 80% target in docs/EVALS.md. Run the
Month-1 retro and write the FRICTION.md summary.

Git: small PRs per fix, teammate review, squash-merge.
Done when: 2 clean full-day runs happen, the evals show ≥ 80% or a written reason why not, all must-fix bugs are ticketed.
```

#### Person 2, Week 4
```text
Continuing from Week 3 (git edge cases, review quality). Week 4, Person 2.

Branch p2/week4-dogfood-fixes: fix review-agent wrong-note patterns and
checkpointing issues the dogfood found. Play the student for a full day and log
friction in FRICTION.md (via a small PR or by handing notes to Person 1). Add
dogfood failures to the review eval dataset (tiny PR to services/evals/datasets/review/
or send to Person 1). Gate review: share eval scores and retro input.

Git: small PRs, teammate review, squash-merge.
Done when: your dogfood bugs are fixed or ticketed and review eval ≥ 80%.
```

#### Person 3, Week 4
```text
Continuing from Week 3 (regenerate, backup, bigger instruction dataset). Week 4, Person 3.

Branch p3/week4-dogfood-fixes: fix unclear day-plan issues and schema/query
problems found in dogfood. Play the student for a full day and log friction.
Add dogfood failures as new cases to the instructions dataset (hand to Person 1).
Gate review: instructions eval ≥ 80%; write month-1 closeout notes in docs/.

Git: small PRs, teammate review, squash-merge.
Done when: your dogfood bugs are fixed or ticketed and instructions eval ≥ 80%.
```

---

### Week 5: Multi-project and feedback capture
**Friday gate:** multiple concurrent projects per user work end to end.

#### Person 1, Week 5
```text
Continuing from Week 4 (dogfood fixes, evals ≥ 80%). Week 5, Person 1.

Track A: frontend. Branch p1/week5-multi-project:
1. Multi-project dashboard in features/projects/: create, switch, and archive projects.
2. State management for the active project; keep editor state per project.
3. UI polish and empty states.

Track B: evals. Branch p1/week5-eval-regression-gate:
1. Make the eval workflow fail a PR if the score drops more than an agreed threshold
   versus main (store the baseline score in services/evals/reports/).
2. Add a prompt-version comparison report: run the same dataset with two prompt versions.

Git: branches as named, small PRs, teammate review, squash-merge.
Done when: I can create 2 projects, switch between them with separate editor state, and a PR with a worse prompt fails CI.
```

#### Person 2, Week 5
```text
Continuing from Week 4. Week 5, Person 2.

Branch p2/week5-accuracy:
1. Accuracy sprint: run the review agent against 10 intentionally buggy submissions
   (create them in services/evals/datasets/review/ via a tiny PR to Person 1).
2. Tune the mistake-detection prompt (review_v2.md) from the results.
3. Add a feedback endpoint to the review-agent: POST /review/feedback
   {review_id, thumbs, comment}. Update the contract with a PR everyone approves.
Pair with Person 3 so feedback gets stored in PocketBase.

Git: small PRs, teammate review, squash-merge.
Done when: review accuracy on buggy samples improves and feedback can be posted.
```

#### Person 3, Week 5
```text
Continuing from Week 4. Week 5, Person 3.

Branch p3/week5-multi-project-schema:
1. Multi-project support in PocketBase: relations and cascade rules (migrations in
   pocketbase/pb_migrations/).
2. Data migration for existing single-project data (a script, tested on a copy).
3. Feedback storage: the feedback and eval_runs collections wired up with Person 2.
4. Improve regenerate-plan options based on dogfood feedback.

Git: small PRs, teammate review, squash-merge.
Done when: users can own multiple projects, migrations run cleanly on a teammate's DB, feedback saves.
```

---

### Week 6: Quality flywheel and observability
**Friday gate:** user feedback lands in the eval sets weekly.

#### Person 1, Week 6
```text
Continuing from Week 5 (multi-project, regression gate in CI). Week 6, Person 1.

Track A: frontend. Branch p1/week6-feedback-ui:
1. Thumbs up/down + comment on every review output in features/feedback/, calling
   Person 2's feedback endpoint.
2. Feedback UI polish and error states.
3. Add Sentry to the desktop app (https://docs.sentry.io; ask me to create a free
   project and keep the DSN in .env).

Track B: evals/observability. Branch p1/week6-flywheel:
1. Write a script in services/evals/ that reads feedback from PocketBase and exports
   low-rated reviews as eval candidates.
2. Label 20 candidates and add them to the review dataset.
3. Build a Phoenix view of cost (tokens) and latency per prompt version.

Git: small PRs, teammate review, squash-merge.
Done when: a thumbs-down in the app appears as a candidate case, and the Phoenix view shows tokens per review.
```

#### Person 2, Week 6
```text
Continuing from Week 5. Week 6, Person 2.

Branch p2/week6-prompt-v2:
1. Iterate the review prompt (review_v3.md) from the 20 labeled samples.
2. Log tokens per review (via agent_obs) and flag outliers.
3. Confirm eval trend is flat or rising with Person 1's regression gate.

Git: small PRs, teammate review, squash-merge.
Done when: review score rises on the new labeled set and no PR fails the regression gate.
```

#### Person 3, Week 6
```text
Continuing from Week 5. Week 6, Person 3.

Branch p3/week6-instructions-v3:
1. Label 20 instruction samples with Person 1 and iterate the prompt (instructions_v3.md).
2. Add cost tracking (tokens per generate call) via agent_obs.
3. Confirm Sentry or error logging in the instructions agent (tell Person 1 which
   exceptions you want surfaced).

Git: small PRs, teammate review, squash-merge.
Done when: instructions score rises on the labeled set and costs are visible per call.
```

---

### Week 7: Accuracy and reliability sprint
**Friday gate:** evals ≥ 85% trending; CI fully green; cross-OS smoke run.

#### Person 1, Week 7
```text
Continuing from Week 6 (feedback UI, flywheel script, Sentry). Week 7, Person 1.

Track A: frontend. Branch p1/week7-polish:
1. Cross-OS smoke test on Windows, macOS, and Linux (use all three teammates'
   machines): write a short checklist in docs/ and record results.
2. Fix the top 5 UI papercuts from docs/FRICTION.md.
3. Finish the error and loading state audit; improve editor startup and file-tree
   load on large folders.

Track B: evals/observability. Branch p1/week7-failure-taxonomy:
1. Classify every eval failure for both agents (missed bug / false positive / vague
   note; vague day / missing step / wrong stack) into a table in docs/EVALS.md.
2. Report p50 and p95 latency per agent from Phoenix.
3. Write a cost-per-review summary.

Git: small PRs, teammate review, squash-merge.
Done when: the cross-OS checklist is filled in, the taxonomy table exists, and the latency numbers are in EVALS.md.
```

#### Person 2, Week 7
```text
Continuing from Week 6. Week 7, Person 2.

Branch p2/week7-top-failure: take the top failure class from Person 1's taxonomy,
fix it, and add 10 eval cases for it. Then branch p2/week7-latency: optimize review
latency (for example, parallelize diff chunking) and verify p95 under 30 seconds
on a 100-sample run (a script under services/review-agent/tests/ or services/evals/).

Git: small PRs, teammate review, squash-merge.
Done when: the top failure class has a measurable improvement and p95 < 30s.
```

#### Person 3, Week 7
```text
Continuing from Week 6. Week 7, Person 3.

Branch p3/week7-instructions-failures: fix the top instructions failure class and
add 10 eval cases. Branch p3/week7-db-and-contracts: audit PocketBase indexes and fix
slow queries; add contract tests so every endpoint in contracts/openapi.yaml is
exercised by a test (target 100% of endpoints).

Git: small PRs, teammate review, squash-merge.
Done when: the failure class is improved, slow queries are fixed, and contract tests cover all endpoints.
```

---

### Week 8: Month 2 dogfood and gate
**Friday gate:** month-2 must-fix = 0; evals ≥ 85%; flywheel produced measurable prompt gains.

#### Person 1, Week 8
```text
Continuing from Week 7. Week 8, Person 1.

Mon-Tue (branch p1/week8-dogfood-fixes): fix the friction batch for month 2 and
log must-fix items as GitHub Issues. Wed: act as the student on a full real day
and log friction. Thu: fix my own bugs and review the telemetry/trace data for
strange behavior. Eval work (branch p1/week8-judge-check): re-run the judge on
the 30 hand-labeled samples and measure agreement again; if it dropped, fix the
rubric. Update EVALS.md with the month-2 trend chart and gate result.

Git: small PRs, teammate review, squash-merge.
Done when: must-fix = 0, evals ≥ 85%, and EVALS.md shows the trend and flywheel gain.
```

#### Person 2, Week 8
```text
Continuing from Week 7. Week 8, Person 2.

Branch p2/week8-dogfood-fixes: fix review-agent friction and git hardening issues
from the student run; play the student and log friction. Grow the review eval set
to 40+ diffs (tiny PR to Person 1's datasets folder) and keep the full regression
suite under 10 minutes. Gate review input.

Git: small PRs, teammate review, squash-merge.
Done when: your must-fix items are zero and the suite runs under 10 minutes.
```

#### Person 3, Week 8
```text
Continuing from Week 7. Week 8, Person 3.

Branch p3/week8-dogfood-fixes: fix instructions-agent and DB issues from the student
run; play the student and log friction. Grow the instructions set to 50+ IDEA.md
samples (hand to Person 1) and keep the regression suite under 10 minutes. Month-2 closeout notes.

Git: small PRs, teammate review, squash-merge.
Done when: your must-fix items are zero and the suite runs under 10 minutes.
```

---

### Week 9: Profile completion and violation defense
**Friday gate:** badges and certificates live; clipboard-polling fallback detects pastes.

#### Person 1, Week 9
```text
Continuing from Week 8. Week 9, Person 1.

Track A: frontend. Branch p1/week9-profile:
1. Badges UI (earned/locked) in components/profile/.
2. Completion certificate UI per project, with a shareable export (PNG or PDF).
3. Violation history with dates on the profile.

Track B: evals. Branch p1/week9-violation-evals: build a detection test suite for
the 4 paste vectors (editor paste, context menu, keyboard shortcut, clipboard
polling): record detection rate and false-positive rate in a table in EVALS.md.
Research with me how Tauri's clipboard plugin (https://v2.tauri.app/plugin/clipboard/)
behaves per OS and document the findings for Person 2.

Git: small PRs, teammate review, squash-merge.
Done when: badges and certificates render from real data and the 4-vector table exists.
```

#### Person 2, Week 9
```text
Continuing from Week 8. Week 9, Person 2.

Branch p2/week9-violation-detector: in src-tauri/src/clipboard.rs implement a
throttled clipboard-polling fallback; in violations.rs build a unified detector
(editor paste + context menu + shortcut + polling) with a single decision point.
Do a false-positive tuning session. Write unit tests for all 4 vectors (cargo test).

Git: small PRs, teammate review, squash-merge.
Done when: all 4 vectors are detected through one decision point with tests passing.
```

#### Person 3, Week 9
```text
Continuing from Week 8. Week 9, Person 3.

Branch p3/week9-badges: design the badge/certificate data model and a rules engine
in PocketBase (migrations + hooks in pb_hooks/); award logic triggers on project
completion. Branch p3/week9-settings: settings schema (theme, font size, keybindings)
and the endpoints/collection rules the app needs.

Git: small PRs, teammate review, squash-merge.
Done when: completing a project awards a badge in the DB and settings can be saved and read.
```

---

### Week 10: OS parity, settings, onboarding
**Friday gate:** violation detection verified on Windows/macOS/Linux; settings screen live.

#### Person 1, Week 10
```text
Continuing from Week 9. Week 10, Person 1.

Track A: frontend. Branch p1/week10-settings-onboarding:
1. Settings UI: theme, font size, keybindings, persisted and applied live (use the
   Tauri store plugin).
2. First-launch walkthrough shell in components/onboarding/.
3. Guided "write your first IDEA.md" step using Person 3's sample template.

Track B: observability. Instrument time-to-first-instructions (from first launch to
first rendered instructions.md) as a trace or event and report it in EVALS.md.
Also run the paste-vector tests on my OS and record results in docs/.

Git: small PRs, teammate review, squash-merge.
Done when: settings persist and apply, onboarding walks through to a generated plan, and the time-to-first-instructions number exists.
```

#### Person 2, Week 10
```text
Continuing from Week 9. Week 10, Person 2.

Branch p2/week10-os-hardening: run the paste-vector tests on Windows, macOS, and
Linux (borrow teammates' machines), document OS-specific edge cases in
ARCHITECTURE.md, and fix the Rust/Tauri differences that the testing exposes.

Git: small PRs, teammate review, squash-merge.
Done when: the OS matrix is filled in and the detector passes on all three.
```

#### Person 3, Week 10
```text
Continuing from Week 9. Week 10, Person 3.

Branch p3/week10-keybindings-onboarding: keybindings storage with conflict detection;
onboarding content and sample project template endpoint (so the guided flow
has an IDEA.md to start from). Add the contract changes with a PR everyone approves.

Git: small PRs, teammate review, squash-merge.
Done when: keybinding conflicts are rejected and the sample template endpoint works.
```

---

### Week 11: Onboarding, robustness, local load test
**Friday gate:** a new user reaches `instructions.md` in under 5 minutes (measured).

#### Person 1, Week 11
```text
Continuing from Week 10. Week 11, Person 1.

Track A: frontend. Branch p1/week11-onboarding: wire onboarding end to end;
polish first-run and empty states from my own observations.

Track B: load testing (local, no cloud). Branch p1/week11-load-test:
1. Write a script in services/evals/ using Python's asyncio + httpx that sends 20
   concurrent POST /review requests to the review-agent on port 8002 and 20
   concurrent /instructions/generate requests to port 8001.
2. Record success rate, p50/p95 latency, and errors; check them in Phoenix.
3. Document in EVALS.md what breaks first and share the findings with Persons 2 and 3.

Git: small PRs, teammate review, squash-merge.
Done when: a new person reaches instructions.md in < 5 min and the load-test report exists.
```

#### Person 2, Week 11
```text
Continuing from Week 10. Week 11, Person 2.

Branch p2/week11-robustness:
1. Handle malformed and empty diffs; chunk huge diffs.
2. Define a timeout + retry contract with Person 1 (what the app shows on timeout).
3. Fix the issues Person 1's load test found, and re-verify the latency budget.

Git: small PRs, teammate review, squash-merge.
Done when: odd diffs don't crash the agent and the load test passes the p95 < 30s budget.
```

#### Person 3, Week 11
```text
Continuing from Week 10. Week 11, Person 3.

Branch p3/week11-cost-controls: caching for identical requests and per-user daily
caps (stored in PocketBase), plus tests so a cost regression fails CI. Branch
p3/week11-backup-drill: a backup/restore drill — wipe a test pb_data folder and
restore from backup.

Git: small PRs, teammate review, squash-merge.
Done when: repeated identical requests hit the cache, caps are enforced, and the restore drill succeeds.
```

---

### Week 12: Bug bash, performance, final gate
**Friday gate:** all month-3 features demoed; bug bash done; installers build; v0.1.0 tagged.

#### Person 1, Week 12
```text
Continuing from Week 11. Week 12, Person 1.

Branch p1/week12-bug-bash:
1. Bug bash as an outsider: use the whole app and file GitHub Issues for everything
   (label P0/P1/P2); fix the P0/P1 issues in my area.
2. Performance budgets: Monaco with a 10k-line file, and editor startup < 2 s.
   Measure, record, and fix the worst offender.
3. Packaging check: run `pnpm tauri build` and install the result on my machine;
   document any issues.
4. Final report in docs/EVALS.md: scores over the 12 weeks, cost, latency,
   failure classes, and a "known limitations" section.

Git: small PRs, teammate review, squash-merge.
Done when: P0/P1 issues are closed, perf numbers are recorded, an installer built and runs, and the final report is merged.
```

#### Person 2, Week 12
```text
Continuing from Week 11. Week 12, Person 2.

Branch p2/week12-bug-bash: bug bash pass in review agent and git areas; fix P0/P1
issues. Measure git ops: target < 500 ms on a repo with 500 commits (write a
benchmark in Rust, record the baseline). Write docs/GIT_CHECKPOINTING.md
(internals + recovery guide). Do the final end-to-end run on my machine.

Git: small PRs, teammate review, squash-merge.
Done when: P0/P1 are closed, the git benchmark passes the budget, and the recovery guide is merged.
```

#### Person 3, Week 12
```text
Continuing from Week 11. Week 12, Person 3.

Branch p3/week12-bug-bash: bug bash pass in instructions agent and DB areas; fix
P0/P1 issues. Write pocketbase/README.md updates and docs/SETUP.md: a full-stack
setup guide a stranger could follow. Do the final end-to-end run on my machine.
Then (only after all three PRs are merged) tag the release: git switch main,
git pull, git tag v0.1.0, git push origin v0.1.0.

Git: small PRs, teammate review, squash-merge.
Done when: P0/P1 are closed, the setup guide works for someone who hasn't seen the project, and v0.1.0 is tagged.
```

---

## 7. After Month 3 (not in this plan)

Beta cohorts, feedback-driven roadmap, marketplace/extensions, public launch, and installers with code signing.