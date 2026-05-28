import re
import uuid
from mongo import MongoController


def split_speech_into_children(full_speech_text, max_words=120):
    """
    Splits a single long continuous speech text into smaller child chunks
    (~120 words each) using sentence boundaries.
    """
    # Split text along sentence boundaries (. ! ?)
    sentences = re.split(r'(?<=[.!?])\s+', full_speech_text)

    child_chunks = []
    current_buffer = []
    current_word_count = 0
    parent_id = str(uuid.uuid4())  # Shared lineage token for the whole speech

    for sentence in sentences:
        if not sentence.strip():
            continue
        current_buffer.append(sentence)
        current_word_count += len(sentence.split())

        # When chunk target size is crossed, close out this child element
        if current_word_count >= max_words:
            child_chunks.append({
                "parent_id": parent_id,
                "text": " ".join(current_buffer)
            })
            current_buffer = []
            current_word_count = 0

    # Sweep up remaining sentence fragments
    if current_buffer:
        child_chunks.append({
            "parent_id": parent_id,
            "text": " ".join(current_buffer)
        })

    return child_chunks


def get_all_chunks_to_import():
    """
    Connects to MongoDB, processes all pending protocols, and returns
    a single flat list of all hierarchical child chunks ready for embedding ingestion.
    """
    db = MongoController()
    all_import_chunks = []

    # 1. Patterns for parsing speeches from the text field
    speaker_pattern = re.compile(
        r"^([A-ZÄÖÜ][a-zßäöü\-\s]+[A-ZÄÖÜ][a-zßäöü]+(?:,\s+(?:Bundesminister|Abgeordneter|Parl\.)\s+[\w\s]+)?)\s*(?:\(([^)]+)\))?:"
    )
    topic_pattern = re.compile(r"(Tagesordnungspunkt(?:e)?\s+\d+|Zusatzpunkt(?:e)?\s+\d+)", re.IGNORECASE)

    try:
        pending_docs = db.get_pending_protocols()
        if len(pending_docs) == 0:
            return []

        for doc in pending_docs:
            meta = doc.get("meta_data", {})
            wahlperiode = meta.get("wahlperiode")
            scraped_at = doc.get("pipeline_status", {}).get("scraped_at", "2026-01-01T00:00:00Z")
            protocol_id = doc.get("protocol_id")
            raw_text = doc.get("text", "")

            # --- METADATA HARVESTING & FLATTENING ---
            sachgebiete_set = set()
            vorgangs_titel_set = set()
            initiativen_set = set()

            for vorgang in meta.get("vorgangsbezug", []):
                if not isinstance(vorgang, dict):
                    continue

                sachgebiete = vorgang.get("sachgebiet", [])
                if isinstance(sachgebiete, list):
                    sachgebiete_set.update(sachgebiete)
                elif sachgebiete:
                    for sachgebiet in sachgebiete:
                        sachgebiete_set.add(sachgebiet)

                initiativen = vorgang.get("initialtive", [])  # matching schema typo "initialtive"
                if isinstance(initiativen, list):
                    initiativen_set.update(initiativen)
                elif initiativen:
                    for initiative in initiativen:
                        initiativen_set.add(initiative)

                if vorgang.get("titel"):
                    vorgangs_titel_set.add(vorgang.get("titel"))

            flattened_sachgebiete = list(sachgebiete_set)
            flattened_initiativen = list(initiativen_set)
            flattened_vorgangs_titel = list(vorgangs_titel_set)

            # --- SPEECH EXTRACTION & PARSING LOGIC ---
            # Splits the raw text dump into structural speeches by speakers
            parsed_speeches = []
            current_topic = "Sitzungseröffnung"
            current_speaker = "Präsidium"
            current_party = "Amt"
            speech_buffer = []

            # Splitting text block by layout lines to reconstruct speaker turns
            lines = raw_text.split('\n')
            for line in lines:
                clean_line = " ".join(line.strip().split())
                if not clean_line or clean_line.isdigit() or "Deutscher Bundestag" in clean_line:
                    continue

                # Check for Agenda topic shifts
                topic_match = topic_pattern.search(clean_line)
                if topic_match:
                    start_idx = topic_match.start()
                    current_topic = clean_line[start_idx:start_idx + 120]
                    continue

                # Check for new Speaker turn
                speaker_match = speaker_pattern.match(clean_line)
                if speaker_match:
                    if speech_buffer:
                        parsed_speeches.append({
                            "speaker": current_speaker,
                            "party": current_party,
                            "topic": current_topic,
                            "full_text": " ".join(speech_buffer)
                        })
                        speech_buffer = []

                    current_speaker = speaker_match.group(1).strip()
                    current_party = speaker_match.group(2).strip() if speaker_match.group(2) else "Regierung"

                    remaining = clean_line[speaker_match.end():].strip()
                    if remaining:
                        speech_buffer.append(remaining)
                    continue

                speech_buffer.append(clean_line)
            if speech_buffer:
                parsed_speeches.append({
                    "speaker": current_speaker,
                    "party": current_party,
                    "topic": current_topic,
                    "full_text": " ".join(speech_buffer)
                })
            for speech in parsed_speeches:
                full_context = speech["full_text"]
                children = split_speech_into_children(full_context)

                for child in children:
                    chunk_payload = {
                        "text": child["text"],  # Small string targeting Dense/Sparse vectors
                        "full_context": full_context,  # Full string context provided to your LLM
                        "parent_id": child["parent_id"],
                        "speaker": speech["speaker"],
                        "party": speech["party"],
                        "topic": speech["topic"],

                        "protocol_id": protocol_id,
                        "mongo_id": str(doc["_id"]),

                        # Flat MongoDB Metadata items targeting your Qdrant exact/fulltext lookup indexes
                        "wahlperiode": wahlperiode,
                        "date": scraped_at,  # Must follow valid ISO timestamp string rules
                        "sachgebiete": flattened_sachgebiete,
                        "initiativen": flattened_initiativen,
                        "vorgangs_titel": flattened_vorgangs_titel
                    }
                    all_import_chunks.append(chunk_payload)


    finally:
        db.close()

    return all_import_chunks