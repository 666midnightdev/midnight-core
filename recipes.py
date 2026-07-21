# recipes.py - Static security tool recipes (Bahasa Indonesia)
# Setiap resep berisi bundle perintah WSL siap copy-paste + penjelasan lengkap.
# AI tidak mengeksekusi; user yang menyalin ke Kali WSL.

TARGET_PLACEHOLDER = "TARGET_ANDA"

RECIPES = {
    "web": {
        "label": "WEB AUDIT (Standard)",
        "desc": "Audit kerentanan web app: port, fingerprint, misconfig, directory brute.",
        "steps": [
            {
                "tool": "nmap",
                "cmd": f"nmap -sV -p- {TARGET_PLACEHOLDER}",
                "why": "Tahap pertama (recon). Memindai semua port terbuka dan mendeteksi versi service (Apache/Nginx/php). Wajib sebelum tool lain karena kita harus tahu port apa yang hidup.",
                "flags": "-sV = service version detection | -p- = scan semua port 1-65535 (bukan cuma 1000 default)",
                "target_format": "IP atau DOMAIN BARE (tanpa http://). Contoh: 192.168.1.10 atau aku.com",
                "note": "JANGAN pakai http:// atau https:// di nmap, akan error 'Unable to split netmask'. Pakai host mentah.",
            },
            {
                "tool": "whatweb",
                "cmd": f"whatweb {TARGET_PLACEHOLDER}",
                "why": "Fingerprint teknologi: CMS (WordPress/Joomla), framework (Django/Laravel), library JS. Berguna untuk cari CVE spesifik setelah tahu versinya.",
                "flags": "tanpa flag = default. Output berisi CMS, server, IP, script.",
                "target_format": "Bebas: domain bare, http://, atau https://. Contoh: aku.com atau https://aku.com",
                "note": "Kalau web pakai HTTPS pakai https:// agar tidak 'connection refused' di port 443.",
            },
            {
                "tool": "nikto",
                "cmd": f"nikto -h {TARGET_PLACEHOLDER}",
                "why": "Scanner miskonfigurasi web server: file berbahaya, header hilang, versi usang. Cepat dan jarang false-positive parah.",
                "flags": "-h = host target",
                "target_format": "http:// atau https:// (atau domain bare). Contoh: http://192.168.1.10 atau https://aku.com",
                "note": "Pakai http:// dulu (port 80). Kalau web HTTPS-only, ganti ke https://. Jangan IP dengan https kalau server tidak pakai TLS.",
            },
            {
                "tool": "ffuf",
                "cmd": f"ffuf -u {TARGET_PLACEHOLDER}/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 20 -mc 200,204,301,302,403 -s",
                "why": "Directory/file brute-force (fuzzing). Mencari file/admin tersembunyi yang gak ada di homepage (mis. /admin, /backup.zip). Ini yang sering nemu celah nyata.",
                "flags": "-u = URL dengan FUZZ sebagai placeholder | -w = wordlist | -t = thread | -mc = response code yang ditampilkan | -s = silent (cuma hasil)",
                "target_format": "WAJIB http:// atau https:// + path. Contoh: http://aku.com/FUZZ atau https://192.168.1.10:8080/FUZZ",
                "note": "ffuf butuh URL lengkap dengan skema. Tanpa http:// akan error. FUZZ adalah placeholder kata yang diganti wordlist.",
            },
            {
                "tool": "arjun",
                "cmd": f"arjun -u {TARGET_PLACEHOLDER} -w /usr/share/seclists/Discovery/Web-Content/parameter_names.txt",
                "why": "Menemukan parameter tersembunyi di URL (mis. ?id=, ?debug=). Parameter tersembunyi sering jadi jalur SQLi/IDOR/RCE.",
                "flags": "-u = URL | -w = wordlist nama parameter",
                "target_format": "WAJIB http:// atau https:// URL. Contoh: https://aku.com/page",
                "note": "Sama seperti ffuf, butuh skema http/https lengkap.",
            },
        ],
    },
    "stealth": {
        "label": "WEB AUDIT (STEALTH / LAMBAT)",
        "desc": "Sama seperti web audit tapi lambat agar tidak ketahuan firewall/IDS. Pakai kalau target pakai WAF atau kamu ingin tidak membebani jaringan.",
        "steps": [
            {
                "tool": "nmap",
                "cmd": f"nmap -sS -T2 -Pn -p- --data-length 24 {TARGET_PLACEHOLDER}",
                "why": "Scan lambat (T2) + SYN stealth (-sS) + skip ping (-Pn) + tambah random data agar signature paket tidak mudah dikenali IDS. Cocok untuk target yang diawasi.",
                "flags": "-sS = SYN stealth scan | -T2 = timing sangat pelan | -Pn = jangan ping dulu | --data-length = padding acak",
                "target_format": "IP atau DOMAIN BARE (tanpa http://). Contoh: 192.168.1.10 atau aku.com",
                "note": "JANGAN pakai http:// atau https:// di nmap.",
            },
            {
                "tool": "whatweb",
                "cmd": f"whatweb --lowercase {TARGET_PLACEHOLDER}",
                "why": "Sama seperti standar, tapi --lowercase agar lebih bersih dibaca. Tetap aman (cuma request HTTP biasa).",
                "flags": "--lowercase = normalisasi output",
                "target_format": "Bebas: domain bare, http://, atau https://.",
                "note": "Kalau HTTPS pakai https:// agar tidak refused.",
            },
            {
                "tool": "nikto",
                "cmd": f"nikto -h {TARGET_PLACEHOLDER} -T 5 -maxtime 120",
                "why": "Nikto dengan throttling (-T 5 = paling pelan) dan batas waktu 120 detik agar tidak membanjiri target.",
                "flags": "-T 5 = tuning timing paling lambat | -maxtime = henti setelah N detik",
                "target_format": "http:// atau https:// (atau domain bare).",
                "note": "Pakai http:// dulu (port 80), ganti https:// kalau web HTTPS-only.",
            },
            {
                "tool": "ffuf",
                "cmd": f"ffuf -u {TARGET_PLACEHOLDER}/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 5 -rate 10 -mc 200,204,301,302,403 -s",
                "why": "Fuzzing pelan (-t 5, -rate 10 req/detik) agar tidak memicu rate-limit atau WAF blokir IP kamu.",
                "flags": "-t 5 = 5 thread | -rate 10 = 10 request per detik",
                "target_format": "WAJIB http:// atau https:// + path. Contoh: http://aku.com/FUZZ",
                "note": "ffuf butuh URL lengkap dengan skema. Tanpa http:// akan error.",
            },
        ],
    },
    "fast": {
        "label": "WEB AUDIT (CEPAT)",
        "desc": "Cepat untuk lab lokal. Tidak peduli ketahuan (karena itu punya sendiri).",
        "steps": [
            {
                "tool": "nmap",
                "cmd": f"nmap -T4 -sV -p 80,443,8080,3306,21,22 {TARGET_PLACEHOLDER}",
                "why": "Scan agresif (-T4) ke port umum saja (web, db, ssh, ftp). Jauh lebih cepat dari -p- tapi cukup untuk lab.",
                "flags": "-T4 = timing agresif | -p = port tertentu",
                "target_format": "IP atau DOMAIN BARE (tanpa http://).",
                "note": "JANGAN pakai http:// atau https:// di nmap.",
            },
            {
                "tool": "whatweb",
                "cmd": f"whatweb {TARGET_PLACEHOLDER}",
                "why": "Fingerprint cepat.",
                "flags": "-",
                "target_format": "Bebas: domain bare, http://, atau https://.",
                "note": "Kalau HTTPS pakai https://.",
            },
            {
                "tool": "nikto",
                "cmd": f"nikto -h {TARGET_PLACEHOLDER} -T 1",
                "why": "Nikto paling cepat (-T 1).",
                "flags": "-T 1 = tuning paling cepat",
                "target_format": "http:// atau https:// (atau domain bare).",
                "note": "Pakai http:// dulu, ganti https:// kalau web HTTPS-only.",
            },
            {
                "tool": "ffuf",
                "cmd": f"ffuf -u {TARGET_PLACEHOLDER}/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50 -mc 200,204,301,302,403 -s",
                "why": "Fuzzing agresif (-t 50).",
                "flags": "-t 50 = 50 thread",
                "target_format": "WAJIB http:// atau https:// + path. Contoh: http://aku.com/FUZZ",
                "note": "ffuf butuh URL lengkap dengan skema.",
            },
        ],
    },
    "full": {
        "label": "FULL RECON + EXPLOIT CHECK",
        "desc": "Semua di atas + SQLmap (jika ada form/login) + amass (subdomain). Untuk target yang kamu punya penuh.",
        "steps": [
            {
                "tool": "amass",
                "cmd": f"amass enum -d {TARGET_PLACEHOLDER}",
                "why": "Enumerasi subdomain (jika target berupa domain). Menemukan app tersembunyi di subdomain.lab.mu.",
                "flags": "enum -d = enumerate domain",
                "target_format": "DOMAIN BARE saja (tanpa http://). Contoh: aku.com",
                "note": "amass hanya untuk domain publik, TIDAK untuk IP. Butuh waktu lama (passive recon).",
            },
            {
                "tool": "nmap",
                "cmd": f"nmap -sV -p- {TARGET_PLACEHOLDER}",
                "why": "Port scan lengkap.",
                "flags": "-",
                "target_format": "IP atau DOMAIN BARE (tanpa http://).",
                "note": "JANGAN pakai http:// atau https:// di nmap.",
            },
            {
                "tool": "whatweb",
                "cmd": f"whatweb {TARGET_PLACEHOLDER}",
                "why": "Fingerprint.",
                "flags": "-",
                "target_format": "Bebas: domain bare, http://, atau https://.",
                "note": "Kalau HTTPS pakai https://.",
            },
            {
                "tool": "nikto",
                "cmd": f"nikto -h {TARGET_PLACEHOLDER}",
                "why": "Misconfig scan.",
                "flags": "-",
                "target_format": "http:// atau https:// (atau domain bare).",
                "note": "Pakai http:// dulu, ganti https:// kalau web HTTPS-only.",
            },
            {
                "tool": "ffuf",
                "cmd": f"ffuf -u {TARGET_PLACEHOLDER}/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 20 -mc 200,204,301,302,403 -s",
                "why": "Directory fuzz.",
                "flags": "-",
                "target_format": "WAJIB http:// atau https:// + path.",
                "note": "ffuf butuh URL lengkap dengan skema.",
            },
            {
                "tool": "sqlmap",
                "cmd": f"sqlmap -u {TARGET_PLACEHOLDER}/login --batch --crawl=2 --level=2",
                "why": "Otomatis cek SQL Injection pada form/login. HANYA untuk lab milikmu. Ini tool exploit sungguhan.",
                "flags": "-u = URL target | --batch = jawab ya semua | --crawl = ikut link | --level = kedalaman tes",
                "target_format": "WAJIB http:// atau https:// URL lengkap (sampai path login).",
                "note": "sqlmap butuh URL dengan skema. Jangan pakai domain bare/IP tanpa http.",
            },
        ],
    },
    "code": {
        "label": "SOURCE CODE AUDIT (Semgrep)",
        "desc": "Cek kerentanan di source code web yang KAMU TULIS SENDIRI. Tidak perlu server jalan.",
        "steps": [
            {
                "tool": "semgrep",
                "cmd": f"semgrep --config auto /path/ke/web-lab-kamu",
                "why": "Static analysis: membaca kode sumber dan mencari pola SQLi, XSS, IDOR, hardcoded secret. Ini yang paling 'expert' karena langsung ke kode, bukan server.",
                "flags": "--config auto = pakai semua rule bawaan | ganti path dengan folder kode kamu",
                "target_format": "PATH folder/file lokal (bukan URL). Contoh: /home/kamu/web-app",
                "note": "semgrep jalan di Linux (Kali WSL) pada path lokal. Tidak butuh server jalan.",
            },
        ],
    },
    "subdomain": {
        "label": "SUBDOMAIN ENUMERATION (CEPAT)",
        "desc": "Cari subdomain / virtual host dari sebuah domain. Lebih cepat dari amass (pakai brute-force + passive ringan). HANYA untuk domain milikmu.",
        "steps": [
            {
                "tool": "gobuster dns",
                "cmd": f"gobuster dns -d {TARGET_PLACEHOLDER} -w /usr/share/seclists/Discovery/DNS/subdomains-top1million.txt -t 50",
                "why": "Brute-force subdomain dari wordlist (DNS query). Paling cepat & reliable untuk nemu subdomain di lab/domain sendiri.",
                "flags": "dns = mode DNS | -d = domain | -w = wordlist | -t = thread",
                "target_format": "DOMAIN BARE. Contoh: aku.com",
                "note": "JANGAN pakai http:// di gobuster dns. Hasil berupa subdomain yang resolve ke IP.",
            },
            {
                "tool": "subfinder",
                "cmd": f"subfinder -d {TARGET_PLACEHOLDER} -silent",
                "why": "Passive enumeration (tanya sumber publik: crt.sh, dll). Lebih cepat dari amass tapi tetap butuh internet. Melengkapi gobuster.",
                "flags": "-d = domain | -silent = cuma hasil",
                "target_format": "DOMAIN BARE. Contoh: aku.com",
                "note": "Passive = tidak kirim request ke target, cuma cek sumber eksternal. Lebih stealth.",
            },
            {
                "tool": "ffuf vhost",
                "cmd": f"ffuf -u http://{TARGET_PLACEHOLDER} -H \"Host: FUZZ.{TARGET_PLACEHOLDER}\" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million.txt -t 50 -mc 200,403,404",
                "why": "Virtual host brute-force: nemu host tersembunyi di 1 IP server (mis. dev.aku.com, admin.aku.com) yang tidak terdaftar di DNS publik.",
                "flags": "-u = base URL | -H = header Host dengan FUZZ | -w = wordlist | -mc = response code",
                "target_format": "DOMAIN BARE (ffuf otomatis tambah http://). Contoh: aku.com",
                "note": "Ini nemu vhost, bukan subdomain DNS. Cocok kalau target 1 IP dengan banyak site.",
            },
            {
                "tool": "dnsx",
                "cmd": f"subfinder -d {TARGET_PLACEHOLDER} -silent | dnsx -silent",
                "why": "Validasi hasil subfinder: hanya tampilkan subdomain yang benar-benar resolve ke IP (filter false-positive).",
                "flags": "dnsx -silent = validasi DNS",
                "target_format": "Pipeline dari subfinder (domain bare).",
                "note": "Gabungan subfinder + dnsx = hasil bersih tanpa basi.",
            },
        ],
    },
    "prod": {
        "label": "PRODUCTION-SAFE AUDIT (Domain Deployed Milikmu)",
        "desc": "Untuk web yang SUDAH DEPLOY & PRODUKSI (punya domain publik sendiri). Lambat + hati-hati agar tidak merusak layanan/user nyata. JANGAN pakai sqlmap tanpa backup.",
        "steps": [
            {
                "tool": "nmap",
                "cmd": f"nmap -sS -T2 -Pn -p 80,443,8080,8443 {TARGET_PLACEHOLDER}",
                "why": "Port scan pelan ke port web umum saja (bukan -p-). Tidak membebani server produksi.",
                "flags": "-sS = SYN stealth | -T2 = pelan | -Pn = skip ping | -p = port tertentu",
                "target_format": "IP atau DOMAIN BARE (tanpa http://).",
                "note": "JANGAN pakai http:// di nmap. Batasi port agar tidak scan semua 65535 (berat di produksi).",
            },
            {
                "tool": "testssl",
                "cmd": f"testssl.sh --fast {TARGET_PLACEHOLDER}",
                "why": "Audit SSL/TLS: cek sertifikat, cipher lemah, Heartbleed, dll. Penting buat domain publik (user kirim data lewat HTTPS).",
                "flags": "--fast = cek cepat | ganti dengan --full untuk audit lengkap",
                "target_format": "DOMAIN BARE atau https://. Contoh: webku.com",
                "note": "testssl butuh domain/host, bukan IP kalau tidak ada SNI. Bagus buat cek kepatuhan HTTPS.",
            },
            {
                "tool": "whatweb",
                "cmd": f"whatweb https://{TARGET_PLACEHOLDER}",
                "why": "Fingerprint teknologi (CMS, framework) untuk cari CVE setelah tahu versi. Aman (cuma GET request).",
                "flags": "-",
                "target_format": "https:// (karena produksi biasanya HTTPS).",
                "note": "Pakai https:// agar tidak refused di 443.",
            },
            {
                "tool": "nikto",
                "cmd": f"nikto -h https://{TARGET_PLACEHOLDER} -T 5 -maxtime 120",
                "why": "Cek miskonfigurasi web server dengan throttling agar tidak membanjiri produksi.",
                "flags": "-T 5 = paling lambat | -maxtime = henti setelah 120 detik",
                "target_format": "https:// (produksi HTTPS).",
                "note": "Hati-hati: nikto bisa trigger WAF. Kalau IP ke-blokir, tunggu atau pakai VPN.",
            },
            {
                "tool": "ffuf",
                "cmd": f"ffuf -u https://{TARGET_PLACEHOLDER}/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 5 -rate 10 -mc 200,204,301,302,403 -s",
                "why": "Directory fuzz pelan (5 thread, 10 req/detik) agar WAF tidak blokir dan server tidak berat.",
                "flags": "-t 5 | -rate 10 = sangat pelan",
                "target_format": "WAJIB https:// + path.",
                "note": "Di produksi, naikkan rate hanya kalau yakin tidak ada WAF rate-limit.",
            },
            {
                "tool": "cmsmap",
                "cmd": f"cmsmap https://{TARGET_PLACEHOLDER}",
                "why": "Jika web pakai WordPress/Joomla/Drupal, cmsmap cek CVE spesifik CMS & plugin. Sangat relevan buat web deployed.",
                "flags": "tanpa flag = auto-detect CMS",
                "target_format": "https:// URL lengkap.",
                "note": "Hanya berguna kalau web pakai CMS populer. Kalau custom framework, lewati saja.",
            },
            {
                "tool": "aquatone",
                "cmd": f"echo {TARGET_PLACEHOLDER} | aquatone -out ~/aquatone-{TARGET_PLACEHOLDER}",
                "why": "Bikin screenshot bukti tiap host/endpoint yang ditemukan. Berguna buat laporan ke klien/atasan (visual evidence).",
                "flags": "-out = folder hasil screenshot",
                "target_format": "Domain bare (aquatone baca dari stdin).",
                "note": "Hasil berupa HTML + screenshot di ~/aquatone-domain. Berguna buat dokumentasi.",
            },
        ],
    },
}


