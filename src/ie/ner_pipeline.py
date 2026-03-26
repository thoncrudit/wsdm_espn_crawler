import os
import json
from bs4 import BeautifulSoup
import spacy

#setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/raw_espn_articles.json"))
CLEAN_DATA_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/extracted_entities.json"))

def clean_html(raw_html):
    """extracts only the paragraph text from the raw html"""
    soup = BeautifulSoup(raw_html, 'html.parser')
    paragraphs = soup.find_all('p')
    text = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text()) > 30])
    return text

def clean_entity_text(text):
    """cleans noisy NER extractions like trailing possessives and punctuation"""
    #remove unicode apostrophes and possessive forms
    cleaned = text.replace("\u2019s", "").replace("'s", "")
    cleaned = cleaned.strip(" '\".,-")
    return cleaned

def extract_entities(text, nlp_model):
    """runs NER to find people, orgs and locations"""
    doc = nlp_model(text)
    entities = []
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]: 
            clean_text = clean_entity_text(ent.text)
            
            if len(clean_text) > 1: #keep >1 because of names like KD or PJ
                entities.append({
                    "entity": clean_text,
                    "label": ent.label_
                })
    return entities

def process_pipeline():
    nlp = spacy.load("en_core_web_sm")

    if not os.path.exists(RAW_DATA_PATH):
        print(f"raw data not found at {RAW_DATA_PATH} run scraper first")
        return

    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_articles = json.load(f)

    processed_data = []

    for article in raw_articles:
        print(f"processing {article['url']}")
        clean_text = clean_html(article['html'])
        entities = extract_entities(clean_text, nlp)
        
        processed_data.append({
            "url": article['url'],
            "text": clean_text,
            "entities": entities
        })

    #ensure data directory exists (just in case)
    os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)

    with open(CLEAN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=4)
    print(f"extraction completed and saved to {CLEAN_DATA_PATH}")

if __name__ == "__main__":
    process_pipeline()