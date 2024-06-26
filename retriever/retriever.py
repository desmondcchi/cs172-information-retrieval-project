import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

def retrieve(storedir: str, query: str):
  """
  storedir = Directory for stored indexes."
  query = Query.
  """
  dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../indexer/{storedir}"))
  searchDir = NIOFSDirectory(Paths.get(dir_path))
  searcher = IndexSearcher(DirectoryReader.open(searchDir))
  searcher.setSimilarity(BM25Similarity())

  parser = QueryParser('Main Content', StandardAnalyzer())
  parsed_query = parser.parse(query)
  

  topDocs = searcher.search(parsed_query, 10).scoreDocs
  topkdocs = []
  for hit in topDocs:
      doc = searcher.doc(hit.doc)
      topkdocs.append({
          "score": hit.score,
          "text": doc.get("Main Content")
      })
  
  print(topkdocs)

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
retrieve('index/', 'GitHub pull request and commits')
