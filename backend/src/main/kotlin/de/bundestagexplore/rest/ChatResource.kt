package de.bundestagexplore.rest

import de.bundestagexplore.ai.BundestagRetriever
import de.bundestagexplore.dto.ChatRequest
import de.bundestagexplore.dto.ChatResponse
import de.bundestagexplore.dto.Citation
import de.bundestagexplore.service.ChatBotService
import dev.langchain4j.rag.query.Query
import jakarta.inject.Inject
import jakarta.ws.rs.POST
import jakarta.ws.rs.Path

@Path("/v1/chat")
class ChatResource {

    @Inject
    lateinit var retrieverBuilder: BundestagRetriever

    @Inject
    lateinit var chatBotService: ChatBotService

    @POST
    fun processChat(request: ChatRequest): ChatResponse {
        val retriever = retrieverBuilder.createRetriever(request.party)

        val contents = retriever.retrieve(Query.from(request.query))

        val contextBlock = contents.joinToString(separator = "\n---\n") { content ->
            val segment = content.textSegment()
            val metadata = segment.metadata()

            val speaker = metadata.getString("speaker") ?: "Unbekannt"
            val party = metadata.getString("party") ?: "Fraktionslos"
            val fullContext = metadata.getString("full_context") ?: segment.text()

            "Redner: $speaker ($party)\nText: $fullContext"
        }

        val citations = contents.map { content ->
            val metadata = content.textSegment().metadata()
            Citation(
                speaker = metadata.getString("speaker") ?: "Unbekannt",
                party = metadata.getString("party") ?: "Fraktionslos",
                topic = metadata.getString("topic") ?: "Plenardebatte"
            )
        }.distinct()

        val aiAnswer = chatBotService.chat(contextBlock, request.query)

        return ChatResponse(
            answer = aiAnswer,
            citations = citations
        )
    }
}