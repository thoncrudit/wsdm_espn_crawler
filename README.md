# End-to-End NBA Knowledge Graph and RAG Pipeline

This repository contains a complete pipeline for building, reasoning over, and querying a domain-specific Knowledge Graph (KG) about the NBA. It integrates web scraping, Natural Language Processing (NER), Semantic Web technologies (RDF/OWL), Knowledge Graph Embeddings (KGE), and a Local LLM Retrieval-Augmented Generation (RAG) system.

## Hardware requirements
* **RAM:** 16GB+ recommended (min 8GB). The inferred graph contains over 211,000 triples, which requires significant memory for in-memory graph operations.
* **Storage:** ~500MB of free space for KG artifacts, KGE datasets, and environment libraries.
* **LLM Engine:** A CPU or GPU capable of running **Ollama** locally (Llama 3 8B model).

## Installation and environment setup
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
   cd YOUR-REPO-NAME
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the spaCy NER model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Install and start Ollama:**
   * Download Ollama from [ollama.com](https://ollama.com/).
   * Pull the Llama 3 model:
     ```bash
     ollama pull llama3
     ```
   * Ensure the Ollama server is running in the background before launching the RAG demo.

## Repository structure
```text
project-root/
├── src/
│   ├── crawl/       # Web scraping scripts (crawler_basic.py, crawler_scaled.py)
│   ├── ie/          # Information Extraction and NER (ner_pipeline.py)
│   ├── kg/          # Graph construction and Wikidata alignment (build_initial_kg.py, alignment.py)
│   ├── reason/      # SWRL (reasoning.py) and Python heuristic reasoning (fast_reasoner.py)
│   ├── kge/         # Embedding training prep and evaluation (train_kge.py)
│   └── rag/         # Natural Language to SPARQL RAG pipeline (rag_pipeline.py)
├── data/            # KGE split datasets (train.txt, valid.txt, test.txt)
├── kg_artifacts/    # Generated graphs (initial_graph.ttl, inferred_graph.xml, alignment.ttl)
├── notebooks/       # Jupyter notebook for pipeline validation (test_pipeline.ipynb)
├── reports/         # Final Project PDF Report
├── README.md
├── LICENSE
└── requirements.txt
```

## How to run the modules

### 1. Data Acquisition and IE
To scrape NBA articles and extract entities (Note: `crawler_scaled.py` was used to build the massive dataset):
```bash
python src/crawl/crawler_scaled.py
python src/ie/ner_pipeline.py
```

### 2. KG Construction and Alignment
To build the initial RDF graph and link top entities to Wikidata using the Smart Alignment strategy:
```bash
python src/kg/build_initial_kg.py
python src/kg/alignment.py
```

### 3. Reasoning
*Note:* `src/reason/reasoning.py` contains the formal SWRL rule utilizing `owlready2` and Pellet. However, due to Java Heap memory limits (`OutOfMemoryError`) when processing our 160k+ triple graph, we implement a custom Python-based heuristic reasoning expansion.
```bash
# Run the scalable heuristic reasoner to generate `associatedWith` links:
python src/reason/fast_reasoner.py
```

### 4. Knowledge Graph Embeddings (KGE)
To prepare the `train/valid/test` splits and view the TransE vs. RotatE evaluation metrics:
```bash
python src/kge/train_kge.py
```

### 5. Run the pipeline validation notebook
For a quick validation of the graph statistics, reasoning output, and alignment layers without running the full codebase, open and run:
`notebooks/test_pipeline.ipynb`

## How to run the RAG Demo
Ensure your Ollama server is running with the `llama3` model. Then, launch the interactive Natural Language to SPARQL CLI:

```bash
python src/rag/rag_pipeline.py
```
*Example Queries to try:*
* "Who plays for the Boston Celtics?"
* "Which team is associated with Moses Moody?"
* "What mentions the Detroit Pistons?"