import joblib
import os

import spacy



root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path = os.path.join(root_dir, 'recommend_model','recommendation_pipeline.pkl')


# Tải mô hình ngôn ngữ của spaCy
nlp = spacy.load("en_core_web_sm")

# Hàm tiền xử lý văn bản sử dụng spaCy


from bs4 import BeautifulSoup

def clean_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ")

def preprocess_text(text):
    text = clean_html(text)
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

# Hàm tải mô hình đã lưu
def load_pipeline():
    try:
        pipeline = joblib.load(model_path)
        return pipeline
    except FileNotFoundError as e:
        print(e)
        return None