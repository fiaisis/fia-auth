# AGENTS.md

Guidance for coding agents working in this repository.

## What this repo is

`fia-auth` is a FastAPI authentication and authorization microservice for the Flexible Interactive
Automation (FIA) system (see `README.md`). It:
- Authenticates users against the STFC User Office Web Service (`UOWS`) via `POST /login`, issuing a
  short-lived HS256 access JWT in the response body and setting a 12-hour `HttpOnly`, `Secure`,
  `SameSite=Lax` `refresh_token` cookie.
- Determines a user's role (`user` vs. `staff`) by checking a lightweight `staff` table in
  PostgreSQL alongside UOWS role lookups.
- Verifies and refreshes access tokens via `POST /verify` and `POST /refresh`.
- Exposes `GET /maintenance` and `GET /scheduled_maintenance` (always returning `show=False`,
  required by the SciGateway host frontend contract) plus `/healthz` and `/ready` probes.
- Exposes an internal endpoint `GET /experiments?user_number=<int>` (protected by
  `Authorization: Bearer <FIA_AUTH_API_KEY>`) that queries the STFC Proposal Allocations GraphQL API
  and returns the list of experiment (`RB`) numbers for that user.

## Position in the FIA service

### Overarching FIA architecture

FIA is a multi-repository system (all checked out as siblings under the same parent workspace
directory) that automatically reduces instrument data, and also lets users browse, plot, and rerun
that data interactively:

```text
[ISIS Instrument Archive (/archive, /imat) & lastrun.txt]
        │
        ▼
  file-watcher (Kopf Operator + Per-Instrument Watcher Pods)
        │  publishes file path to RabbitMQ: `watched-files`
        ▼
  run-detection ◄──── fetches instrument rules (`GET /instrument/{inst}/specification`) ────► FIA-API
        │  ingests .nxs metadata, verifies rules, publishes JobRequest JSON
        │  to RabbitMQ: `scheduled-jobs` (or retries via `failed-watched-files`)
        ▼
  jobcontroller (job_creator) ◄──── requests PreScript (`GET /script/{inst}`) & posts Job ──► FIA-API ◄──► autoreduction-scripts
        │  spawns Kubernetes Job in cluster:
        ├──► Main container: runners (`ghcr.io/fiaisis/mantid` or `mantid-imaging`) -> writes reduced data to `/ceph`
        └──► Sidecar container: jobcontroller (job_watcher) -> updates job status/outputs in FIA-API (`PATCH /job/{id}`)

[Interactive / Web & Live Data Paths]
  scigateway (Host App) ──► frontend (FIA React Plugin)
                                ├──► fia-auth (THIS REPO) (UOWS login, JWT verify/refresh, `/experiments` RB lookup)
                                ├──► FIA-API (runs, jobs, scripts, specifications, reruns -> `watched-files` / `scheduled-jobs`)
                                └──► plotting-service (h5grove NeXus/HDF5 & IMAT image serving from `/ceph` & `/imat`)

  Kafka (`<INST>_events`, `<INST>_sampleEnv`, `<INST>_runInfo`)
        └──► live-data (Live Data Operator + Mantid Live Data Processor fetching `/live-data/{inst}/script` from FIA-API)

  LLSP (Long Lived Script Processors: `LLSP-API` + RabbitMQ + Celery `LLSP-Worker` built on `ghcr.io/fiaisis/mantid`)

[Infrastructure & Deployment]
  k8s (Terraform + Ansible for OpenStack clusters, Redpanda, local Minikube)
  gitops (ArgoCD App-of-Apps & Kustomize `base`/`envs`/`variants` manifests for all FIA services)
```

### This repository's location (upstream, downstream & siblings)

- **Role**: Central authentication authority and user-to-experiment (`RB` number) resolver for the
  interactive FIA web/API tier.
- **Upstream callers (who calls `fia-auth`)**:
  - `scigateway` (`../scigateway`) and `frontend` (`../frontend`) — call `/login`, `/verify`,
    `/refresh`, `/maintenance`, and `/scheduled_maintenance` via the configured `authUrl`.
  - `FIA-API` (`../FIA-API`) — calls `GET /experiments` (authenticated with `FIA_AUTH_API_KEY`) and
    verifies JWTs signed with the shared `JWT_SECRET` when checking experiment access.
  - `plotting-service` (`../plotting-service`) — calls `GET /experiments` (via `FIA_AUTH_URL` and
    `FIA_AUTH_API_KEY`) and verifies JWTs when authorizing access to reduced data files.
