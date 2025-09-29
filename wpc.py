#!/usr/bin/env python3

import requests
import os
import sys
import argparse
import time
import json
import re
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class ShadowDownloader:
    def __init__(self, base_url, output_dir=None, threads=10, timeout=30, user_agent=None):
        self.base_url = base_url.rstrip('/')
        if getattr(sys.modules['__main__'], 'SINGLE_TARGET_MODE', False):
            # Kalau single target
            if output_dir:
                self.output_dir = output_dir
            else:
                self.output_dir = None
        else:
            self.output_dir = output_dir or self._create_output_dir()
        self.threads = threads
        self.timeout = timeout
        self.session = requests.Session()
        self.downloaded_files = []
        self.failed_downloads = []

        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': self.base_url
        }
        self.session.headers.update(self.headers)

        # 🎯 Display
        print("┌─────────────────────────────────────────────────────────┐")
        print("│                  SHΔDØW DOWNLOADER v1.1                 │")
        print("│                 Enhanced Display Edition                │")
        print("└─────────────────────────────────────────────────────────┘")
        print(f"🔗 Target    : {self.base_url}")
        if getattr(sys.modules['__main__'], 'SINGLE_TARGET_MODE', False):
            if self.output_dir: 
                print(f"📁 Output    : {self.output_dir}")
        else:
            print(f"📁 Output    : {self.output_dir}")
        print(f"🔢 Threads   : {self.threads}")
        print("─" * 60)

    def _create_output_dir(self):
        domain = urlparse(self.base_url).netloc
        timestamp = int(time.time())
        output_dir = f"downloads_{domain}_{timestamp}"
        return output_dir

    def _get_directory_listing(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return []

            file_patterns = [
                r'href="([^"]+\.(jpg|jpeg|png|gif|bmp|webp|pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z|tar|gz|mp4|mp3|avi|mov|wmv|flv|txt|log|csv|json|xml|sql|backup|bak))"',
                r'href="([^"]+\.(JPG|JPEG|PNG|GIF|BMP|WEBP|PDF|DOC|DOCX|XLS|XLSX|PPT|PPTX|ZIP|RAR|7Z|TAR|GZ|MP4|MP3|AVI|MOV|WMV|FLV|TXT|LOG|CSV|JSON|XML|SQL|BACKUP|BAK))"',
                r"href='([^']+\.(jpg|jpeg|png|gif|bmp|webp|pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z|tar|gz|mp4|mp3|avi|mov|wmv|flv|txt|log|csv|json|xml|sql|backup|bak))'",
                r'href="([^"]+\.[a-zA-Z0-9]{2,5})"',
            ]

            files = []
            for pattern in file_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    file_url = match[0] if isinstance(match, tuple) else match
                    if (file_url not in ['../', './']
                            and not file_url.startswith('?')
                            and not file_url.endswith('/')):
                        full_url = urljoin(url, file_url)
                        files.append(full_url)

            return list(set(files))

        except requests.RequestException as e:
            print(f"❌ Error accessing {url}: {e}")
            return []

    def _discover_directories(self, base_url):
        print("🔍 Scanning directory structure...")

        directories = [base_url]
        discovered_dirs = set()

        common_dirs = ['2025', '2024', '2023', '2022', '2021', '2020',
                       '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

        for year in common_dirs[:6]:
            year_url = f"{base_url}/{year}/"
            if self._check_directory_exists(year_url):
                directories.append(year_url)
                discovered_dirs.add(year_url)
                print(f"├─ 📁 Found: /{year}/")

                for month in common_dirs[6:]:
                    month_url = f"{year_url}/{month}/"
                    if self._check_directory_exists(month_url):
                        directories.append(month_url)
                        discovered_dirs.add(month_url)
                        print(f"│  └─ 📂 Found: /{year}/{month}/")

        print(f"└─ Scan completed")
        return list(discovered_dirs)

    def _check_directory_exists(self, url):
        try:
            response = self.session.head(url, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False

    def _download_file(self, file_url, local_path):
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            response = self.session.get(file_url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_info = {
                'url': file_url,
                'local_path': local_path,
                'size': os.path.getsize(local_path),
                'timestamp': time.time()
            }
            self.downloaded_files.append(file_info)

            print(f"✅ {os.path.basename(local_path):<50} {self._format_size(file_info['size']):>10}")
            return True

        except Exception as e:
            filename = os.path.basename(local_path)
            print(f"❌ {filename:<50} {str(e)[:25]:<25}")
            self.failed_downloads.append({'url': file_url, 'error': str(e)})
            return False

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def discover_files(self, base_url):
        print("🔍 Starting file discovery...")

        all_files = []
        base_files = self._get_directory_listing(base_url)
        all_files.extend(base_files)
        print(f"├─ Base directory: {len(base_files)} files")

        directories = self._discover_directories(base_url)

        total_dir_files = 0
        for directory in directories:
            dir_files = self._get_directory_listing(directory)
            all_files.extend(dir_files)
            if dir_files:
                total_dir_files += len(dir_files)

        if total_dir_files > 0:
            print(f"├─ Subdirectories: {total_dir_files} files")

        total_files = len(set(all_files))
        print(f"└─ Total files: {total_files}")

        return list(set(all_files))

    def download_single_file(self, file_url, custom_filename=None):
        print("🎯 SINGLE TARGET MODE")
        print(f"🔗 URL: {file_url}")
        print("─" * 60)

        if getattr(sys.modules['__main__'], 'SINGLE_TARGET_MODE', False) and self.output_dir:
            # Kalau user kasih -o, simpan di folder itu
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
            base_dir = self.output_dir
        else:
            # Default: simpan di current working dir
            base_dir = os.getcwd()

        if custom_filename:
            local_path = os.path.join(base_dir, custom_filename)
        else:
            parsed_url = urlparse(file_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or filename == '/':
                filename = f"downloaded_file_{int(time.time())}"
            local_path = os.path.join(base_dir, filename)


        success = self._download_file(file_url, local_path)

        print("─" * 60)
        if success:
            print(f"✅ DOWNLOAD COMPLETE: {local_path}")
            return True
        else:
            print(f"❌ DOWNLOAD FAILED: {file_url}")
            return False

    def download_all_files(self):
        print("🚀 MASS DOWNLOAD INITIATED")

        all_files = self.discover_files(self.base_url)

        if not all_files:
            print("❌ No files found to download")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        print(f"📦 Total files to download: {len(all_files)}")
        print("─" * 60)

        download_tasks = []
        for file_url in all_files:
            parsed_url = urlparse(file_url)
            relative_path = parsed_url.path.split('/wp-content/uploads/')[-1]
            local_path = os.path.join(self.output_dir, relative_path.lstrip('/'))
            download_tasks.append((file_url, local_path))

        print("📥 Starting download process...")

        successful_downloads = 0
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self._download_file, url, path): (url, path)
                           for url, path in download_tasks}

                with tqdm(total=len(futures), desc="📥 Downloading", unit="file") as pbar:
                    for future in as_completed(futures):
                        url, path = futures[future]
                        try:
                            if future.result():
                                successful_downloads += 1
                        except Exception as e:
                            print(f"💥 Unexpected error with {url}: {e}")
                        finally:
                            pbar.update(1)
        except KeyboardInterrupt:
            print("\n⏹️  Download interrupted by user")
            return

        self._print_summary(len(all_files), successful_downloads)

    def _print_summary(self, total_files, successful_downloads):
        print("─" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("─" * 60)
        print(f"├─ Target: {self.base_url}")
        print(f"├─ Output: {self.output_dir}")
        print(f"├─ Total files: {total_files}")
        print(f"├─ ✅ Successful: {successful_downloads}")
        print(f"├─ ❌ Failed: {len(self.failed_downloads)}")
        total_data = sum(f['size'] for f in self.downloaded_files)
        print(f"└─ 💾 Total data: {self._format_size(total_data)}")

        if self.failed_downloads:
            print(f"\n⚠️  Failed downloads ({len(self.failed_downloads)} total):")
            for failed in self.failed_downloads:
                filename = os.path.basename(failed['url'])
                print(f"   └─ {filename} → {failed['url']}")


def main():
    parser = argparse.ArgumentParser(description='SHΔDØW DOWNLOADER v1.1 - WordPress Uploads Mass Downloader')
    parser.add_argument('url', help='URL of wp-content/uploads/ directory OR single file URL')
    parser.add_argument('-o', '--output', help='Output directory (default: auto-generated)')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of concurrent downloads (default: 10)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')

    parser.add_argument('-st', '--single-target', action='store_true',
                        help='Single target mode - download only the specified file URL')
    parser.add_argument('-name', '--filename', help='Custom filename for single target download')

    args = parser.parse_args()

    try:
        if args.single_target:
            setattr(sys.modules['__main__'], 'SINGLE_TARGET_MODE', True)
        else:
            setattr(sys.modules['__main__'], 'SINGLE_TARGET_MODE', False)

        downloader = ShadowDownloader(
            base_url=args.url,
            output_dir=args.output,
            threads=args.threads,
            timeout=args.timeout
        )

        if args.single_target:
            downloader.download_single_file(args.url, args.filename)
        else:
            downloader.download_all_files()

    except KeyboardInterrupt:
        print(f"\n⏹️  Download interrupted by user")
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
