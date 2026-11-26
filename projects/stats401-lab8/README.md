# STATS 401 Lab 8 · Semantic map of a university bulletin

Explore passages from the 2023–24 Duke Kunshan University undergraduate bulletin in the [interactive lab](lab8/index.html). It includes a UMAP map, a topic-by-section matrix, and passage-level nearest neighbors.

- [Analysis script](lab8/process_bulletin.py) extracts the bundled PDF, embeds passages with MiniLM, clusters them with K-means, and builds the lab.
- [Analyzed passages CSV](lab8/full_corpus/analyzed_passages.csv) and [analysis JSON](lab8/full_corpus/analysis.json) contain the saved results.

To rebuild, install `pymupdf numpy scikit-learn umap-learn tokenizers onnxruntime` and run `python lab8/process_bulletin.py` from this directory. The script downloads model weights on the first run. The interactive page uses the bundled D3.js library.
