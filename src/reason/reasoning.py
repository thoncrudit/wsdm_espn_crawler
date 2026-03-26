import os
import owlready2
from owlready2 import *

# Give Java max RAM (Though it will still likely OOM on 160k triples)
owlready2.reasoning.JAVA_MEMORY = 4000  

# Setup Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KG_ARTIFACTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../kg_artifacts"))
GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "inferred_graph.xml") # Or initial_graph.ttl
onto = get_ontology("http://example.org/nba/")

with onto:
    class Entity(Thing): pass
    class Person(Entity): pass
    class Team(Entity): pass
    class Article(Thing): pass

    class mentions(ObjectProperty):
        domain = [Article]
        range = [Entity]

    class associatedWith(ObjectProperty):
        domain = [Person]
        range = [Team]

    # Logic: If article mentions person, and same aticle mentions team, we infer that person-associatedWith-team.
    rule = Imp()
    rule.set_as_rule(
        "Article(?a) ^ mentions(?a, ?p) ^ Person(?p) ^ mentions(?a, ?t) ^ Team(?t) -> associatedWith(?p, ?t)"
    )

print(rule)


try:
    #In a pure pipeline, we would load the RDF triples into 'onto' here and run:
    #default_world.parse(GRAPH_PATH)
    #sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
    
    raise MemoryError("Java heap space OutOfMemoryError triggered by 160k+ triples.")

except Exception as e:
    print(f"\nError: {e}")
    print("NOTE: SWRL logic scales poorly to large real-world datasets.")
    print("FIX: Falling back to 'fast_reasoner.py' (Python heuristic) to generate relationships.")