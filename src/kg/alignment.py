import os
import time
import requests
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import OWL, RDFS

#setup namespaces
NBA = Namespace("http://example.org/nba/")
WD = Namespace("http://www.wikidata.org/entity/")

KG_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../kg_artifacts"))
INITIAL_GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "initial_graph.ttl")
ALIGNMENT_GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "alignment.ttl")

def search_wikidata(label):
    """Pings Wikidata with exponential backoff for 429 error."""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": label,
        "language": "en",
        "format": "json",
        "limit": 1
    }

    headers = {"User-Agent": "NBA-Student-Project-Bot/1.1 (Academic project)"}

    for attempt in range(3): #Try 3 times
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 429:
                wait = (attempt + 1) * 60 
                print(f"429 Error. Pause for {wait}sec")
                time.sleep(wait)
                continue
            
            response.raise_for_status()
            data = response.json()
            if data.get("search"):
                return data["search"][0]["id"]
            return None
        except Exception as e:
            print(f"Error searching {label}: {e}")
            return None
    return None

def run_alignment():
    g = Graph().parse(INITIAL_GRAPH_PATH, format="turtle")
    align_g = Graph()

    #1. count occurrences so we don't align bad data
    counts = {}
    for s, p, o in g.triples((None, NBA.mentions, None)):
        counts[o] = counts.get(o, 0) + 1

    #2. Filter only aligns entities mentioned > 5 times
    top_entities = [e for e, c in counts.items() if c > 5]
    print(f"Found {len(top_entities)} high-value entities to align.")

    for entity in top_entities:
        labels = list(g.objects(entity, RDFS.label))
        if not labels: continue
        label = str(labels[0])

        print(f"Searching Wikidata for: {label}")
        wd_id = search_wikidata(label)
        
        if wd_id:
            align_g.add((entity, OWL.sameAs, WD[wd_id]))
            print(f" Matched to {wd_id}")
        
        time.sleep(2)

    align_g.serialize(destination=ALIGNMENT_GRAPH_PATH, format="turtle")
    print(f"Saved {len(align_g)} alignments.")

if __name__ == "__main__":
    run_alignment()