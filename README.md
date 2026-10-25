# 🏛️ TriageIQ: Automated MLOps Ticket Triage & Continuous Retraining

TriageIQ is a production-grade, 100% locally deployable MLOps platform for enterprise customer support ticket triage. It classifies incoming support tickets across 10 core queues, captures Human-in-the-Loop (HITL) feedback, monitors concept drift, and automates model retraining with zero-downtime redeployment.

---

## 🛠️ Prerequisites

Before getting started, ensure you have the following installed on your machine:
* **Python 3.11+** ([python.org](https://www.python.org/downloads/))
* **Docker Desktop** ([docker.com](https://www.docker.com/products/docker-desktop/))
* **Jenkins** (Installed natively on Windows or standalone)
* **Git**

---

## 🚀 Step-by-Step Local Setup

### 1. Clone the Repository
```powershell
git clone https://github.com/nsk724/autoTagger.git
cd autoTagger
```

### 2. Create Virtual Environment & Install Dependencies

You can use standard Python `venv` (no Conda required):

```powershell
# Create standard Python virtual environment
python -m venv .venv

# Activate the virtual environment:
# On Windows:
.venv\Scripts\activate
# On macOS / Linux:
# source .venv/bin/activate

# Install all required dependencies
pip install -r requirements.txt
```

*(Note: If you prefer Conda, you can run: `conda create -n triageiq python=3.11 -y && conda activate triageiq && pip install -r requirements.txt`)*.

---

### 3. Prepare the Dataset & Baseline Model (~40s)

Run these two one-time initialization scripts inside your active environment:

```powershell
# 1. Download dataset and create stratified parquet splits
python scripts/prepare_data.py

# 2. Train baseline hybrid TF-IDF + MiniLM classifier to artifacts/
python scripts/train_initial.py
```

---

### 4. Launch Microservices with Docker

Make sure **Docker Desktop** is running, then execute:

```powershell
docker compose up -d
```

This starts all 8 services in the background. Check their status anytime with:
```powershell
docker compose ps
```

---

## 🌐 Services, Ports & Prerequisites

All ports have been configured to prevent collisions with Windows services or Hyper-V:

| Service | Port / URL | Credentials | Description & Prerequisites |
| :--- | :--- | :--- | :--- |
| **Gateway Reviewer UI** | [http://localhost:8085](http://localhost:8085) | `reviewer1` / `reviewer1` | Nginx reverse proxy, BasicAuth, rate-limiting & human review dashboard. |
| **Model Inference API** | [http://localhost:8002/health](http://localhost:8002/health) | (No auth) | FastAPI CPU inference endpoint. Mounts local [artifacts/](file:///d:/MLOps/artifacts). |
| **Prometheus Metrics** | [http://localhost:9090](http://localhost:9090) | (No auth) | Time-series metrics engine scraping backend and feedback services every 5s. Targets at `/targets`. |
| **Grafana Dashboard** | [http://localhost:3005](http://localhost:3005) | `admin` / `admin` | Real-time monitoring dashboard (*TriageIQ Overview*) showing accuracy, error ratio vs. 0.54 threshold, and drift. |
| **Backend API** | [http://localhost:8000/docs](http://localhost:8000/docs) | Internal / Proxy | FastAPI ticket ingestion and label metadata service. |
| **Feedback Service** | [http://localhost:8001/docs](http://localhost:8001/docs) | Internal / Proxy | Human verdict ingestion & active learning ground-truth store. |
| **PostgreSQL 16** | `localhost:5433` | `triageiq` / `postgres` | Database storing tickets, predictions, and human reviews. |
| **Ticket Generator** | Internal Container | Background | Automatically replays streaming customer tickets into Gateway every 10s. |
| **Jenkins Controller** | [http://localhost:8080](http://localhost:8080) | Local Admin | CI/CD automation server running test suite, retraining, and container redeploy. |

---

### 5. Verify the System (End-to-End Smoke Test)

Run the automated integration test to verify all routes and models:

```powershell
python scripts/smoke_test.py
```
*(Confirms Gateway health, Labels, Predictions, Pending queue, Feedback intake, and Idempotency 409 handling)*.

---

### 6. Configure Jenkins CI/CD & Automated Retraining (1 Minute)

1. Open **[http://localhost:8080](http://localhost:8080)** in your browser.
2. Click **New Item** $\to$ Name: **`TriageIQ-CI-Retrain`** $\to$ Select **Freestyle project** $\to$ Click **OK**.
3. Under **Build Steps** $\to$ Click **Add build step** $\to$ **Execute Windows batch command**.
4. Enter:
   ```bat
   call scripts\ci_pipeline.bat
   ```
   *(The script automatically detects `.venv` or Conda, runs pytest, retrains the model on new feedback, and reloads `model-service`)*.
5. Click **Save** and click **Build Now**!

---

### 7. Stopping and Restarting

* **To stop without losing data**:
  ```powershell
  docker compose stop
  ```
* **To resume**:
  ```powershell
  docker compose start
  ```
* **To tear down containers (volumes preserved)**:
  ```powershell
  docker compose down
  ```
  *(Never use `docker compose down -v`, as `-v` wipes the database)*.

---

## 📖 Technical Documentation

For an in-depth explanation of system architecture, file-by-file implementation, and mathematical rationale (e.g. the 54% error rate alert threshold), see:
👉 **[docs/CODEBASE_ARCHITECTURE.md](docs/CODEBASE_ARCHITECTURE.md)**