def render_recipe(profile: str, target: str) -> str:
    """Return formatted recipe text for given profile and target."""
    if profile not in RECIPES:
        avail = ", ".join(RECIPES.keys())
        return f"[ERROR] Profil '{profile}' tidak dikenal.\nProfil tersedia: {avail}"

    r = RECIPES[profile]
    tgt = target if target else TARGET_PLACEHOLDER
    lines = []
    lines.append("=" * 70)
    lines.append(f"RESEP KEAMANAN: {r['label']}")
    lines.append("=" * 70)
    lines.append(f"Deskripsi: {r['desc']}")
    lines.append(f"Target: {tgt}")
    lines.append("")
    lines.append("Salin SEMUA perintah di bawah ke Kali WSL (satu per satu atau sekaligus):")
    lines.append("-" * 70)
    for i, s in enumerate(r["steps"], 1):
        lines.append(f"\n[{i}] TOOL: {s['tool']}")
        lines.append(f"    Perintah:")
        lines.append(f"    {s['cmd'].replace(TARGET_PLACEHOLDER, tgt)}")
        lines.append(f"    Fungsi : {s['why']}")
        lines.append(f"    Flag   : {s['flags']}")
        lines.append(f"    Format : {s.get('target_format', '-')}")
        lines.append(f"    Catatan: {s.get('note', '-')}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("CATATAN: Ganti TARGET_ANDA dengan IP/domain lab milikmu.")
    lines.append("Jangan arahkan ke web orang tanpa izin (UU ITE).")
    lines.append("=" * 70)
    return "\n".join(lines)
