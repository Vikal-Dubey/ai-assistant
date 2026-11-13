import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url = os.getenv("BASE_URL"),
    api_key = os.getenv("API_KEY")
)

EMBED_MODEL = os.getenv("EMBED_MODEL")

#Get the embedding of a text using EMBED_MODEL
def get_embedding(text):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding

chunks = {
    "c0": "Leave Policies - Maternity Leave\nMaternity leave is 26 weeks of paid leave for the first two children.",
    "c1": "Medical Policy - Maternity Cover\nHospitalization for childbirth is covered up to 75,000 rupees.",
    "c2": "Travel Expense - Reimbursement\nSubmit expense claims within 30 days of the trip. Approved claims are reimbursed within 7 working days.",
    "c3": "Tech Docs - Deployment Windows\nProduction deployments are allowed on Tuesdays and Thursdays between 11 AM and 4 PM."
}

ids = list(chunks.keys())
documents = list(chunks.values())

embeddings = []
for s in documents:
    embedding = get_embedding(s)
    embeddings.append(embedding)

chroma = chromadb.PersistentClient(path="./chroma_db")

zorvex_collection = chroma.get_or_create_collection(
    name = "zorvex_technology",
    configuration = {
        "hnsw": {
            "space": "cosine",
        }
    }
)

zorvex_collection.upsert(
    ids = ids,
    documents = documents,
    embeddings = embeddings
)

query = "What is the maternity leave policy?"
query_embedding = get_embedding(query)

results = zorvex_collection.query(
    query_embeddings = [query_embedding],
    n_results = 2
)

print(results["documents"][0])