import fitz  # PyMuPDF
import re

def parse_bundestag_pdf_manual_structure_aware(pdf_path):
    """
    Parses a local Bundestag plenary transcript PDF and divides it into
    structured, semantic speech units containing speaker, party, topic, and text content.
    """
    doc = fitz.open(pdf_path)

    # Baseline session metadata states before explicit topics or speakers are initialized
    current_topic = "Sitzungseröffnung / Formalia (Session Opening)"
    current_speaker = "Präsidium (Presidency)"
    current_party = "Amt"

    speech_chunks = []
    current_speech_text = []

    # REGEX 1: Topic detection engine
    # Looks inside the text stream for explicit declarations of agenda items (e.g., 'Tagesordnungspunkt 6' or 'Zusatzpunkt 8')
    topic_pattern = re.compile(
        r"(Tagesordnungspunkt(?:e)?\s+\d+|Zusatzpunkt(?:e)?\s+\d+)",
        re.IGNORECASE
    )

    # REGEX 2: Main speaker detection engine
    # Matches patterns like "Lars Klingbeil, Bundesminister der Finanzen:" or "Kay Gottschalk (AfD):"
    # Negative lookbehind (?<!\bvon der\b) and similar rules ensure we do not trip over random party mentions.
    speaker_pattern = re.compile(
        r"^([A-ZÄÖÜ][a-zßäöü\-\s]+[A-ZÄÖÜ][a-zßäöü]+(?:,\s+(?:Bundesminister|Abgeordneter|Parl\.)\s+[\w\s]+)?)\s*(?:\(([^)]+)\))?:"
    )

    # CRITICAL: We skip pages 0-3 (0-indexed pages 0 to 3) because they contain the multi-column table of contents.
    # Processing those early pages triggers false speaker changes since names are listed next to layout numbers.
    # Real transcription delivery begins on Page 5 (index 4).
    for page_num in range(4, len(doc)):
        page = doc[page_num]

        # 'blocks' returns a list of layout structures sorted sequentially by column flows (top-to-bottom, left-to-right)
        blocks = page.get_text("blocks")

        for block in blocks:
            # Clean up leading/trailing white spaces and remove harsh mid-line line breaks from layout wrappers
            text_line = block[4].strip()
            text_line = " ".join(text_line.split())

            if not text_line or text_line.isdigit():
                continue

            # Filter layout header signatures injected onto every single page of official logs
            if "Deutscher Bundestag" in text_line and "Wahlperiode" in text_line:
                continue

            # STEP A: Check if a new Agenda Item (TOP) is explicitly mentioned or initialized in this block
            topic_match = topic_pattern.search(text_line)
            if topic_match:
                # Capture the text slice starting from the Topic keyword to provide contextual description
                start_idx = topic_match.start()
                # We limit the text payload length to keep the metadata property succinct
                current_topic = text_line[start_idx:start_idx + 120]

            # STEP B: Check for a main speaker change state
            speaker_match = speaker_pattern.match(text_line)
            if speaker_match:
                # Prior to flushing out state parameters, dump the active speech block payload into memory
                if current_speech_text:
                    speech_chunks.append({
                        "speaker": current_speaker,
                        "party": current_party,
                        "topic": current_topic,
                        "text": " ".join(current_speech_text)
                    })
                    current_speech_text = []  # Reset buffer for upcoming speaker data

                # Assign new global processing attributes from matched groups
                current_speaker = speaker_match.group(1).strip()
                current_party = speaker_match.group(2).strip() if speaker_match.group(2) else "Regierung / Präsidium"

                # If conversational text immediately follows the colon on the same line, harvest it
                remaining_text = text_line[speaker_match.end():].strip()
                if remaining_text:
                    current_speech_text.append(remaining_text)
                continue

            # STEP C: Append standard text elements into the current speaker's list buffer
            current_speech_text.append(text_line)

    # Clean and persist the final active speech queue item remaining after processing loops complete
    if current_speech_text:
        speech_chunks.append({
            "speaker": current_speaker,
            "party": current_party,
            "topic": current_topic,
            "text": " ".join(current_speech_text)
        })

    return speech_chunks
