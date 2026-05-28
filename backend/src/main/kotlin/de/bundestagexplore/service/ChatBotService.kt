package de.bundestagexplore.service

import dev.langchain4j.service.SystemMessage
import dev.langchain4j.service.UserMessage
import io.quarkiverse.langchain4j.RegisterAiService

@RegisterAiService
interface ChatBotService {
    @SystemMessage(
        """
            Du bist ein neutraler, präziser KI-Assistent für deutsche Parlamentsdokumente.
        Beantworte die Frage des Benutzers AUSSCHLIESSLICH basierend auf dem bereitgestellten Kontext.
        Wenn der Kontext die Antwort nicht hergibt, sage: 'Dazu liegen mir keine Protokolldaten vor.'
        Zitiere Fakten sachlich unter Nennung des Redners und seiner Fraktion.
        """
    )
    @UserMessage("""
        Hier ist der aufgearbeitete Kontext aus den Bundestagssitzungen:
        {context}

        Nutzerfrage: {question}
    """)
    fun chat(context: String, question: String): String
}