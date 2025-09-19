from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma

load_dotenv()


file_path = "./lab/files/nke-10k-2023.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

# print(len(docs))

# print(f"{docs[0].page_content[:200]}\n")
# print(docs[0].metadata)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

# print(len(all_splits))

embeddings = HuggingFaceEndpointEmbeddings(
    model="Qwen/Qwen3-Embedding-8B", provider="nebius"
)

# vector_1 = embeddings.embed_query(all_splits[0].page_content)
# vector_2 = embeddings.embed_query(all_splits[1].page_content)
# assert len(vector_1) == len(vector_2)
# print(f"Generated vectors of length {len(vector_1)}\n")
# print(vector_1[:10])

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./lab/chroma_db",  # Where to save data locally, remove if not necessary
)

ids = vector_store.add_documents(documents=all_splits)

results = vector_store.similarity_search(
    "How many distribution centers does Nike have in the US?"
)

print(results[0])
