import re
import string

def clean_text_for_bert(text: str) -> str:
    """
    Cleans raw input text by removing punctuation, converting to lowercase,
    and stripping extra whitespace for NLP processing pipelines.
    """
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_words(text: str) -> list:
    """
    Splits a cleaned string into a list of individual word tokens.
    """
    cleaned_text = clean_text_for_bert(text)
    return cleaned_text.split(' ')

if __name__ == "__main__":
    sample = "This is a   TEST string, for NLP!!"
    print(tokenize_words(sample))