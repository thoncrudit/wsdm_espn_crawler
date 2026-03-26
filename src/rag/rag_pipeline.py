import os
import requests
from rdflib import Graph

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KG_ARTIFACTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../kg_artifacts"))
INFERRED_GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "inferred_graph.xml")
ALIGNMENT_GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "alignment.ttl")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

SCHEMA_SUMMARY = """
PREFIX nba: <http://example.org/nba/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

1. Players are associated with Teams via: ?player nba:associatedWith ?team
2. Always search for teams using a label filter on the ?team variable.
3. If using LCASE(), the search keyword inside CONTAINS MUST also be completely lowercase.

GOLDEN EXAMPLE:
Question: "Who plays for the Lakers?"
SPARQL:
SELECT DISTINCT ?player_name WHERE {
  ?player nba:associatedWith ?team .
  ?team rdfs:label ?team_label .
  FILTER(CONTAINS(LCASE(STR(?team_label)), "lakers"))
  ?player rdfs:label ?player_name .
}
"""

def query_ollama(prompt):
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"].strip()

def translate_to_sparql(question, error_msg=None, previous_query=None):
    prompt = f"""
    You are a SPARQL expert. Translate this question into a query.
    Question: "{question}"
    {SCHEMA_SUMMARY}
    Return ONLY the raw SPARQL code. No markdown.
    """
    if error_msg:
        prompt += f"\nPrevious failed query: {previous_query}\nError: {error_msg}\nFix it!"
    
    raw_response = query_ollama(prompt)
    return raw_response.replace("```sparql", "").replace("```", "").strip()

def execute_sparql(graph, question):
    query = translate_to_sparql(question)
    print(f"\n[Running Query]:\n{query}")
    try:
        results = graph.query(query)
        output = []
        for row in results:
            output.append(" | ".join([str(term).split('/')[-1] for term in row]))
        return output if output else ["No results found in the graph."]
    except Exception as e:
        return [f"Error: {e}"]

def rag_chat(graph):
    print("\nNBA ALIGNED RAG")
    while True:
        user_q = input("\nQuestion: ")
        if user_q.lower() == 'exit': break
        
        # RAG Logic
        facts = execute_sparql(graph, user_q)
        context = "\n".join(facts)
        
        final_prompt = f"""
        Answer the question using ONLY these graph facts:
        {context}
        If the facts say "No results found", you MUST reply exactly: "I do not know based on the graph." Do not add outside knowledge.
        Question: {user_q}
        """
        print("\n[AI Answer]:")
        print(query_ollama(final_prompt))

if __name__ == "__main__":
    g = Graph()
    if os.path.exists(INFERRED_GRAPH_PATH):
        g.parse(INFERRED_GRAPH_PATH, format="xml")
    if os.path.exists(ALIGNMENT_GRAPH_PATH):
        g.parse(ALIGNMENT_GRAPH_PATH, format="turtle")
    
    rag_chat(g)
