from chunking import parse_bundestag_pdf_manual_structure_aware
from ingestion import create_client, initialize_hybrid_collection, ingest_data

if __name__ == '__main__':
    pdf_path = "/Users/mburger/Downloads/21080.pdf"
    speech_chunks = parse_bundestag_pdf_manual_structure_aware(pdf_path)
    client = create_client()

    # Change the logic here later so we can incrementally insert data
    initialize_hybrid_collection(client, "bundestag_collection")
    ingest_data(client, speech_chunks, "bundestag_collection")