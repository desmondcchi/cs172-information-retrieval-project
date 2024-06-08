## In the terminal, "export FLASK_APP=flask_demo" (without .py)
## flask run -h 0.0.0.0 -p 8888

import lucene
import os
import re
from org.apache.lucene.store import MMapDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from flask import request, Flask, render_template

app = Flask(__name__)


def get_snippet(query: str, text: str):
    query_terms = sorted(query.split(), key=len, reverse=True)
    sentences = re.split("[!.]+", text)
    query_terms_re = re.compile('|'.join(query_terms), re.IGNORECASE)

    def repl(matched_term):
        return f"<mark>{matched_term.group(0)}</mark>"

    for sentence in sentences:
        snippet, matched = query_terms_re.subn(repl, sentence)
        if matched: return snippet

    return "snippet"

def retrieve(storedir: str, query: str):
    """
    storedir = Directory for stored indexes."
    query = Query.
    """
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('Main Content', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "snippet": get_snippet(query, doc.get("Main Content")),
            "text": doc.get("Main Content"),
            "title": doc.get("Title")
        })
    return topkdocs

@app.route('/', methods = ['POST', 'GET'])
def input():
    return render_template('input_page.html')

@app.route('/output', methods = ['POST', 'GET'])
def output():
    if request.method == 'GET':
        return f"Nothing"
    if request.method == 'POST':
        form_data = request.form
        query = form_data['query']
        if query == '':
            return render_template('empty_output.html')
        lucene.getVMEnv().attachCurrentThread()
        docs = retrieve('../indexer/index/', str(query))
        Query = [{"title" : query}]
        return render_template('output_page.html',lucene_output = Query+docs)
    
lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    
if __name__ == "__main__":
    app.run(debug=True)
