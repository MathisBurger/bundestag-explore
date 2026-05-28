from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from models import ChatRequest, ChatResponse, Citation

app = FastAPI(title="Bundestag Explore AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
qdrant_client = QdrantClient(url="http://localhost:6333")
ollama_client = OllamaLLM(base_url="http://localhost:11434", model="qwen2.5:1.5b")


@app.post("/v1/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    try:
        query_vector = embedding_model.encode(request.query)
        qdrant_filter = None
        if request.party:
            from qdrant_client.http import models as rest_models
            qdrant_filter = rest_models.Filter(
                must=[
                    rest_models.FieldCondition(
                        key="party",
                        match=rest_models.MatchValue(value=request.party)
                    )
                ]
            )

        search_results = qdrant_client.query_points(
            collection_name="bundestag_collection",
            query=query_vector.tolist(),
            query_filter=qdrant_filter,
            limit=4
        ).points

        context_segments = []
        citations = []

        for hit in search_results:
            payload = hit.payload
            speaker = payload.get("speaker", "Unbekannt")
            party = payload.get("party", "Fraktionslos")
            topic = payload.get("topic", "Plenardebatte")
            full_context = payload.get("full_context", hit.payload.get("text", ""))

            context_segments.append(f"Redner: {speaker} ({party})\nText: {full_context}")

            citations.append(Citation(speaker=speaker, party=party, topic=topic))

        # Duplikate bei den Citations entfernen
        unique_citations = list({f"{c.speaker}-{c.party}": c for c in citations}.values())
        context_block = "\n---\n".join(context_segments)

        # 6. Prompt für Ollama bauen
        prompt = f"""
        Du bist ein neutraler, präziser KI-Assistent für deutsche Parlamentsdokumente.
        Beantworte die Frage des Benutzers AUSSCHLIESSLICH basierend auf dem bereitgestellten Kontext.
        Wenn der Kontext die Antwort nicht hergibt, sage: 'Dazu liegen mir keine Protokolldaten vor.'

        Hier ist der aufgearbeitete Kontext aus den Bundestagssitzungen:
        {context_block}

        Nutzerfrage: {request.query}
        """

        ai_answer = ollama_client.invoke(prompt)

        return ChatResponse(answer=ai_answer, citations=unique_citations)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)