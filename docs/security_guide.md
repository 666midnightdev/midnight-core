# 🛡️ Midnight Core — Security Reference Guide

Panduan referensi cepat untuk CVE, MITRE ATT&CK, dan OWASP yang digunakan oleh
`SecurityValidator` di Midnight Core. Gunakan ini saat menganalisis temuan agar
tidak halusinasi dan selalu menyertakan bukti konkret.

---

## 1. CVE → MITRE ATT&CK Mapping (Contoh)

| CVE | Nama | Kategori | MITRE Equivalent |
|-----|------|----------|------------------|
| CVE-2021-34527 | PrintNightmare | Printer RCE | T1059.001 (PowerShell) |
| CVE-2021-44228 | Log4Shell | Log4j RCE | T1059.001 (PowerShell) |
| CVE-2021-3620 | Sudo Heap Overflow | Privilege Escalation | T1068 |
| CVE-2021-35041 | F5 LFI | Path Traversal | T1548 |
| CVE-2021-26855 | Exchange ProxyLogon | Web Proxy Bypass | T1078 |
| CVE-2023-23397 | Outlook Elevation | Privilege Escalation | T1068 |

**Aturan:** Setiap kali output alat menyebut CVE, validasi terhadap tabel di atas
sebelum melaporkan. Jika CVE tidak ada di database, tandai sebagai `UNVERIFIED`.

---

## 2. OWASP Top 10 Checklist (2021)

- [ ] **A01 — Broken Access Control**: cek `access denied`, `forbidden`, `403`
- [ ] **A02 — Cryptographic Failures**: cek transmisi plaintext, cipher lemah
- [ ] **A03 — Injection**: cek `sql injection`, `xss`, `command injection`, `csrf`
- [ ] **A04 — Insecure Design**: cek logika bisnis yang bisa dilewati
- [ ] **A05 — Security Misconfiguration**: cek `debug mode`, default password
- [ ] **A06 — Vulnerable Components**: cek versi usang / deprecated
- [ ] **A07 — Auth Failures**: cek weak password, MFA tidak ada
- [ ] **A08 — Integrity Failures**: cek update tanpa signature
- [ ] **A09 — Logging & Monitoring Failures**: cek tidak ada audit log
- [ ] **A10 — SSRF**: cek permintaan ke internal URL

---

## 3. Playbook Incident Response (Sederhana)

| Pola Terdeteksi | Kemungkinan | Respon Cepat |
|-----------------|-------------|--------------|
| Banyak file dihapus serentak | Ransomware | Isolate host → snapshot forensik |
| PowerShell encode aneh | Living-off-land | Dump process → periksa parent |
| Login gagal massal | Brute force | Block source IP → reset kredensial |
| Port terbuka tak dikenal | Exposure | Identify service → tutup / firewall |

---

## 4. Cara Kerja SecurityValidator

`core/security_validation.py` menjalankan:

1. **Ekstraksi indikator** — CVE, port, process, hash, path dari output alat.
2. **Korelasi CVE** — cocokkan dengan database CVE internal.
3. **Analisis MITRE ATT&CK** — deteksi pola T1059.001, T1055, T1068, dll.
4. **Penilaian OWASP** — deteksi kegagalan A01–A10.
5. **Skor Kepercayaan** — 0.5 (baseline) hingga 1.0 (expert), grade:
   EXPERT ≥ 0.9, HIGH ≥ 0.8, SENIOR ≥ 0.6, JUNIOR ≥ 0.4, ANALYST < 0.4.
6. **Rekomendasi Expert** — remediasi prioritas berdasarkan severity.

Setiap temuan yang divalidasi otomatis diperkaya dengan `security_validation`
(di `CoreOrchestrator.run_task`) sehingga laporan selalu punya referensi nyata.

---

## 5. Contoh Penggunaan CLI

```bash
# Mode interaktif
python midnight_cli.py

# Langsung jalankan assessment
python midnight_cli.py /run "Periksa kerentanan eksaustif aplikasi web target"

# Tampilkan semua fitur
python midnight_cli.py /features

# Deteksi WSL & indeks untuk RAG
python midnight_cli.py /wsl-distros
python midnight_cli.py /index ./target-app/
```

---

**Ingat:** Midnight Core mengasumsikan target telah diotorisasi untuk diuji.
Jangan pernah mengklaim kerentanan tanpa bukti (`evidence`). Jika bukti kurang,
nyatakan **"Not enough evidence"** dan minta scan tambahan.
