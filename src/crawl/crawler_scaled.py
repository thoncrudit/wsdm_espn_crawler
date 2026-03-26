import os
import time
import json
import requests
from bs4 import BeautifulSoup
import spacy

#1. Setup paths and models
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data"))
OUTPUT_FILE = os.path.join(DATA_DIR, "massive_extracted_entities.json")

nlp = spacy.load("en_core_web_sm")

#2. Spider Configuration
START_URL = "https://www.espn.com/nba/"
MAX_ARTICLES = 1000  # 1000 articles * ~100 triples per article = ~100,000 triples
visited_urls = set()
urls_to_visit = [START_URL]
all_extracted_data = []

HEADERS = {"User-Agent": "NBA_KG_Bot/2.0 (Academic project w/ limited rate)"}

def clean_entity(text):
    """Cleans up noisy text from the NLP model."""
    return text.replace("'s", "").replace("\n", "").replace("\r", "").strip()

def process_article(url):
    """Scrapes the article, runs NER, and finds new links to crawl."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #1. Extract text
        paragraphs = soup.find_all('p')
        full_text = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 20])
        
        if not full_text:
            return [] #skip empty pages (like video-only pages)
            
        # 2. Run NLP
        doc = nlp(full_text)
        entities = []
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE"]:
                clean_name = clean_entity(ent.text)
                if len(clean_name) > 2:
                    entities.append({"name": clean_name, "type": ent.label_})
                    
        #3. Find more links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Only grab ESPN NBA story links that we haven't seen yet
            if "/nba/story/" in href and href not in visited_urls and href not in urls_to_visit:
                if href.startswith("/"):
                    href = "https://www.espn.com" + href
                urls_to_visit.append(href)
                
        return entities
        
    except Exception as e:
        print(f"skipped {url} (Error: {e})")
        return []

print(f"dtarting deep crawler. Target: {MAX_ARTICLES} articles.")
articles_scraped = 0

while urls_to_visit and articles_scraped < MAX_ARTICLES:
    current_url = urls_to_visit.pop(0)
    
    if current_url in visited_urls:
        continue
        
    visited_urls.add(current_url)
    
    #We only want to process actual story articles, not the homepage itself
    if "/story/" in current_url:
        print(f"[{articles_scraped + 1}/{MAX_ARTICLES}] scraping: {current_url}")
        entities = process_article(current_url)
        
        if entities:
            all_extracted_data.append({
                "url": current_url,
                "entities": entities
            })
            articles_scraped += 1
            
            #Save progress every 10 articles so we don't lose data if it crashes
            if articles_scraped % 10 == 0:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_extracted_data, f, indent=4)
                    
        time.sleep(1)
    else:
        #If it's the homepage, just scrape it for links without counting it as an article
        process_article(current_url)

#Final save
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_extracted_data, f, indent=4)

print(f"\nCrawl complete. Saved {articles_scraped} articles to {OUTPUT_FILE}")