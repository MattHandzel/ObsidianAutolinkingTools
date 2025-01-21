from utils import *
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
import os
import dotenv

dotenv.load_dotenv()


def init_vector_db():
    client = QdrantClient(path="./qdrant_db")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    if not client.get_collections().collections:
        client.create_collection(
            collection_name="notes",
            vectors_config=VectorParams(
                size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE
            ),
        )

    return client, model


client, model = init_vector_db()

import hashlib

secret_key = os.getenv("SECRET_KEY")
assert secret_key, "SECRET_KEY is not set in .env"


def get_topics_for_every_note(note_path, meta_data, content, root_directory):
    note_title = (
        ("\t" + meta_data["title"])
        if "title" in meta_data
        else ("\t" + str(meta_data["id"]) if "id" in meta_data else "")
    )
    # hash note_title with secret key
    hash_object = hashlib.sha256()
    hash_object.update(note_title.encode("utf-8") + secret_key.encode("utf-8"))
    note_id = int(hash_object.hexdigest(), 16)

    # Check if note is already in the database
    search_result = client.search(
        collection_name="notes", query_vector=model.encode(note_title), limit=1
    )

    print("note_id is", note_id)
    if not search_result or search_result[0].score < 0.95:
        # Embed and store the note
        embedding = model.encode(content).tolist()
        client.upsert(
            collection_name="notes",
            points=[
                PointStruct(
                    id=note_id,
                    payload={"title": note_title, "content": content},
                    vector=embedding,
                )
            ],
        )
        print(f"Embedded note: {note_title}")
    else:
        print(f"Note already embedded: {note_title}")

    # Find similar notes
    similar_notes = client.search(
        collection_name="notes", query_vector=model.encode(content), limit=10
    )

    result = "Similar notes:\n"
    for note in similar_notes:
        result += f"- {note.payload['title']} (similarity: {note.score:.2f})\n"

    print(result)
    return None, None, False


def query_notes(query):
    query_vector = model.encode(query).tolist()
    results = client.search(
        collection_name="notes", query_vector=query_vector, limit=10
    )

    print(f"Query: {query}")
    print("Results:")
    for result in results:
        print(f"- {result.payload['title']} (similarity: {result.score:.2f})")
        print(f"  Content: {result.payload['content'][:100]}...")
        print("-----------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", type=str)
    parser.add_argument("--query", type=str, help="Query to search for similar notes")
    args = parser.parse_args()
    root_directory = args.root_directory

    if args.query:
        query_notes(args.query)
    else:
        loop_through_notes(
            root_directory,
            [get_topics_for_every_note],
            clear_bottom_matter=False,
        )