- **Downstream dependencies (what `fia-auth` calls or reads)**:
  - STFC User Office Web Service (`UOWS_URL`, authenticated with `UOWS_API_KEY`) — REST API for
    credential authentication and role lookups.
  - STFC Proposal Allocations GraphQL API (`ALLOCATIONS_URL`) — GraphQL queries for a user's RB
    numbers.
  - PostgreSQL (`postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:5432/fia`) — stores the
    `staff(id, user_number)` table managed via SQLAlchemy.
  - `gitops` (`../gitops`) — `.github/workflows/build_and_push.yml` builds and pushes
    `ghcr.io/fiaisis/fia-auth` on every push to `main` and automatically updates the image digest in
    `./components/fia-auth/envs/staging/fia-auth.yml`.
- **Sibling repositories to check when changing contracts**: `../FIA-API` and
  `../plotting-service` (JWT payload claims, `JWT_SECRET`, and `GET /experiments` response format),
  `../frontend` / `../scigateway` (`/login`, `/verify`, `/refresh`, `/maintenance`, and
  `/scheduled_maintenance` routes), and `../gitops` (`components/fia-auth/` manifests and secrets).

### Core technologies
- **Python**: version/minimum is defined by `requires-python` in `pyproject.toml` — do not hardcode a
  version here; always check `pyproject.toml` and `.github/workflows/` before creating an
  environment.
- **FastAPI** + **uvicorn**: Web framework and ASGI server.
- **PyJWT** + **cryptography**: HS256 access/refresh JWT generation and verification.
- **SQLAlchemy** + **psycopg2**: PostgreSQL connectivity and ORM for the `staff` table.
- **gql** (`gql[all]`) + **requests**: GraphQL and REST clients for Proposal Allocations and UOWS.
- **pytest** (+ `pytest-cov`, `pytest-random-order`): Unit and Postgres-backed E2E testing.
- **ruff**: Linting and formatting (`line-length = 120`, rules in `pyproject.toml`).
- **mypy**: Static type checking (`mypy --strict fia_auth`).
- **Docker**: Containerization (`container/fia-auth.Dockerfile`).

---

## Repository structure

```
fia_auth/                    Application source package — FastAPI app entrypoint, routers (`/login`,
                              `/verify`, `/refresh`, `/experiments`, `/maintenance`,
                              `/scheduled_maintenance`, `/healthz`, `/ready`), UOWS auth client,
                              Proposal Allocations GraphQL client, JWT token handling, role lookup,
                              SQLAlchemy `staff` model/session setup, and custom exceptions

test/                        Pytest test suite — unit tests for auth, tokens, roles, and models at
                              top level, plus `test/e2e/` (Postgres-backed end-to-end tests for
                              auth, db, experiments, and maintenance routes)

container/                   Production Dockerfile (`fia-auth.Dockerfile`)
.github/workflows/           CI/CD workflows: tests.yml, formatting-and-linting.yml,
                              build_and_push.yml, codeql.yml, scorecards.yml, dependency-review.yml
pyproject.toml               Single source of truth for package metadata, pinned dependencies,
                              optional extras, and ruff configuration
```

---

## `pyproject.toml` — read this first

`pyproject.toml` is the single source of truth for dependencies, extras, and tool config. Read it
before adding dependencies, changing supported Python versions, or modifying lint/type rules:

- Runtime dependencies and optional extras (`formatting`, `test`, `all`) are pinned with `==` — keep
  any new dependencies pinned the same way.
- `requires-python` defines the minimum supported Python version; check it and `.github/workflows/`
  before creating a local environment.
- Ruff (`[tool.ruff]`, `[tool.ruff.lint]`) enforces `line-length = 120` and a wide rule set
  (docstrings `D`, bandit `S`, bugbear `B`, pathlib `PTH`, type-checking `TCH`, no print `T20`,
  pylint `PL`, etc.). Check `[tool.ruff.lint.ignore]` before "fixing" intentionally ignored rules.
- CI runs `mypy --strict fia_auth`.

---

## Configuration (environment variables)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `JWT_SECRET` | `"shh"` *(insecure test default)* | Symmetric secret used to sign and verify HS256 JWTs |
| `UOWS_API_KEY` | *(required for live UOWS calls)* | API key for STFC User Office Web Service requests |
| `FIA_AUTH_API_KEY` | `"shh"` *(insecure test default)* | Bearer token required by `GET /experiments` |
| `DB_USERNAME` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | `password` | PostgreSQL password |
| `DB_IP` | `localhost` | PostgreSQL host (connects to port `5432`, database `fia`) |
| `UOWS_URL` | `https://devapi.facilities.rl.ac.uk/users-service` | Base URL for UOWS REST API |
| `ALLOCATIONS_URL` | `https://devapi.facilities.rl.ac.uk/proposal-allocations/graphql` | GraphQL endpoint for Proposal Allocations |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `10` | Lifetime of issued access tokens in minutes |

