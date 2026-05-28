package de.bundestagexplore.ai

import dev.langchain4j.model.embedding.EmbeddingModel
import dev.langchain4j.model.embedding.onnx.OnnxEmbeddingModel
import dev.langchain4j.model.embedding.onnx.PoolingMode
import jakarta.enterprise.context.ApplicationScoped
import jakarta.enterprise.inject.Produces
import java.io.IOException
import java.net.URL
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardCopyOption

@ApplicationScoped
class GermanEmbeddingModelProducer {

    @Produces
    @ApplicationScoped
    fun embeddingModel(): EmbeddingModel {
        try {
            val modelUrl = "https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/resolve/main/onnx/model.onnx"
            val tokenizerUrl = "https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/resolve/main/tokenizer.json"

            val cacheDir = Path.of(System.getProperty("user.home"), ".cache", "onnx-models")
            Files.createDirectories(cacheDir)

            val modelPath = cacheDir.resolve("multilingual-model.onnx")
            val tokenizerPath = cacheDir.resolve("multilingual-tokenizer.json")

            downloadIfMissing(modelUrl, modelPath)
            downloadIfMissing(tokenizerUrl, tokenizerPath)

            return OnnxEmbeddingModel(
                modelPath.toString(),
                tokenizerPath.toString(),
                PoolingMode.MEAN
            )
        } catch (e: Exception) {
            throw RuntimeException("Error while initializing german embedding model", e)
        }
    }

    private fun downloadIfMissing(urlString: String, target: Path) {
        if (!Files.exists(target)) {
            println("📥 Downloading embedding model: ${target.fileName}")
            try {
                URL(urlString).openStream().use { inputStream ->
                    Files.copy(inputStream, target, StandardCopyOption.REPLACE_EXISTING)
                }
            } catch (e: IOException) {
                throw RuntimeException("Error downloading from $urlString", e)
            }
        }
    }
}