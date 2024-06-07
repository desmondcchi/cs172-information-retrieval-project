import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
import time
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

def create_index(dir: str, scraped_data_file: str):
  """
  dir: Directory name (no need for absolute path).
  scraped_data_file: jsonl file name for scraped data.
  """
  dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"./{dir}"))
  if not os.path.exists(dir_path):
    os.mkdir(dir_path)
  store = SimpleFSDirectory(Paths.get(dir_path))
  analyzer = StandardAnalyzer()
  config = IndexWriterConfig(analyzer)
  config.setSimilarity(BM25Similarity())
  config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
  writer = IndexWriter(store, config)

  metaType = FieldType()
  metaType.setStored(True)
  metaType.setTokenized(False)

  contextType = FieldType()
  contextType.setStored(True)
  contextType.setTokenized(True)
  contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

  # Open jsonl file.
  scraped_data = open(os.path.abspath(os.path.join(os.path.dirname(__file__), f"../scraped_data/{scraped_data_file}")), "r")

  # Add records to index writer.
  for record in list(scraped_data):
    result = json.loads(record)
    title = result["title"]
    main_content = result["main_content"]

    doc = Document()
    doc.add(Field("Title", str(title), metaType))
    doc.add(Field("Main Content", str(main_content), contextType))
    writer.addDocument(doc)

  writer.close()

def retrieve(storedir: str, query: str):
  """
  storedir = Directory for stored indexes."
  query = Query.
  """
  dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"./{storedir}"))
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
scraped_data_file = sys.argv[1]
start_time = time.time()
create_index('index/', scraped_data_file)
end_time = time.time()
print(f"Indexing took {end_time - start_time:.2f} seconds")
# retrieve('index/', 'UC riverside students and school')


