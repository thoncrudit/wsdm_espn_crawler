import os
import json
import re
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

#setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLEAN_DATA_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/extracted_entities.json"))
KG_ARTIFACTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../kg_artifacts"))
OUTPUT_GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "initial_graph.ttl")

#namespace
NBA = Namespace("http://example.org/nba/")

#manual overrides NEED TO FIND SOLUTION
ENTITY_CORRECTIONS = {
    "Spurs": {"uri": NBA.SanAntonioSpurs, "type": NBA.Team},
    "San Antonio Spurs": {"uri": NBA.SanAntonioSpurs, "type": NBA.Team},
    "Tatum": {"uri": NBA.JaysonTatum, "type": NBA.Player},
    "Jayson Tatum": {"uri": NBA.JaysonTatum, "type": NBA.Player},
    "Giannis": {"uri": NBA.GiannisAntetokounmpo, "type": NBA.Player},
    "Victor Wembanyama": {"uri": NBA.VictorWembanyama, "type": NBA.Player},
}

def create_uri(text):
    """Converts a string into a clean, strictly alphanumeric URI."""
    # This regex removes ALL punctuation, spaces, and invisible characters!
    clean_str = re.sub(r'[^A-Za-z0-9]', '', text)
    return NBA[clean_str]

def build_graph():
    g = Graph()
    g.bind("nba", NBA)

    if not os.path.exists(CLEAN_DATA_PATH):
        print(f"data not found at {CLEAN_DATA_PATH}")
        return

    with open(CLEAN_DATA_PATH, "r", encoding="utf-8") as f:
        articles = json.load(f)

    os.makedirs(KG_ARTIFACTS_DIR, exist_ok=True)

    print("building rdf triples")
    
    for article in articles:
        article_uri = URIRef(article["url"])
        g.add((article_uri, RDF.type, NBA.Article))
        
        for ent in article["entities"]:
            raw_text = ent["name"]
            ent_type = ent["type"]

            #check manual corrections
            if raw_text in ENTITY_CORRECTIONS:
                entity_uri = ENTITY_CORRECTIONS[raw_text]["uri"]
                entity_type = ENTITY_CORRECTIONS[raw_text]["type"]
            else:
                entity_uri = create_uri(raw_text)
                if ent_type == "PERSON":
                    entity_type = NBA.Player #assuming most people are players
                elif ent_type == "ORG":
                    entity_type = NBA.Team #assuming most orgs are teams
                elif ent_type == "GPE":
                    entity_type = NBA.Location
                else:
                    entity_type = NBA.Entity

            g.add((entity_uri, RDF.type, entity_type))
            
            g.add((article_uri, NBA.mentions, entity_uri))
            
            g.add((entity_uri, RDFS.label, Literal(raw_text)))

    g.serialize(destination=OUTPUT_GRAPH_PATH, format="turtle")
    
    print(f"graph built and saved to {OUTPUT_GRAPH_PATH}")
    print(f"{len(g)} triplets")

if __name__ == "__main__":
    build_graph()