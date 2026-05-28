package de.bundestagexplore.ai

import dev.langchain4j.data.segment.TextSegment
import dev.langchain4j.model.embedding.EmbeddingModel
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever
import jakarta.enterprise.context.ApplicationScoped
import jakarta.inject.Inject
import dev.langchain4j.store.embedding.EmbeddingStore
import dev.langchain4j.store.embedding.filter.comparison.IsEqualTo

@ApplicationScoped
public class BundestagRetriever {
    @Inject
    lateinit var embeddingStore: EmbeddingStore<TextSegment>

    @Inject
    lateinit var embeddingModel: EmbeddingModel

    fun createRetriever(partyFilter: String?): EmbeddingStoreContentRetriever {
        val builder = EmbeddingStoreContentRetriever.builder()
            .embeddingStore(embeddingStore)
            .embeddingModel(embeddingModel)
            .maxResults(4)
            .minScore(0.6)

        if (!partyFilter.isNullOrBlank()) {
            builder.filter(IsEqualTo("party", partyFilter))
        }

        return builder.build()
    }

}