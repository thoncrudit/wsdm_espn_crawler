import requests
import time
import json
import urllib.robotparser
import os

#config
DOMAIN = "https://www.espn.com"
HEADERS = {
    "User-Agent": "NBA_KG_Bot/1.0 (academic project)"
}
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/raw_espn_articles.json"))

def check_robots_txt(url):
    """checks ESPN's robots.txt"""
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{DOMAIN}/robots.txt")
    try:
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except:
        return False 

def fetch_articles(urls):
    """fetches raw HTML !ethically! and saves to disk"""
    scraped_data = []

    for url in urls:
        if not check_robots_txt(url):
            print(f"{url} blocked by robots.txt")
            continue

        try:
            print(f"fetching {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            scraped_data.append({
                "url": url,
                "html": response.text
            })
            
            #rate limit
            time.sleep(3) 

        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    
    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4)
    print(f"saved {len(scraped_data)} raw articles to {RAW_DATA_PATH}")

if __name__ == "__main__":
    test_urls = [
        "https://www.espn.com/nba/story/_/id/48185582/nba-2025-2026-regular-season-final-month-giannis-jayson-tatum-more",
         "https://www.espn.com/nba/story/_/id/48233122/nba-power-rankings-all-30-teams-unsung-hero-rookie-veteran-six-man-award",
         "https://www.espn.com/nba/story/_/id/48215728/glass-my-hand-los-angeles-lakers-guard-marcus-smart-return-punch",
         "https://www.espn.com/nba/story/_/id/48165108/nba-2025-2026-shai-gilgeous-alexander-wilt-chamberlain-oklahoma-city-thunder",
         "https://www.espn.com/nba/story/_/id/48196709/bam-adebayo-miami-heat-83-points-team-loaded-aau-high-school",
         "https://www.espn.com/nba/story/_/id/48174027/27-straight-wins-lebron-james-most-dominant-stretch-career-heat-cavaliers-lakers-moments" 
    ]
    fetch_articles(test_urls)