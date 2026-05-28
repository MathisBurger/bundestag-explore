from qdrant_client import QdrantClient
from qdrant_client.http.models import TextIndexParams, TokenizerType, TextIndexType
from qdrant_client.models import PayloadSchemaType
from qdrant_client.models import Distance, VectorParams, SparseVectorParams
from fastembed.embedding import DefaultEmbedding
from fastembed.sparse import SparseTextEmbedding

def create_client():
    return QdrantClient(host="localhost", port=6333)


def initialize_hybrid_collection(client, collection_name):
    """
    Creates or recreates a Qdrant collection configured for unified hybrid search.
    """
    # Check if collection already exists to prevent duplication during testing
    if client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' exists. Recreating it for clean ingestion...")
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        # 1. Config for Dense Vectors (Semantic search)
        # BGE-Small-EN-v1.5/Multilingual models use 384 dimensions and Cosine distance
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        ),
        # 2. Config for Sparse Vectors (Keyword/Quote search)
        # BM42 is Qdrant's native fast lexical model
        sparse_vectors_config={
            "text-sparse": SparseVectorParams()
        },
        on_disk_payload=True
    )
    client.create_payload_index(collection_name, "speaker", PayloadSchemaType.KEYWORD)
    client.create_payload_index(collection_name, "party", PayloadSchemaType.KEYWORD)

    client.create_payload_index(collection_name, "date", PayloadSchemaType.DATETIME)
    client.create_payload_index(collection_name, "sachgebiete", PayloadSchemaType.KEYWORD)

    client.create_payload_index(collection_name, "initiativen", PayloadSchemaType.KEYWORD)

    client.create_payload_index(
        collection_name=collection_name,
        field_name="vorgangs_titel",
        field_schema=TextIndexParams(
            type=TextIndexType.TEXT,
            tokenizer=TokenizerType.WORD,
            lowercase=True
        )
    )
    print(f"Collection '{collection_name}' initialized successfully.")


def ingest_data(client, speech_chunks, collection_name="bundestag_collection"):

    dense_model = DefaultEmbedding(model_name="BAAI/bge-small-en-v1.5")
    # BM42 handles word frequencies and exact keyword token matches
    sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")

    # 4. Prepare batch structures
    texts = [chunk["text"] for chunk in speech_chunks]

    print("Generating dense embeddings...")
    dense_embeddings = list(dense_model.embed(texts))

    print("Generating sparse lexical embeddings...")
    sparse_embeddings = list(sparse_model.embed(texts))

    # 5. Package and upload to Qdrant
    points = []
    for idx, chunk in enumerate(speech_chunks):
        # Convert fastembed sparse matrix format into Qdrant API structure
        sparse_vector = sparse_embeddings[idx]
        qdrant_sparse = {
            "indices": sparse_vector.indices.tolist(),
            "values": sparse_vector.values.tolist()
        }

        points.append({
            "id": idx,
            "vector": {
                "": dense_embeddings[idx].tolist(),  # Main dense vector
                "text-sparse": qdrant_sparse  # Named sparse vector
            },
            # The payload stores all the metadata you extracted for filtering later
            "payload": {
                "speaker": chunk["speaker"],
                "party": chunk["party"],
                "topic": chunk["topic"],
                "text": chunk["text"]
            }
        })

    print(f"Uploading {len(points)} records to Qdrant...")
    client.upsert(collection_name=collection_name, points=points)
    print("Ingestion complete!")


