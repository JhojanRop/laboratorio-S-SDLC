# AGENTS.md

Instructions for AI coding agents working on this repository.

Read this file before making any change. If an instruction here conflicts with a
user request, stop and ask for clarification instead of guessing.

---

## 1. Purpose

This repository is an **intentionally vulnerable Flask laboratory** used to
practice Secure SDLC (S-SDLC) concepts. It must only be run in a local, isolated
environment for educational purposes.

The goal of this document is to keep every agent session consistent:

- Respect the project structure and tooling.
- Follow the Git workflow.
- Do not mix different kinds of work in a single task.
- Preserve the intentional vulnerabilities until a task explicitly addresses
  them.

---

## 2. Technology Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | Python 3.12 | Pinned in `.python-version` |
| Dependency manager | `uv` | Do not use `pip install` directly |
| Web framework | Flask 3.1.x | Intentionally vulnerable application |
| Database | SQLite (`academia.db`) | Generated locally, never committed |
| Linting / formatting | `ruff` | Replaces `black`, `isort`, `flake8`, `pyupgrade` |
| Security analysis | `bandit` | Advisory mode for now |
| Commit messages | `commitlint` + Conventional Commits | Enforced by a `commit-msg` hook |
| Pre-commit hooks | `pre-commit` | Runs on every commit |
| Git workflow | Simplified Git Flow | `main` + `dev` + short-lived branches |

---

## 3. Task Types (Strict)

Every session must be classified into **exactly one** of the following task
types. Do not mix them. If the user asks for work outside the current type,
stop and ask to switch task type first.

### 3.1 Planning

**Purpose:** Decide what to do, how, and in what order.

- Allowed: analysis, proposals, plans, task breakdowns, architecture decisions.
- Forbidden: editing source code, editing documentation files, changing the Git
  state (no commits, branches, merges, pushes, or index changes). Read-only Git
  commands (`git status`, `git diff`, `git log`) are allowed for context.
- Output: an agreed plan that can be executed in a later task.

### 3.2 Code

**Purpose:** Implement, fix, or refactor source code and technical configuration.

- Allowed: Python files, templates, static assets, and tool configuration
  (`pyproject.toml`, `.pre-commit-config.yaml`, runner/config files).
- Forbidden: editing project documentation (`README.md`, `BITACORA.md`,
  `AGENTS.md`, docs) and changing the Git state (no commits, branches, merges,
  pushes, or index changes).
- Output: code ready to be reviewed and committed in a separate Git task.

### 3.3 Documentation

**Purpose:** Write or update project documentation only.

- Allowed: `README.md`, `BITACORA.md`, `AGENTS.md`, Markdown files under `docs/`,
  and explanatory docstrings/comments.
- Forbidden: changing business logic, fixing bugs, editing technical
  configuration, and changing the Git state (no commits, branches, merges,
  pushes, or index changes).
- Output: documentation ready to be reviewed and committed in a separate Git
  task.

### 3.4 Git

**Purpose:** Manage the repository history and collaboration workflow.

- Allowed: creating branches, staging, committing, merging (`--no-ff`), tags,
  pushing, opening Pull Requests, resolving conflicts, and managing branch
  protection.
- Forbidden: adding new features or writing documentation as part of this task.
  Files may only change to resolve merge conflicts or to complete an already
  approved commit.
- Output: a clean, reviewed history and integrated branches.

---

## 4. Git Workflow

### 4.1 Long-lived branches

- `main`: production-ready code and releases. **Protected**: no direct pushes,
  changes only through Pull Requests.
- `dev`: integration branch. Features and fixes are integrated here first.

### 4.2 Short-lived branches

| Type | Pattern | Created from | Merged into |
|------|---------|--------------|-------------|
| Feature | `feat/<name>` | `dev` | `dev` |
| Bug fix | `fix/<name>` | `dev` | `dev` |
| Refactor | `refactor/<name>` | `dev` | `dev` |
| Documentation | `docs/<name>` | `dev` | `dev` |
| Hotfix | `hotfix/<name>` | `main` | `main` and `dev` |

