# TrailRelay

TrailRelay is an offline-first trail hazard reporting system that uses local AI to classify reports and GitHub Issues to track hazards.

The project aims to make trail hazard reporting more resilient when network connectivity is unreliable.

## Features

- **Offline-first reporting:** Store hazard reports locally in the browser using IndexedDB.
- **AI-powered classification:** Use Gemma 3 1B through Ollama to classify hazard descriptions.
- **Workflow orchestration:** Use Temporal to coordinate report processing and retry failed activities.
- **GitHub integration:** Create GitHub Issues for processed hazard reports.
- **Automatic synchronization:** Attempt to synchronize pending reports when connectivity returns.
- **Simple web interface:** Submit and review hazard reports through a browser.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Local storage:** IndexedDB
- **AI model:** Gemma 3 1B
- **AI runtime:** Ollama
- **Backend:** Python, FastAPI
- **Workflow orchestration:** Temporal
- **Issue tracking:** GitHub Issues
- **Infrastructure:** Docker Compose

## How It Works

1. A user submits a trail hazard description through the web interface.
2. The report is stored locally in the browser.
3. When the backend is reachable, the frontend attempts to synchronize the report.
4. FastAPI submits the report to a Temporal workflow.
5. The workflow uses the local AI model to classify the hazard.
6. A GitHub Issue is created to track the report.
7. After successful synchronization, the report is removed from the local pending queue.

## Prerequisites

Before running TrailRelay, install:

- Python 3
- Git
- Docker and Docker Compose
- Ollama
- A GitHub repository with Issues enabled
- A GitHub personal access token with the permissions required to read and create issues

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/AkshajShetty012/TrailRelay.git
cd TrailRelay
```

### 2. Set up the Python environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Linux and macOS**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Set up Ollama

Install Ollama by following the instructions at [ollama.com](https://ollama.com/).

Download the required model:

```bash
ollama pull gemma3:1b
```

Ensure Ollama is running and the model is available before submitting reports.

### 4. Start Temporal

Use the official [Temporal Docker Compose repository](https://github.com/temporalio/docker-compose) and follow its setup instructions.

Configure and start Temporal with PostgreSQL. TrailRelay expects the Temporal service to be accessible at `localhost:7233`.

The Temporal Web UI is typically available at [http://localhost:8080](http://localhost:8080).

### 5. Configure GitHub access

Create a GitHub personal access token with the necessary permissions to read and create issues in the target repository.

Set the following environment variables in the terminal where the worker will run:

```bash
export GITHUB_REPO="OWNER/REPOSITORY"
export GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
```

Replace the example values with your repository details and token.

For Windows PowerShell:

```powershell
$env:GITHUB_REPO = "OWNER/REPOSITORY"
$env:GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
```

Keep your token private and never commit credentials to the repository.

### 6. Start the Temporal worker

From the project directory, with the Python virtual environment activated and GitHub environment variables configured, run:

```bash
python run_trailrelay.py worker
```

Keep the worker running.

### 7. Start the backend API

Open another terminal in the project directory and activate the Python virtual environment.

Run:

```bash
uvicorn api:app --host 127.0.0.1 --port 8000
```

The API health endpoint is available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

### 8. Start the frontend

Open another terminal in the project directory and run:

```bash
python -m http.server 5500 --directory frontend
```

Open [http://localhost:5500](http://localhost:5500) in your browser.

## Testing

1. Submit a sample hazard report through the frontend.
2. Verify that the report is stored locally.
3. Check that the backend accepts the report.
4. Inspect the workflow execution in the Temporal Web UI.
5. Check GitHub Issues for the resulting hazard report.
6. Test offline storage and synchronization when connectivity returns.

## Project Status

TrailRelay is a working prototype demonstrating offline report storage, local AI classification, workflow orchestration, and GitHub issue creation.