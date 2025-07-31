#!/usr/bin/env python3
"""
AI Spam Filter Service for Salesforce Cases
Hackathon Demo Version
"""
import os
import time
import json
import pickle
from datetime import datetime
from dotenv import load_dotenv
from simple_salesforce import Salesforce

class SpamFilterService:
    def __init__(self):
        print("Initializing AI Spam Filter...")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize stats tracking
        self.stats = {
            'total_processed': 0,
            'spam_closed': 0,
            'legitimate_kept': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Connect to Salesforce
        if not self.initialize_salesforce_connection():
            print("Failed to initialize Salesforce connection!")
            return
        
        # Load ML model
        if not self.load_spam_model():
            print("Failed to load spam classification model!")
            return
        
        print("Service initialized")

    def initialize_salesforce_connection(self):
        try:
            print("Connecting to Salesforce...")
            self.sf = Salesforce(
                username=os.getenv('SF_USERNAME'),
                password=os.getenv('SF_PASSWORD'),
                security_token=os.getenv('SF_SECURITY_TOKEN')
            )
            
            print("Connected to Salesforce!")
            return True
            
        except Exception as e:
            print(f"Salesforce connection failed: {e}")
            return False

    def load_spam_model(self):
        """Load the trained spam classification model"""
        try:
            print("Loading spam classification model...")
            
            with open('./models/spam_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            
            with open('./models/tfidf_vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            print("Spam model loaded successfully!")
            return True
            
        except FileNotFoundError:
            print("Model files not found! Run train_spam_model.py first.")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def classify_ticket_as_spam(self, subject, description):
        """Classify ticket using local ML model"""
        try:
            text = f"{subject} {description or ''}"
            
            text_tfidf = self.vectorizer.transform([text])
            
            prediction = self.model.predict(text_tfidf)[0]
            probabilities = self.model.predict_proba(text_tfidf)[0]
            
            spam_prob = probabilities[1] if self.model.classes_[1] == 'spam' else probabilities[0]
            
            is_spam = prediction == 'spam'
            confidence = spam_prob if is_spam else (1 - spam_prob)
            
            reason = f"ML model prediction: {prediction} ({confidence:.1%} confidence)"
            
            return is_spam, confidence, reason
            
        except Exception as e:
            print(f"Error in classification: {e}")
            return False, 0.0, "Classification error"

    def get_new_tickets(self):
        """Get all new/open tickets from Salesforce"""
        try:
            print("Checking for new tickets...")
            result = self.sf.query("SELECT Id, Subject, Description, Status, SuppliedEmail FROM Case WHERE Status IN ('New', 'Open')")
            
            tickets = result['records']
            print(f"Found {len(tickets)} tickets to process\n")
            
            return tickets
            
        except Exception as e:
            print(f"Error getting tickets: {e}")
            return []

    def close_spam_ticket(self, ticket_id, reason):
        """Close a ticket as spam with audit trail"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.sf.Case.update(ticket_id, {
                'Status': 'Closed',
                'Reason': 'Spam',
                'Comments': f"Auto-closed by AI spam filter at {timestamp}. Reason: {reason}"
            })
            
            print(f"Closed ticket {ticket_id} as spam\n")
            return True
            
        except Exception as e:
            print(f"Error closing ticket {ticket_id}: {e}")
            return False

    def check_tickets_periodically(self):
        """Main loop - classify tickets and optionally close spam"""
        print("\nStarting periodic ticket checking...")
        print("Press Ctrl+C to stop")
        
        try:
            # for i in range(60):
            print(f"\n=== Checking at {datetime.now().strftime('%H:%M:%S')} ===")
            tickets = self.get_new_tickets()
            
            if not tickets:
                print("No tickets to process")
            else:
                for ticket in tickets:
                    subject = ticket.get('Subject', 'No Subject')
                    description = ticket.get('Description', '')
                    
                    is_spam, confidence, reason = self.classify_ticket_as_spam(subject, description)
                    
                    if is_spam and confidence > 0.53:
                        print("=== SPAM DETECTED ===")
                        print(f"  Subject: {subject}")
                        print(f"  Confidence: {confidence:.1%}\n")
                        
                        if self.close_spam_ticket(ticket['Id'], reason):
                            self.stats['spam_closed'] += 1
                        else:
                            print(f"  Failed to close ticket")
                    else:
                        self.stats['legitimate_kept'] += 1
                    
                    self.stats['total_processed'] += 1
            
            # Print stats
            if self.stats['total_processed'] > 0:
                spam_rate = self.stats['spam_closed'] / self.stats['total_processed'] * 100
                print(f"Stats: {self.stats['total_processed']} processed, {self.stats['spam_closed']} closed, {spam_rate:.1f}% spam rate")
                
                # print("Waiting 30 seconds...")
                # time.sleep(30)
                
        except KeyboardInterrupt:
            print("\nStopped checking tickets")
            print(f"\nFinal Stats:")
            print(f"Total processed: {self.stats['total_processed']}")
            print(f"Spam closed: {self.stats['spam_closed']}")
            print(f"Legitimate kept: {self.stats['legitimate_kept']}")

if __name__ == "__main__":
    service = SpamFilterService()
    print("Service ready to run!")
    service.check_tickets_periodically()
