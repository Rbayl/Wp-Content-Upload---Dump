# WP Content Dumper v1.1  

🚀 **WordPress Uploads Bulk Downloader** support with:  
- **Mass download** all files from `/wp-content/uploads/`
- **Single target mode** (download only one file)
- **Auto resume** if the connection is lost
- **Threads** for parallel downloads
- **Progress bar (tqdm)** for a neater layout
- **Error reporting** (failed downloads display the full URL in the summary)

---

## ⚡ Main Features
- 🔍 Auto scan folder structure (`/year/month/`)
- 📥 Bulk download all files (images, documents, archives, videos, etc.)
- 🎯 Single target mode with custom filenames
- 💾 Automatic session resume (`.wpc_resume.json`)
- 📊 Complete download summary (total files, success, failure, data size)
- ⚠️ List of failed links automatically displayed in the summary

---

## 📦 Installation
Clone repo:
```bash
https://github.com/Rbayl/wpcu-dump.git
cd wpcu-dump
pip install -r requirements.txt
```

---

## ⚙️ How To Use

### Mass Download
Download the entire contents of `wp-content/uploads/` (auto-scan):
```bash
python3 wpc.py "https://target.com/wp-content/uploads/"
```

### Single Target
Download 1 Specific File
```bash
python3 wpc.py -st "https://target.com/wp-content/uploads/2025/01/file.pdf"
```

### Custom Filename (single target)
Download 1 file and save it with a custom name:
```bash
python3 wpc.py "https://target.com/wp-content/uploads/2025/01/file.pdf" -st -name report.pdf
```

### Set Threads
Change the number of threads (default 10):
```bash
python3 wpc.py "https://target.com/wp-content/uploads/" -t 20
```

### Set Timeout
Change the request timeout (seconds, default 30):
```bash
python3 wpc.py "https://target.com/wp-content/uploads/" --timeout 60
```

### Resume Session
Resume the previous download session (use the resume file in the output folder):
```bash
python3 wpc.py "https://target.com/wp-content/uploads/" --resume
```

### Mass target display
```bash
┌─────────────────────────────────────────────────────────┐
│               WP Content Upload Download                │
│                     by 0xk4sa                           │
└─────────────────────────────────────────────────────────┘
🔗 Target    : https://target.com/wp-content/uploads/
📁 Output    : downloads_target.com_1738213423
🔢 Threads   : 10
────────────────────────────────────────────────────────────
🚀 MASS DOWNLOAD INITIATED
🔍 Starting file discovery...
├─ Base directory: 1 files
🔍 Scanning directory structure...
├─ 📁 Found: /2025/
│  └─ 📂 Found: /2025/01/
│  └─ 📂 Found: /2025/02/
│  └─ 📂 Found: /2025/03/
│  └─ 📂 Found: /2025/04/
│  └─ 📂 Found: /2025/05/
│  └─ 📂 Found: /2025/06/
│  └─ 📂 Found: /2025/07/
│  └─ 📂 Found: /2025/08/
│  └─ 📂 Found: /2025/09/
├─ 📁 Found: /2024/
│  └─ 📂 Found: /2024/06/
│  └─ 📂 Found: /2024/07/
│  └─ 📂 Found: /2024/08/
│  └─ 📂 Found: /2024/09/
│  └─ 📂 Found: /2024/10/
│  └─ 📂 Found: /2024/11/
│  └─ 📂 Found: /2024/12/
└─ Scan completed
├─ Subdirectories: 4814 files
└─ Total files: 4797
📦 Total files to download: 4797
────────────────────────────────────────────────────────────
```

### Single target display

```bash
┌─────────────────────────────────────────────────────────┐
│               WP Content Upload Download                │
│                     by 0xk4sa                           │
└─────────────────────────────────────────────────────────┘
🔗 Target    : https://target.com/wp-content/uploads/example.jpeg
📁 Output    : downloads_target.com_1738213423
🔢 Threads   : 10
────────────────────────────────────────────────────────────
🎯 SINGLE TARGET MODE
🔗 URL: https://target.com/wp-content/uploads/example.jpeg
────────────────────────────────────────────────────────────
✅ example.jpeg     6.5 KB
────────────────────────────────────────────────────────────
✅ DOWNLOAD COMPLETE: downloads_target.com_1738213423/example.jpeg
```

### Finished scanning display

```bash
────────────────────────────────────────────────────────────
📊 DOWNLOAD SUMMARY
────────────────────────────────────────────────────────────
├─ Target: https://target.com/wp-content/uploads/
├─ Output: downloads_target.com_1738213423
├─ Total files: 4797
├─ ✅ Successful: 4794
├─ ❌ Failed: 3
├─ 💾 Total data: 763.0 MB
└─ 💾 Resume data: downloads_target.com_1738213423/.wpc_resume.json

⚠️  Failed downloads (1 total):
   └─ example.jpeg → https://target.com/wp-content/uploads/example.jpeg
```

### Disclaimer
This tool is designed for educational and pentesting purposes.
Use only on sites you have permission to scan/download.
The developer is not responsible for any misuse. Use with caution.