*(Note from `README.md`: `refresh_token` cookies are set with `Secure=True` and `SameSite=Lax`.
Browsers over plain HTTP may not store the cookie during local debugging; prefer API clients like
`curl`/`httpie` or run behind HTTPS.)*

---

## Environment & running commands

Do not assume any particular machine already has a conda env, kubectl context, or virtualenv set up
— check what is available first. Prefer `conda` when available (`command -v conda` on Linux/macOS or
`where conda` on Windows); fall back to a Python `venv` only if conda is not installed.

1. Check existing conda environments:
   ```shell
   conda env list
   ```
   If a matching env exists (e.g. `fia-auth`), use it with `conda run -n <env-name> <command>` or
   `conda activate <env-name>`.
2. If no suitable conda env exists but `conda` is installed, create one using the Python version
   from `pyproject.toml` / `.github/workflows/`:
   ```shell
   conda create -n fia-auth python=<version-from-pyproject.toml-or-CI> -y
   conda run -n fia-auth pip install ".[all]"
   ```
3. Only if `conda` is not installed, fall back to a virtualenv:
   ```shell
   python3 -m venv .venv        # Linux/macOS (use `python` on Windows)
   . .venv/bin/activate         # POSIX shell (.venv\Scripts\Activate.ps1 on PowerShell)
   pip install ".[all]"
   ```

### Running the service, tests & linting
- **Run development server** (OpenAPI UI at `http://127.0.0.1:8000/docs`):
  ```shell
  conda run -n <env-name> uvicorn fia_auth.fia_auth:app --reload
  ```
- **Unit tests, linting & type checking (default for all changes)**:
  ```shell
  conda run -n <env-name> pytest test --ignore=test/e2e --random-order --random-order-bucket=global
  conda run -n <env-name> ruff check .
  conda run -n <env-name> ruff format --check .
  conda run -n <env-name> mypy --strict fia_auth
  ```
- **E2E tests** (require a running PostgreSQL instance on `localhost:5432` with user `postgres`,
  password `password`, and database `fia` — see `.github/workflows/tests.yml` and
  `test/e2e/conftest.py`, which automatically creates the SQLAlchemy tables):
  ```shell
  conda run -n <env-name> pytest test/e2e --random-order --random-order-bucket=global
  ```
- **Docker build** (from repo root, per `README.md`):
  ```shell
  docker build -f container/fia-auth.Dockerfile -t fia-auth:local .
  ```

## Kubernetes commands

Available kubectl contexts vary per machine/operator — always run `kubectl config get-contexts`
first before targeting a cluster. Never rely on the current context; always pass `--context`
explicitly at the **end** of the command:

```shell
kubectl get pods -n fia --context <context-name>
kubectl logs deploy/fia-auth -n fia --context <context-name>
```

Double- and triple-check the context name before running anything against a production-like cluster.

## Managing issues

This repo has no local `.github/ISSUE_TEMPLATE/`; GitHub serves the org-wide default template from
`fiaisis/.github` instead. Always use it rather than inventing an ad hoc issue format:

```shell
gh issue create --template Issue
```

Check `gh issue list` / `gh issue view <number>` first to avoid duplicates.

## Branch naming

Branches use `snake_case` descriptions of the work being done. Do not use category prefixes like
`feature/` or `fix/`.

- **Format**: `description_of_work` (e.g. `add_maintenance_route`, `update_agent_guidelines`).

## Commit messages

`main`'s history (`git log --oneline main`) is predominantly **squash merges**: one commit per PR,
titled `<PR title> (#<PR number>)`. This has two practical consequences:

- **The PR title is what actually survives into permanent history.** Individual commits on a working
  branch are squashed on merge, so getting the PR title right (see "Pull request process" below)
  matters more than crafting a commit-by-commit history.
- **Individual commit messages still matter for review and for the squash commit body.** By default,
  GitHub's squash merge concatenates every commit subject on the branch into the squashed commit's
  body. Write each commit as a focused, reviewable unit of work with a clear, imperative-mood
  summary line (and a short *why* body paragraph on non-trivial commits) — avoid noise like `wip` or
  `fix` that would leak into the squashed body. Leave auto-generated Dependabot commit messages as-is.

## Requirements for code changes

