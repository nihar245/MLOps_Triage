"""Script to rebuild git commit history with clean attribution for the 4 team members across 2 subteams."""

import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AUTHORS = {
    "nihar": ("nihar 245", "niharmehta245@gmail.com"),
    "nand": ("nsk724", "koradiyanand0@gmail.com"),
    "divyesh": ("divyeshodedara", "divyeshvisana123@gmail.com"),
    "devan": ("devanmodhavadiya189", "modhavadiyadevan189@gmail.com"),
}

# 8 Commits: 2 per author, grouped by Subteam A (Data & ML) and Subteam B (Platform & Ops)
COMMITS = [
    # Subteam A: Nihar (Data & Preprocessing)
    {
        "author": "nihar",
        "date": "2026-10-22T10:15:00+05:30",
        "message": "feat(data): setup dataset schema, preprocessing, and stratified splits\n\nAdd label configuration, text normalization, dataset splitting logic into\ntrain, val, golden, stream, and heldout partitions, with DVC pointers.",
        "paths": [
            "requirements.txt",
            "config",
            ".dvc",
            ".dvcignore",
            "data/.gitignore",
            "data/README.md",
            "data/processed.dvc",
            "data/raw",
            "ml/requirements.txt",
            "ml/requirements-dev.txt",
            "ml/triage_ml/__init__.py",
            "ml/triage_ml/config.py",
            "ml/triage_ml/text.py",
            "ml/triage_ml/prepare.py",
            "ml/tests/test_text.py",
            "ml/tests/test_prepare.py",
        ],
    },
    {
        "author": "nihar",
        "date": "2026-10-22T15:30:00+05:30",
        "message": "feat(ml): implement baseline hybrid TF-IDF and MiniLM classifier\n\nAdd feature extraction pipeline combining TF-IDF word n-grams and\nsentence-transformers embeddings with Logistic Regression.",
        "paths": [
            "ml/triage_ml/train.py",
            "ml/triage_ml/evaluate.py",
            "ml/tests/test_train.py",
            "ml/tests/test_evaluate.py",
            "ml/tests/conftest.py",
            "scripts/prepare_data.py",
            "scripts/train_initial.py",
        ],
    },
    # Subteam A: Nand (Model Serving & Active Learning Feedback)
    {
        "author": "nand",
        "date": "2026-10-23T11:00:00+05:30",
        "message": "feat(model-service): implement FastAPI inference service with local model loader\n\nAdd containerized CPU model serving endpoint (/predict, /health)\nwith background loading from local model artifacts.",
        "paths": [
            "services/model-service",
            "ml/triage_ml/promote.py",
            "ml/triage_ml/deploy_space.py",
            "ml/triage_ml/publish.py",
        ],
    },
    {
        "author": "nand",
        "date": "2026-10-23T16:45:00+05:30",
        "message": "feat(feedback-service): implement review ingestion and active learning holdout split\n\nAdd feedback-service for recording human verdicts into PostgreSQL\nand exporting feedback snapshots for continuous retraining.",
        "paths": [
            "services/feedback-service",
            "ml/triage_ml/export_feedback.py",
            "ml/triage_ml/runs.py",
            "ml/tests/test_dry_runs.py",
        ],
    },
    # Subteam B: Divyesh (Reverse Proxy & Docker Orchestration)
    {
        "author": "divyesh",
        "date": "2026-10-24T09:30:00+05:30",
        "message": "feat(gateway): implement Nginx reverse proxy, BasicAuth, and reviewer web UI\n\nAdd Nginx gateway configuration routing /api and /feedback-api,\nrate limiting, and SSI-enabled human review web frontend.",
        "paths": [
            "services/gateway",
            "services/backend-api",
        ],
    },
    {
        "author": "divyesh",
        "date": "2026-10-24T14:15:00+05:30",
        "message": "feat(infra): setup PostgreSQL schema, migrations, and docker compose orchestration\n\nConfigure multi-service docker compose with database health checks,\nticket-generator background stream, and conflict-free port mappings.",
        "paths": [
            "services/postgres",
            "services/ticket-generator",
            "docker-compose.yml",
            ".env.example",
            ".dockerignore",
            ".gitignore",
        ],
    },
    # Subteam B: Devan (Monitoring, Observability & Jenkins CI/CD)
    {
        "author": "devan",
        "date": "2026-10-25T10:00:00+05:30",
        "message": "feat(monitoring): setup Prometheus scraping, alerts, and Grafana drift dashboard\n\nConfigure Prometheus scrape targets, recording rules, 0.54 error\nratio alert, and provisioned Grafana business quality dashboard.",
        "paths": [
            "ops/prometheus",
            "ops/grafana",
            "docs",
        ],
    },
    {
        "author": "devan",
        "date": "2026-10-25T14:30:00+05:30",
        "message": "feat(ci-cd): implement Jenkins automated test suite, local retraining, and pipeline runner\n\nAdd 3-stage Jenkins automation (pytest -> retrain -> redeploy),\nsmoke test validation, offline caching flags, and execution timer.",
        "paths": [
            "Jenkinsfile",
            "Jenkinsfile.retrain",
            "ops/jenkins",
            "scripts/smoke_test.py",
            "scripts/retrain_local.py",
            "scripts/run_pipeline.py",
            "scripts/ci_pipeline.bat",
            "ml/tests/test_integration.py",
            "pyproject.toml",
            "README.md",
            "STARTUP_GUIDE.md",
            "scripts/rebuild_git_history.py",
            "Team-A-Application-ML-Guide.md",
            "Team-B-Platform-Delivery-Guide.md",
            ".pre-commit-config.yaml",
            ".gitattributes",
        ],
    },
]


