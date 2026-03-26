import os
from collections import defaultdict
from rdflib import Graph, Namespace

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KG_ARTIFACTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../kg_artifacts"))
GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "inferred_graph.xml")

NBA = Namespace("http://example.org/nba/")
g = Graph()
g.parse(GRAPH_PATH, format="xml")
print(f"Starting triples: {len(g)}")

#1. group all entities by the article/team that mentions them
mentions_by_source = defaultdict(list)

for subject, predicate, obj in g:
    #if the predicate is 'mentions', save the object (the entity) under that subject (the article)
    if "mentions" in str(predicate):
        mentions_by_source[subject].append(obj)

new_triples = 0
for source, entities in mentions_by_source.items():
    limited_entities = entities[:10] 
    for i in range(len(limited_entities)):
        for j in range(i + 1, len(limited_entities)):
            entity_1 = limited_entities[i]
            entity_2 = limited_entities[j]
            
            #don't link entity to itself
            if entity_1 != entity_2:
                g.add((entity_1, NBA.associatedWith, entity_2))
                g.add((entity_2, NBA.associatedWith, entity_1))
                new_triples += 2

print(f"Inferred {new_triples} new 'associatedWith' relationships!")
print(f"Total triples now: {len(g)}")

g.serialize(destination=GRAPH_PATH, format="xml")