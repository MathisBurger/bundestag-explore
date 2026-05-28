package de.bundestagexplore.dto

data class ChatRequest(
    val query: String,
    val party: String? = null
)
