import fitz  # PyMuPDF
import re

def parse_bundestag_pdf_manual_structure_aware(pdf_path):
    doc = fitz.open(pdf_path)

    # Fallback metadata
    current_topic = "Sitzungseröffnung / Formalia"
    current_speaker = "Präsidium / System"
    current_party = "Amt"

    speech_chunks = []
    current_speech_text = []

    # 1. Regex meant for TOPs and ZPs
    topic_pattern = re.compile(r"^(Tagesordnungspunkt\s+\d+|Zusatzpunkt\s+\d+):", re.IGNORECASE)

    # Regex for parsing the speaker
    speaker_pattern = re.compile(
        r"^([A-ZÄÖÜ][a-zßäöü\-\s]+[A-ZÄÖÜ][a-zßäöü]+(?:,\s+Bundesminister\s+[\w\s]+)?)\s*(?:\(([^)]+)\))?:"
    )

    # We start from page 5 because there the real content of the protocol lies
    # TODO: Here we need a dynamic start. After a blank page the real protocol starts
    for page_num in range(4, len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")

        for block in blocks:
            text_line = block[4].strip()

            text_line = " ".join(text_line.split())
            if not text_line or text_line.isdigit():
                continue

            if "Deutscher Bundestag" in text_line and "Wahlperiode" in text_line:
                continue

            # Check for new TOP
            if topic_pattern.match(text_line):
                current_topic = text_line
                continue

            # Check for speaker switch
            speaker_match = speaker_pattern.match(text_line)
            if speaker_match:
                # Save text of prev. speaker
                if current_speech_text:
                    speech_chunks.append({
                        "speaker": current_speaker,
                        "party": current_party,
                        "topic": current_topic,
                        "text": " ".join(current_speech_text)
                    })
                    current_speech_text = []

                current_speaker = speaker_match.group(1).strip()
                current_party = speaker_match.group(2).strip() if speaker_match.group(2) else "Regierung / Amt"

                # handle ":" after text
                remaining_text = text_line[speaker_match.end():].strip()
                if remaining_text:
                    current_speech_text.append(remaining_text)
                continue

            # Text belongs to current speaker
            current_speech_text.append(text_line)

    # Save last speaker to document
    if current_speech_text:
        speech_chunks.append({
            "speaker": current_speaker,
            "party": current_party,
            "topic": current_topic,
            "text": " ".join(current_speech_text)
        })

    return speech_chunks
