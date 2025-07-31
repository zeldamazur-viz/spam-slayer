import os
import json
from dotenv import load_dotenv
from simple_salesforce import Salesforce
import openai

def test_connection():
    load_dotenv()

    try:
        print("🔗 Attempting Salesforce connection...")
        sf = Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            security_token=os.getenv('SF_SECURITY_TOKEN')
        )
        
        print("Connected to Salesforce!")
        
        # List all objects (tables)
        result = sf.query("SELECT Id, Subject, Description, SuppliedEmail, Status FROM Case WHERE Status = 'New'")
        print(json.dumps(result, indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"Salesforce connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()