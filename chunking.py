import fitz  # PyMuPDF
import re
import uuid

def parse_bundestag_pdf_manual_structure_aware(pdf_path):
    doc = fitz.open(pdf_path)

    current_topic = "Sitzungseröffnung"
    current_speaker = "Präsidium"
    current_party = "Amt"

    all_final_chunks = [] # This will hold our small child chunks

    speaker_pattern = re.compile(
        r"^([A-ZÄÖÜ][a-zßäöü\-\s]+[A-ZÄÖÜ][a-zßäöü]+(?:,\s+(?:Bundesminister|Abgeordneter|Parl\.)\s+[\w\s]+)?)\s*(?:\(([^)]+)\))?:"
    )
    topic_pattern = re.compile(r"(Tagesordnungspunkt(?:e)?\s+\d+|Zusatzpunkt(?:e)?\s+\d+)", re.IGNORECASE)

    # Accumulator for text belonging to the active speech block
    speech_buffer = []

    def flush_current_speech():
        """Helper to break a long speech into small searchable children attached to a parent context."""
        nonlocal speech_buffer
        if not speech_buffer:
            return

        full_speech_text = " ".join(speech_buffer)
        parent_id = str(uuid.uuid4()) # Generate a unique link identifier

        # Split the full speech text into smaller semantic chunks (e.g., roughly every 3-4 sentences)
        # Using a simple sentence splitter for the prototype
        sentences = re.split(r'(?<=[.!?])\s+', full_speech_text)

        child_buffer = []
        child_word_count = 0

        for sentence in sentences:
            child_buffer.append(sentence)
            child_word_count += len(sentence.split())

            # Once a child chunk reaches ~120 words (approx 150-200 tokens), lock it and save it
            if child_word_count >= 120:
                child_text = " ".join(child_buffer)
                all_final_chunks.append({
                    "id": str(uuid.uuid4()),
                    "parent_id": parent_id,
                    "speaker": current_speaker,
                    "party": current_party,
                    "topic": current_topic,
                    "text": child_text,                 # Embedded & searched text
                    "full_context": full_speech_text    # Handed to the LLM
                })
                child_buffer = []
                child_word_count = 0

        # Save any leftover sentences as the final child chunk
        if child_buffer:
            all_final_chunks.append({
                "id": str(uuid.uuid4()),
                "parent_id": parent_id,
                "speaker": current_speaker,
                "party": current_party,
                "topic": current_topic,
                "text": " ".join(child_buffer),
                "full_context": full_speech_text
            })
        speech_buffer = []

    # Main Loop
    for page_num in range(4, len(doc)):
        for block in doc[page_num].get_text("blocks"):
            text_line = " ".join(block[4].strip().split())
            if not text_line or text_line.isdigit() or "Deutscher Bundestag" in text_line:
                continue

            if topic_pattern.search(text_line):
                start_idx = topic_pattern.search(text_line).start()
                current_topic = text_line[start_idx:start_idx + 120]
                continue

            speaker_match = speaker_pattern.match(text_line)
            if speaker_match:
                flush_current_speech() # Save previous speaker's split chunks

                current_speaker = speaker_match.group(1).strip()
                current_party = speaker_match.group(2).strip() if speaker_match.group(2) else "Regierung"

                remaining = text_line[speaker_match.end():].strip()
                if remaining:
                    speech_buffer.append(remaining)
                continue

            speech_buffer.append(text_line)

    flush_current_speech() # Flush the absolute final speech block
    return all_final_chunks
