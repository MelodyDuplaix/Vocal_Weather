from transformers import CamembertTokenizer, AutoModelForTokenClassification, pipeline
import dateparser
from transformers.pipelines.base import Pipeline

def extract_entities(text):
    """
    Extract entities from a given text using a Camembert model fine-tuned for Named Entity Recognition (NER) with dates and localisations.

    Args:
        text (string): The text from which to extract entities.

    Returns:
        dict: A dictionary containing the extracted dates and localisations.
    """
    # Load the model and tokenizer and create the pipeline
    tokenizer = CamembertTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    nlp: Pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    
    # Extract entities
    entities = nlp(text)
    
    # Extract dates and localisations from entities
    dates = []
    localisations = []

    for entite in entities:
        if entite["entity_group"] == "DATE":
            date_obj = dateparser.parse(entite["word"], languages=["fr"])
            dates.append(date_obj)
        elif entite["entity_group"] == "LOC":
            localisations.append(entite["word"])
            
    return {
        "date": dates,
        "localisation": localisations
    }

if __name__ == "__main__":
    text = input("Entrez le texte à analyser: ")
    entities = extract_entities(text)
    print(f"Dates: {entities['date']}")
    print(f"Localisations: {entities['localisation']}")