> **Small-change exception:** if the change is very small (typo, one-line fix,
> minor configuration tweak), do not create a new branch. Commit directly to
> `dev`. When in doubt, use a short-lived branch.

### 4.3 Merge rules

- Always merge supporting branches with `git merge --no-ff`.
- Never push directly to `main`; use Pull Requests.
- `dev` may receive direct commits only for the small-change exception above.
- After a `hotfix` is merged into `main`, merge the same branch into `dev`
  immediately so the fix is not lost in the next release.
- Delete short-lived branches after they are merged.

### 4.4 Commit messages

Use Conventional Commits, for example:

```text
feat: add login validation
fix: correct session handling
docs: update setup instructions
chore: update development dependencies
```

The `commitlint` hook validates the message format on every commit.

---

## 5. Code Quality

- Use `uv` for all dependency and environment operations.
- Run `ruff check` and `ruff format` before committing.
- Run `uv run pre-commit run --all-files` before opening a Pull Request.
- Do not introduce `black`, `isort`, `flake8`, or `pylint`; `ruff` covers those
  responsibilities.
- Do not edit `uv.lock` manually. This project intentionally does not version
  `uv.lock`; do not force-add it to Git.

---

## 6. Security Rules (Shift-Left)

- Never commit real secrets: `.env`, private keys, tokens, credentials, or
  production configuration.
- `bandit` findings in this repository are **advisory for now** because the
  application contains deliberate vulnerabilities. Do not remove or silence
  them unless the task explicitly asks to fix that vulnerability.
- `academia.db` and the contents of `uploads/` must never be committed.
- Do not enable `debug=True` outside a local, isolated development environment.
- When a security fix is implemented, document why in the Pull Request and, if
  relevant, in `BITACORA.md`.

---

## 7. Key Commands

| Command | Purpose |
|---------|---------|
| `uv sync --dev` | Install development dependencies |
| `uv run app.py` | Run the laboratory locally |
| `uv run ruff check .` | Lint the code |
| `uv run ruff format --check .` | Check formatting without modifying files |
| `uv run bandit -r app.py database.py` | Run the security analysis |
| `uv run pre-commit run --all-files` | Run every pre-commit hook |
| `uv lock --check` | Verify that the lockfile matches `pyproject.toml` |

---

## 8. Anti-Patterns

- Do not install packages with `pip install`; use `uv add`.
- Do not commit directly to `main` or `dev`.
- Do not commit `academia.db`, `uploads/*`, `.env`, or generated reports.
- Do not remove intentional vulnerabilities without an explicit task and
  documentation.
- Do not mix Planning, Code, Documentation, and Git work in one session.
- Do not rewrite history destructively (`git reset --hard`, force-push) unless
  the user explicitly asks for it.

---

## 9. Available OpenCode Agents

The following specialized agents are available in this environment:

| Agent | Scope | Use it for |
|-------|-------|------------|
| `bitacora` | Documentation | Technical decision logs and high-level change notes |
| `readme` | Documentation | Creating or updating `README.md` |
| `git` | Git | Commit grouping, branch management, history safety |

Rules:

- These agents do not replace this `AGENTS.md`; they must follow it too.
- Use the `git` agent for any Git-changing task. It must not commit or push
  without explicit user approval.
- Use `bitacora` or `readme` only for documentation tasks.
- If a new project-specific agent is added, document it in this section.

---

## 10. Updating This Document

`AGENTS.md` is treated as project documentation:

1. Change it only during a **Documentation** task.
2. Propose changes through a `docs/<name>` branch and a Pull Request to `dev`.
3. Merge with `--no-ff` after review.
4. Never edit it directly on `main`.

---

## 11. Session Checklist

Before starting:

- [ ] Identify the task type (Planning, Code, Documentation, or Git).
- [ ] Confirm the working branch and repository state.
- [ ] Read the relevant files before changing them.

Before finishing:

- [ ] Stay within the selected task type.
- [ ] Run the checks relevant to the task.
- [ ] Report what changed and what was intentionally left untouched.
