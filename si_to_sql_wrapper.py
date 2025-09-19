# si_to_sql_wrapper.py
import sys
import json
import os

# Set UTF-8 encoding for Windows console
if os.name == 'nt':  # Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from googletrans import Translator
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Read input from temp file
if len(sys.argv) < 2:
    print("Error: No input file provided")
    sys.exit(1)

try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    usertext = data.get('sinhala', 'NotFound')
    divNum = data.get('division', 'Division_Not_Found')
    
    # Translate Sinhala → English
    translator = Translator()
    translation = translator.translate(usertext, src="si", dest="en")
    
    # Use ASCII representation for problematic Unicode characters
    try:
        origin_safe = translation.origin.encode('ascii', 'replace').decode('ascii')
        text_safe = translation.text.encode('ascii', 'replace').decode('ascii')
        print(f"{origin_safe} ({translation.src}) --> {text_safe} ({translation.dest})")
    except:
        print(f"Translation completed: {translation.text}")
    
    query_text = translation.text

    def parse_natural_language_to_sql(query_text, div_num):
        doc = nlp(query_text)
        entities = [ent.text for ent in doc.ents]
        keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ"]]
        print("Entities:", entities)
        print("Keywords:", keywords)
        tbName = f"{div_num}_persons"
        sql = f"SELECT * FROM {tbName}"
        if "number" in keywords or "count" in keywords:
            if "disabled" in keywords or "handicapped" in keywords:
                sql = f"SELECT COUNT(*) FROM {tbName} WHERE disability = 1"
            else:
                sql = f"SELECT COUNT(*) FROM {tbName}"
        elif "disabled" in keywords:
            sql = f"SELECT * FROM {tbName} WHERE disability = 1"
        elif "elderly" in keywords or "old" in keywords:
            sql = f"SELECT * FROM {tbName} WHERE age >= 60"
        elif "children" in keywords or "child" in keywords:
            sql = f"SELECT * FROM {tbName} WHERE age < 18"
        return sql

    sql_query = parse_natural_language_to_sql(query_text, divNum)
    print("Generated SQL Query:", sql_query)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)