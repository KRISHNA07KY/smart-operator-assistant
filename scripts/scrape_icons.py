"""
Web Scraper for Dashboard Icons
Scrapes clean, high-resolution vector SVG icons from open icon repositories on the web
and saves them to the assets/icons directory.
"""

import os
import urllib.request
import time

ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons"))

# Map icon key name to remote URL on Lucide / Feather icon CDN
BASE_URL = "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons"

ICON_MAP = {
    # Navigation & General
    "tasks": f"{BASE_URL}/clipboard-list.svg",
    "safety": f"{BASE_URL}/shield-alert.svg",
    "estimator": f"{BASE_URL}/timer.svg",
    "telemetry": f"{BASE_URL}/activity.svg",
    "training": f"{BASE_URL}/graduation-cap.svg",
    
    # Status & Alerts
    "alert-triangle": f"{BASE_URL}/triangle-alert.svg",
    "alert-octagon": f"{BASE_URL}/octagon-alert.svg",
    "alert-circle": f"{BASE_URL}/circle-alert.svg",
    "shield-check": f"{BASE_URL}/shield-check.svg",
    "check-circle": f"{BASE_URL}/circle-check.svg",
    "x-circle": f"{BASE_URL}/circle-x.svg",
    "radio": f"{BASE_URL}/radio.svg",
    
    # Actions & Controls
    "pause": f"{BASE_URL}/pause.svg",
    "play": f"{BASE_URL}/play.svg",
    "refresh": f"{BASE_URL}/refresh-cw.svg",
    "zap": f"{BASE_URL}/zap.svg",
    "save": f"{BASE_URL}/save.svg",
    "target": f"{BASE_URL}/target.svg",
    "calendar": f"{BASE_URL}/calendar.svg",
    
    # Context Badges & Metadata
    "cloud-rain": f"{BASE_URL}/cloud-rain.svg",
    "sun": f"{BASE_URL}/sun.svg",
    "user": f"{BASE_URL}/user.svg",
    "truck": f"{BASE_URL}/truck.svg",
    "hard-hat": f"{BASE_URL}/hard-hat.svg",
    "wrench": f"{BASE_URL}/wrench.svg",
    "lightbulb": f"{BASE_URL}/lightbulb.svg",
    "trending-down": f"{BASE_URL}/trending-down.svg",
    "video": f"{BASE_URL}/video.svg",
    "gauge": f"{BASE_URL}/gauge.svg",
}

def scrape_all_icons():
    os.makedirs(ICONS_DIR, exist_ok=True)
    print(f"Starting web scraping of {len(ICON_MAP)} icons into {ICONS_DIR}...")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    success_count = 0
    
    for name, url in ICON_MAP.items():
        dest_file = os.path.join(ICONS_DIR, f"{name}.svg")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                svg_data = response.read().decode("utf-8")
                with open(dest_file, "w", encoding="utf-8") as f:
                    f.write(svg_data)
                print(f"[OK] Scraped: {name}.svg ({len(svg_data)} bytes)")
                success_count += 1
        except Exception as e:
            print(f"[ERROR] Failed scraping {name} from {url}: {e}")
        time.sleep(0.05)  # gentle rate limit
        
    print(f"\nSuccessfully scraped {success_count}/{len(ICON_MAP)} icons!")

if __name__ == "__main__":
    scrape_all_icons()
