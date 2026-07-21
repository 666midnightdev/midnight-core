# Midnight Core: Setup & Installation Guide

This document describes the installation procedure, environment variables, configuration templates, and operations guide for the Midnight Core platform.

## Prerequisites
1. **Python 3.10+**: Ensure the Python launcher `py` or `python` is installed on your Windows host.
2. **WSL (Kali Linux)**: Required if running security assessment tools or Linux commands:
   ```bash
   wsl --install -d kali-linux
   ```
3. **Ollama**: Ensure Ollama is installed and running locally. The platform utilizes `midnight-agent` as the primary chat/reasoning model and `nomic-embed-text` as the vector embedding model.
   - Run the model creation commands:
     ```bash
     ollama create midnight-agent -f ./Modelfile
     ollama pull nomic-embed-text
     ```

## Installation & Launch Steps

### 1. Configure Python Virtual Environment
Navigate to the project root and create a virtual environment:
```bash
py -m venv venv
```

Activate the environment:
- **Windows Command Prompt**:
  ```cmd
  venv\Scripts\activate.bat
  ```
- **PowerShell**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
To customize settings, set variables in your terminal with prefix `MIDNIGHT_`:
```cmd
set MIDNIGHT_LLM__MODEL=midnight-agent
set MIDNIGHT_EXECUTOR__DEFAULT_WSL_DISTRO=kali-linux
set MIDNIGHT_DASHBOARD__PORT=8000
```

---

## Configuration Template (`config/templates/config.yaml`)

```yaml
llm:
  url: "http://localhost:11434"
  model: "midnight-agent"
  embedding_model: "nomic-embed-text"
  temperature: 0.2
  context_length: 8192

executor:
  default_wsl_distro: "kali-linux"
  timeout_seconds: 120
  allowed_commands:
    - "nmap"
    - "ping"
    - "whoami"
    - "uname"
    - "ls"
    - "cat"
    - "grep"
  auto_approve_level: "low" # options: none, low, high

storage:
  base_dir: "C:/midnight_agent/storage"
  db_path: "C:/midnight_agent/storage/midnight_core.db"
  rag_dir: "C:/midnight_agent/storage/rag"

dashboard:
  host: "127.0.0.1"
  port: 8000
  debug: false
```

---

## Operating Command Reference

### Launch the Visual Admin Dashboard Panel
```bash
python run.py dashboard
```
Open your browser and navigate to `http://127.0.0.1:8000`.

### Dispatch a Reasoning Goal via CLI
```bash
python run.py run "Scan local ports 22, 80, 443 and report findings"
```
Use `--auto-approve` to bypass CLI confirmation prompts for safe system inspect commands.

### Index files in RAG
```bash
python run.py index "C:/midnight_agent/config/settings.py"
```

### List WSL Distros
```bash
python run.py wsl-distros
```

### Run Platform Unit Tests
```bash
python run.py test
```
