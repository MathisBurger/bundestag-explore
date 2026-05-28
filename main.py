from chunking import parse_bundestag_pdf_manual_structure_aware

if __name__ == '__main__':
    pdf_pfad = "/Users/mburger/Downloads/21080.pdf"
    daten = parse_bundestag_pdf_manual_structure_aware(pdf_pfad)

    print(f"Erfolgreich {len(daten)} Redebeiträge extrahiert.\n")
    for i, chunk in enumerate(daten):
        print(f"--- BEITRAG {i + 1} ---")
        print(f"Sprecher: {chunk['speaker']} ({chunk['party']})")
        print(f"Thema:    {chunk['topic']}")
        print(f"Text (Auszug): {chunk['text'][:200]}...")
        print("\n")