# Midnight Core

**Autonomous Red Team Orchestration Platform** — orchestrator AI lokal untuk security assessment, tool orchestration melalui WSL/Kali Linux, dan expert report generation.

```
    __  ___     __          __  ___               
   /  |/  |__ _/ /____  ___/ / / _ \___  ___  ___ 
  / /|_/ / _ `/ __/ _ \/ _  / / // / _ \/ _ \/ _ \
 /_/  /_/\_,_/\__/\___/\_,_/ /____/\___/ \___/\___/
```

```
contributions (14 hari terakhir)
             Sn  Sl  Rb  Km  Jm  Sb  Mg  
           ┌──┬──┬──┬──┬──┬──┬──┐
sekarang   │▓▓│▓▓│░░│░░│░░│░░│░░│ (20-26 Jul)
           └──┴──┴──┴──┴──┴──┴──┘
           ┌──┬──┬──┬──┬──┬──┬──┐
minggu lalu│░░│░░│░░│░░│▓▓│▓▓│▓▓│ (13-19 Jul)
           └──┴──┴──┴──┴──┴──┴──┘
           ░░ = 0   ▓▓ = 1+ commit
           streak: 5 hari (17-21 Jul 2026)
```

---

## Fitur

- **AI Reasoning** — Ollama-based planner (midnight-agent) yang menyusun strategi pengujian keamanan secara otonom
- **Multi-Tool Orchestration** — Eksekusi tool keamanan melalui WSL/Kali Linux: Nmap, Gobuster, Nikto, FFUF, WhatWeb, SQLmap, Metasploit, Semgrep, dan lainnya
- **Expert Security Validation** — Validasi temuan terhadap database CVE, MITRE ATT&CK, dan OWASP Top 10
- **Report Generator** — Laporan otomatis dalam format HTML, Markdown, dan JSON
- **Recipe System** — Resep perintah siap copy-paste untuk berbagai profil pengujian (stealth, production-safe, full audit)
- **Security-First Planning** — Planner otomatis menyusun prioritas recon terlebih dahulu sebelum tindakan intrusif

---

## Persyaratan

| Komponen | Spesifikasi Minimum |
|----------|-------------------|
| OS | Windows 10/11 dengan WSL |
| CPU | x86_64, 8+ core |
| RAM | 16 GB |
| GPU | NVIDIA dengan CUDA (opsional, 4GB+ VRAM) |
| Storage | 30 GB free (model + tools) |
| Software | Ollama, WSL dengan Kali Linux, Python 3.12+ |

---

## Instalasi

### 1. Clone Repositori

```bash
git clone https://github.com/666midnightdev/midnight-core.git
cd midnight-core
```

### 2. Setup Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

### 3. Setup WSL + Kali Linux

```powershell
wsl --install -d kali-linux
wsl -d kali-linux
sudo apt update && sudo apt install -y nmap whatweb nikto ffuf gobuster sqlmap seclists metasploit-framework semgrep testssl
```

### 4. Setup Model Ollama

```bash
ollama create midnight-agent-fast -f Modelfile.fast
```

### 5. Konfigurasi Environment (Administrator)

```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS","16","Machine")
[System.Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE","3m","Machine")
```

Restart Ollama dari system tray.

---

## Penggunaan

### CLI Interaktif

```powershell
.\venv\Scripts\python.exe midnight_cli.py
```

Tersedia prompt interaktif dengan perintah `/command`:

| Perintah | Fungsi |
|----------|--------|
| `/run <goal>` | Jalankan security assessment dengan AI dan tool orchestration |
| `/recipe <profil> <target>` | Tampilkan resep perintah siap copy-paste |
| `/help` | Tampilkan bantuan |
| `/exit` | Keluar |

### Mode Command-Line

```powershell
.\venv\Scripts\python.exe midnight_cli.py /run "audit web https://domain-kamu.com"
.\venv\Scripts\python.exe midnight_cli.py /recipe stealth domain-kamu.com
```

### Recipe System

Resep menyediakan bundle perintah siap salin ke terminal WSL, tanpa perlu prompt satu per satu.

```powershell
# Web audit standar
.\venv\Scripts\python.exe midnight_cli.py /recipe web target.com

# Production-safe audit (domain deployed)
.\venv\Scripts\python.exe midnight_cli.py /prod target.com

# Pelan, hindari WAF
.\venv\Scripts\python.exe midnight_cli.py /recipe stealth target.com

# Audit source code lokal
.\venv\Scripts\python.exe midnight_cli.py /recipe code ./path/to/project
```

---

## Arsitektur

```
midnight-core/
├── core/                    # Orkestrator inti, security validator
│   ├── orchestrator.py      # AI task execution engine
│   └── security_validation.py # CVE/MITRE/OWASP validation
├── planner/                 # AI planning engine
│   └── planner.py           # LLM-based task decomposition
├── tools/                   # Tool definitions & registry
│   ├── registry.py          # Dynamic tool registration
│   ├── network.py           # ping, port scan
│   └── system.py            # WSL shell execution
├── executor/                # Execution layer
│   ├── wsl.py               # WSL command execution
│   ├── local.py             # Local command execution
│   └── permissions.py       # Security permission controller
├── reports/                 # Report generation
│   ├── generator.py         # Multi-format report (HTML/MD/JSON)
│   └── expert_analyzer.py   # Expert analysis pipeline
├── providers/               # LLM providers (Ollama)
│   └── ollama.py            # Ollama API client
├── config/                  # Configuration
│   └── settings.py          # Pydantic settings (env vars)
├── docs/                    # Documentation
│   ├── security_guide.md    # CVE, MITRE ATT&CK, OWASP reference
│   └── architecture.md      # Architecture overview
├── midnight_cli.py          # CLI entry point
├── recipes.py               # Tool recipe templates (Bahasa)
├── run.py                   # Orchestrator entry point
├── Modelfile                # Midnight Agent model definition
└── Modelfile.fast           # Optimized model variant
```

---

## Keamanan

- Semua eksekusi tool melalui permission controller dengan approval callback
- Model hanya untuk target yang telah diotorisasi secara eksplisit
- Validasi output terhadap database CVE dan MITRE ATT&CK untuk mencegah halusinasi
- Tidak menyimpan kredensial, token, atau informasi sensitif dalam kode

**Peringatan:** Gunakan platform ini hanya untuk pengujian keamanan pada sistem yang Anda miliki atau memiliki izin tertulis. Penggunaan tanpa otorisasi melanggar hukum yang berlaku.

---

## Lisensi

Proprietary — lihat file LICENSE untuk detail.

---

> **Midnight Core** — Built for authorized security professionals and red team operations.