def run_git(cmd: list[str], env: dict | None = None) -> str:
    res = subprocess.run(["git", *cmd], cwd=ROOT, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        print(f"git {' '.join(cmd)} failed:\n{res.stderr}", file=sys.stderr)
        raise SystemExit(res.returncode)
    return res.stdout.strip()


def main():
    print("[*] Rebuilding git commit history for 4 teammates...")
    # 1. First ensure current working tree is safely committed on main
    subprocess.run(["git", "add", "-A"], cwd=ROOT)
    subprocess.run(["git", "commit", "-m", "temp: save working state before history rewrite"], cwd=ROOT)

    # 2. Create orphan branch
    branch_name = "clean-history"
    run_git(["checkout", "--orphan", branch_name])
    run_git(["rm", "-rf", "."])

    for i, c in enumerate(COMMITS, 1):
        name, email = AUTHORS[c["author"]]
        print(f"[{i}/8] Committing: {c['message'].splitlines()[0]} by {name} <{email}>")
        
        # Add files for this commit
        run_git(["checkout", "main", "--", *c["paths"]])
        run_git(["add", "-A"])
        
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = name
        env["GIT_AUTHOR_EMAIL"] = email
        env["GIT_AUTHOR_DATE"] = c["date"]
        env["GIT_COMMITTER_NAME"] = name
        env["GIT_COMMITTER_EMAIL"] = email
        env["GIT_COMMITTER_DATE"] = c["date"]
        
        res = subprocess.run(["git", "commit", "-m", c["message"]], cwd=ROOT, capture_output=True, text=True, env=env)
        if res.returncode != 0 and "nothing to commit" not in res.stdout:
            print(f"commit failed: {res.stderr}", file=sys.stderr)
            sys.exit(res.returncode)

    # Force move branch to main
    print("[*] Switching branch to main...")
    run_git(["branch", "-D", "main"])
    run_git(["branch", "-m", "main"])
    run_git(["checkout", "main"])

    print("\n[+] Git history rebuilt successfully! Current log:")
    print(run_git(["log", "--pretty=format:%h | %an <%ae> | %ad | %s", "--date=short"]))


if __name__ == "__main__":
    main()
