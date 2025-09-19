# si_to_sql.py
from googletrans import Translator
import spacy
import sys

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Get Sinhala text and division from command line
usertext = sys.argv[1] if len(sys.argv) > 1 else "NotFound"
divNum = sys.argv[2] if len(sys.argv) > 2 else "Division_Not_Found"

# Translate Sinhala → English
translator = Translator()
translation = translator.translate(usertext, src="si", dest="en")
print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
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
