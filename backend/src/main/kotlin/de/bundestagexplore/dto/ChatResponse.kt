package de.bundestagexplore.dto

data class ChatResponse(
    val answer: String,
    val citations: List<Citation>
)
