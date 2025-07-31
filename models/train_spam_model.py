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
script_dir = os.path.dirname(os.path.abspath(__file__))
xlsx_path = os.path.join(script_dir, 'training_data.xlsx')

def load_training_data(xlsx_path='./models/training_data.xlsx'):
    """Load training data from XLSX file"""
    try:
        print(f"Loading training data from {xlsx_path}...")
        df = pd.read_excel(xlsx_path)
        
        # Ensure required columns exist
        required_cols = ['SuppliedEmail', 'Subject', 'Description', 'is_spam']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"XLSX must have columns: {required_cols}. Missing: {missing_cols}")
        
        # Preprocess the data
        df = preprocess_data(df)
        
        return df
        
    except FileNotFoundError:
        print(f"Training data file {xlsx_path} not found. Creating sample file...")
        raise FileNotFoundError(f"Training data file {xlsx_path} not found")

def preprocess_data(df):
    """Combine text fields and convert labels"""
    print("Preprocessing data...")
    
    # Combine sender, subject, and body into single text field
    df['text'] = df['Subject'].fillna('') + ' ' + df['Description'].fillna('')
    
    # Convert boolean to string labels
    df['label'] = df['is_spam'].map({True: 'spam', False: 'legitimate'})
    
    # Clean up text (remove extra whitespace)
    df['text'] = df['text'].str.strip()
    
    print(f"Combined text from sender + subject + body")
    print(f"Converted {df['is_spam'].sum()} True values to 'spam'")
    print(f"Converted {(~df['is_spam']).sum()} False values to 'legitimate'")
    
    return df

def train_model():
    """Train the spam classification model"""
    print("Loading training data...")
    df = load_training_data('./models/training_data.xlsx')
    
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
        ngram_range=(1, 2)  # Use unigrams and bigrams
    )
    
    # Fit vectorizer on training data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print("Training logistic regression model...")
    # Train logistic regression
    model = LogisticRegression(random_state=42)
    model.fit(X_train_tfidf, y_train)
    
    # Test the model
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel accuracy: {accuracy:.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model and vectorizer
    print("\nSaving model...")
    with open('./models/spam_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('./models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("Model saved as spam_model.pkl")
    print("Vectorizer saved as tfidf_vectorizer.pkl")

if __name__ == "__main__":
    train_model() 