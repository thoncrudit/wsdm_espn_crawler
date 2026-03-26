import os
import pandas as pd
from rdflib import Graph
from pykeen.pipeline import pipeline
from pykeen.datasets import PathDataset

#1.setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KG_ARTIFACTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../kg_artifacts"))
INFERRED_GRAPH_PATH = os.path.join(KG_ARTIFACTS_DIR, "inferred_graph.xml")

KGE_DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/kge"))
os.makedirs(KGE_DATA_DIR, exist_ok=True)

def prepare_data():
    """converts XML graph into plain text triples and uses Pandas to split."""
    print("Loading inferred graph for PyKEEN...")
    g = Graph()
    g.parse(INFERRED_GRAPH_PATH, format="xml")
    
    #PyKEEN needs a simple list of strings: head > relation > tail]
    triples = []
    for s, p, o in g:
        #strip out the bulky "http://example.org/nba/" part to keep the text clean
        s_str = str(s).split('/')[-1].split('#')[-1]
        p_str = str(p).split('/')[-1].split('#')[-1]
        o_str = str(o).split('/')[-1].split('#')[-1]
        triples.append([s_str, p_str, o_str])
        
    #convert to Pandas and shuffle
    df = pd.DataFrame(triples, columns=["head", "relation", "tail"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    #2. 80/10/10 splits
    train_end = int(len(df) * 0.8)
    valid_end = int(len(df) * 0.9)
    train_df = df.iloc[:train_end]
    valid_df = df.iloc[train_end:valid_end]
    test_df = df.iloc[valid_end:]
    train_path = os.path.join(KGE_DATA_DIR, "train.txt")
    valid_path = os.path.join(KGE_DATA_DIR, "valid.txt")
    test_path = os.path.join(KGE_DATA_DIR, "test.txt")
    
    #Save formatted TSV files for grader 
    #/!\ TAB SEPARATED AND NO HEADERS FOR PYKEEN
    train_df.to_csv(train_path, sep='\t', index=False, header=False)
    valid_df.to_csv(valid_path, sep='\t', index=False, header=False)
    test_df.to_csv(test_path, sep='\t', index=False, header=False)
    print(f"Saved dataset splits to {KGE_DATA_DIR}")
    return train_path, test_path, valid_path

def train_and_evaluate(train_path, test_path, valid_path, model_name):
    """Trains a KGE model and extracts the metrics."""
    print(f"\n=============================================")
    print(f"Training model: {model_name}")
    print(f"===============================================")
    
    dataset = PathDataset(
        training_path=train_path,
        testing_path=test_path,
        validation_path=valid_path
    )
    
    result = pipeline(
        dataset=dataset,
        model=model_name,
        training_kwargs=dict(num_epochs=15), # CHANGE EPOCHS IF NEEDED
        random_seed=42,
        device='cpu'
    )
    
    #Metrics (MRR, Hits@1/3/10)
    print(f"\n- {model_name} Final Metrics -")
    print(f"MRR:     {result.metric_results.get_metric('mrr'):.4f}")
    print(f"Hits@1:  {result.metric_results.get_metric('hits@1'):.4f}")
    print(f"Hits@3:  {result.metric_results.get_metric('hits@3'):.4f}")
    print(f"Hits@10: {result.metric_results.get_metric('hits@10'):.4f}")
    
    return result

if __name__ == "__main__":
    if not os.path.exists(INFERRED_GRAPH_PATH):
        print(f"Error: Could not find {INFERRED_GRAPH_PATH}")
    else:
        train_p, test_p, valid_p = prepare_data()
        
        #4. Two models 
        transe_results = train_and_evaluate(train_p, test_p, valid_p, "TransE")
        rotate_results = train_and_evaluate(train_p, test_p, valid_p, "RotatE")
        
        print("\nKGE training complete")