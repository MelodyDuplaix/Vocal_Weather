from transformers import CamembertTokenizer, AutoModelForTokenClassification, pipeline
import dateparser
from transformers.pipelines.base import Pipeline
from datetime import datetime, timedelta

def load_model():
    """
    Load the Camembert model fine-tuned for Named Entity Recognition (NER) with dates and localisations.

    Returns:
        tuple: A tuple containing the tokenizer and the model.
    """
    tokenizer = CamembertTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    ner_pipeline: Pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    return ner_pipeline

def extract_entities(text, ner_pipeline):
    """
    Extract entities from a given text using a Camembert model fine-tuned for Named Entity Recognition (NER) with dates and localisations.

    Args:
        text (string): The text from which to extract entities.

    Returns:
        dict: A dictionary containing the extracted dates and localisations.
    """
    
    try:
        # Extract entities
        entities = ner_pipeline(text)
        
        # Extract dates and localisations from entities
        dates = []
        localisations = []

        for entite in entities:
            if entite["entity_group"] == "DATE":
                date_obj = dateparser.parse(entite["word"], languages=["fr"], settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()})
                if date_obj is not None:
                    dates.append(date_obj)
            elif entite["entity_group"] == "LOC":
                localisations.append(entite["word"])
                
        return {
            "date": dates,
            "localisation": localisations
        }                 
    except ValueError as e:
        return {
            "date": [],
            "localisation": []
        }

if __name__ == "__main__":
    text = input("Entrez le texte à analyser: ")
    ner_pipeline = load_model()
    entities = extract_entities(text, ner_pipeline)
    dates = [date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date, datetime) else date for date in entities['date']]
    print(f"Dates: {dates}")
    print(f"Localisations: {entities['localisation']}")
    print(extract_entities(12345, ner_pipeline))
