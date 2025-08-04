#!/usr/bin/env python3
"""
Train a local spam classification model using TF-IDF + Logistic Regression
For hackathon demo
"""
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import os
def load_training_data(csv_path=None):
    """Load training data from CSV file"""
    if csv_path is None:
        # Default path to training-data folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'training-data', 'training_data.csv')
    
    try:
        print(f"Loading training data from {csv_path}...")
        df = pd.read_csv(csv_path)

        required_cols = ['Subject', 'Description', 'is_spam']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV must have columns: {required_cols}. Missing: {missing_cols}")

        df = preprocess_data(df)
        
        return df
        
    except FileNotFoundError:
        print(f"Training data file {csv_path} not found.")
        print("Run 'python models/get_training_data_from_salesforce.py' first to generate the CSV.")
        raise FileNotFoundError(f"Training data file {csv_path} not found")

def preprocess_data(df):
    """Combine text fields and convert labels"""
    print("Preprocessing data...")

    df['text'] = df['Subject'].fillna('') + ' ' + df['Description'].fillna('')
    df['label'] = df['is_spam'].map({True: 'spam', False: 'legitimate'})
    df['text'] = df['text'].str.strip()
    
    print(f"Combined text from subject + description")
    print(f"Converted {df['is_spam'].sum()} True values to 'spam'")
    print(f"Converted {(~df['is_spam']).sum()} False values to 'legitimate'")
    
    return df

def train_model():
    """Train the spam classification model"""
    print("Loading training data...")
    df = load_training_data()
    
    print(f"Training data: {len(df)} samples")
    print(f"Spam: {len(df[df['label'] == 'spam'])}")
    print(f"Legitimate: {len(df[df['label'] == 'legitimate'])}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['label'], test_size=0.2, random_state=42
    )
    
    print("\nTraining TF-IDF vectorizer...")
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        lowercase=True,
        ngram_range=(1, 3)  # Use unigrams, bigrams, and trigrams
    )
    
    # Fit vectorizer on training data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print("Training logistic regression model...")
    model = LogisticRegression(random_state=42)
    model.fit(X_train_tfidf, y_train)
    
    # Test the model
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel accuracy: {accuracy:.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))

    print("\nSaving model...")
    with open('./models/spam_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('./models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("Model saved as spam_model.pkl")
    print("Vectorizer saved as tfidf_vectorizer.pkl")

if __name__ == "__main__":
    train_model() 