Only run tests, linters, and type checkers when they are **relevant to the files you actually
changed** — if a change only touches documentation (e.g. `.md` files), skip `pytest`, `ruff`, and
`mypy`. When you do change Python code, dependency manifests, or configuration, before considering
the change complete:
1. **Add or update unit tests** in `test/` for any new or changed behavior.
2. **Add or update e2e tests** in `test/e2e/` (Postgres-backed) when the change affects routes,
   token flows, or DB behavior that suite already exercises.
3. **Run the linter and type checker** (`ruff check .`, `ruff format .`, `mypy --strict fia_auth`)
   and fix everything reported — don't just rely on CI's auto-fix commit.
4. **Run both the unit and e2e suites with coverage** and confirm coverage has not regressed
   compared to `main` (CI uploads both runs to Codecov; locally, add `--cov-report=term-missing` to
   the `pytest` commands in "Environment & running commands").

## Pull request process

1. **Local validation** before opening a PR (when `.py` / `pyproject.toml` / container files are
   changed; skip for `.md`-only changes):
   ```shell
   conda run -n <env-name> pytest test --ignore=test/e2e --random-order --random-order-bucket=global
   conda run -n <env-name> ruff check .
   conda run -n <env-name> ruff format .
   conda run -n <env-name> mypy --strict fia_auth
   ```
   Note: the CI workflow (`.github/workflows/formatting-and-linting.yml`) also runs `ruff format .`,
   `ruff check --fix`, and `mypy --strict fia_auth` on every non-`main` push and auto-commits any
   fixes back to the branch as `"Formatting and linting commit"`.
2. **PR title**: a clear, concise description in normal grammar/sentence case. Do not use
   `snake_case` for PR titles.
3. **PR description**: use the org-wide default template from `fiaisis/.github`
   (`.github/pull_request_template.md` — no local override in this repo), which is just
   `Closes # <Issue Number>` followed by a `## Description` section. Ask the user for the issue
   number if one isn't evident from the task, or confirm there is none to link.
4. **AI-assistance label**: attach a label to the PR indicating that it was made with the assistance
   of AI. Check existing labels first with `gh label list` (e.g. `AI` or `AI_code` in this org) and
   apply the matching label via `gh pr create --label <label>` or
   `gh pr edit <number> --add-label <label>`; if the repo does not have an AI label yet, create one
   first (`gh label create "AI" --description "Created with the assistance of AI"`).

## Handling Dependabot PRs

Dependabot creates PRs grouped as `python-packages` (weekly), `action-packages` (daily, GitHub
Actions), and `docker` (daily, `/container`) per `.github/dependabot.yml`. When asked to handle
these:

1. **List and identify**: `gh pr list` to find open Dependabot PRs.
2. **Review changes**: `gh pr diff <number>`, paying close attention to major version bumps in
   `pyproject.toml`, `container/fia-auth.Dockerfile`, or `.github/workflows/`.
3. **Validate**:
   - Python/dependency changes: `gh pr checkout <number>`, install updated dependencies
     (`pip install ".[all]"`), and run unit tests, `ruff`, and `mypy --strict fia_auth`.
   - Docker/Action changes: verify CI checks pass with `gh pr checks <number>`.
4. **Approve and merge** once validation passes:
   ```shell
   gh pr review <number> --approve
   gh pr merge <number> --merge
   ```
   Use `--admin` if blocked by branch protection (`gh pr merge <number> --merge --admin`).
5. **Clean up**: close redundant/superseded PRs with `gh pr close <number> --delete-branch`.
6. **Final verification**: checkout `main`, pull latest changes, and re-run
   `pytest test --ignore=test/e2e` to confirm `main` is green.

## General working practices

- Prefer the `read` tool (with `offset`/`limit`) over `sed -n`, `cat`, or similar shell one-liners
  when inspecting file contents, and prefer the `write` and `edit` tools over `bash` (`cat <<EOF`,
  `sed -i`, `echo >`), Python one-liners, or other non-tool-based commands whenever creating or
  modifying files.
- Ask the user a clarifying question whenever a task is ambiguous (e.g. JWT claim changes that
  affect downstream services, UOWS/Allocations schema assumptions, or whether an issue number exists
  to link in a PR) rather than guessing.
- Keep dependency versions pinned with `==` in `pyproject.toml` consistent with the existing style.

## Keeping this document up to date

If a change you make would make any information in this `AGENTS.md` inaccurate or incomplete —
e.g. a new route or environment variable, a changed database table or directory layout, a
new/renamed CI workflow, an updated Dependabot grouping, a new sibling-repo contract, or a different
testing/linting command — update the relevant section of this file as part of the same change. Treat
it the same way you would treat `README.md`: documentation that goes stale is worse than no
documentation, so don't leave it to a future agent or PR to notice the drift.
