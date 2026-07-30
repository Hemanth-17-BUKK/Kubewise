# KubeWise services

This repository contains three independent Python services. Each service has its own
virtual environment, dependency file, configuration template, and startup command.
Do not run `pip install -r requirements.txt` with the system Python: use the service's
`.venv` interpreter so dependencies stay isolated from the global Python installation.

| Service | Purpose | Local URL |
| --- | --- | --- |
| `cluster-service` | Assumes an AWS role and lists EKS clusters. | `http://127.0.0.1:8001` |
| `monitoring-service` | Connects to EKS and reads Kubernetes resources and metrics. | `http://127.0.0.1:8002` |
| `installer-service` | Checks or installs Prometheus on an EKS cluster. | `http://127.0.0.1:8003` |

## Prerequisites

- Git
- Python 3.12 (the version used by the Docker images). Verify with `python --version`.
- AWS credentials supplied through an AWS profile, IAM role, or standard AWS environment
  variables. The identity must be able to call STS and assume the role supplied to the API.
- For `installer-service`, install [Helm](https://helm.sh/docs/intro/install/) and make
  sure `helm` is available on `PATH`.
- Network access to AWS/EKS. Kubernetes access also requires the assumed role to have the
  appropriate EKS and Kubernetes RBAC permissions.

## First-time setup

Run the following once from the repository root in PowerShell. These commands create one
environment per service and install dependencies only into that service's `.venv`.

```powershell
$services = 'cluster-service', 'monitoring-service', 'installer-service'

foreach ($service in $services) {
    Push-Location "services/$service"
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    Copy-Item .env.example .env
    Pop-Location
}
```

Edit each generated `.env` to suit your environment. `.env` files and `.venv` directories
are deliberately ignored by Git; `.env.example` files are committed templates and must not
contain credentials.

If you already have a local `.env`, do not overwrite it. Skip the `Copy-Item` line and
compare it with `.env.example` instead.

### Setting up one service

To set up just one service, replace `<service>` below with its directory name:

```powershell
Set-Location services/<service>
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

You can activate the environment for an interactive shell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, either run `Set-ExecutionPolicy -Scope Process Bypass` for
the current terminal or use `.\.venv\Scripts\python.exe` directly, as all commands in this
README do.

## Running locally

Open a separate terminal for each service. From the service directory, run its command:

```powershell
# cluster-service
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001

# monitoring-service
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8002

# installer-service
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8003
```

Open `http://127.0.0.1:<port>/docs` for the FastAPI Swagger UI. Health endpoints are:

- Cluster service: `GET /health`
- Monitoring service: `GET /`
- Installer service: `GET /health`

## AWS and security notes

- Prefer AWS IAM roles or `aws configure` profiles over long-lived keys in `.env`.
- The APIs accept a target `roleArn`; the credentials running the service need permission to
  call `sts:AssumeRole` for that role.
- Never commit `.env`, `.venv`, generated Python cache files, or AWS credentials.
- If a credential was committed previously, rotate it. Adding it to `.gitignore` prevents
  future commits but does not remove it from Git history.

## Dependency maintenance

Install new packages only through the relevant service environment, then add the package to
that service's `requirements.txt`:

```powershell
Set-Location services/cluster-service
.\.venv\Scripts\python.exe -m pip install <package>
.\.venv\Scripts\python.exe -m pip freeze > requirements.txt
```

Review the resulting dependency file before committing it. The services are intentionally
separate: do not share one root virtual environment or install their requirements globally.
