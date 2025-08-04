import os
import pandas as pd
import json
from dotenv import load_dotenv
from simple_salesforce import Salesforce

class SalesforceDataLoader:
    """
    Class for loading and processing Salesforce data for spam training
    """
    
    def __init__(self):
        load_dotenv()
    
    def _load_raw_data(self):
        """
        Load raw case data from Salesforce
        """
        try:
            sf = Salesforce(
                username=os.getenv('SF_USERNAME'),
                password=os.getenv('SF_PASSWORD'),
                security_token=os.getenv('SF_SECURITY_TOKEN')
            )
            print("Salesforce connection established successfully")

            query = "SELECT Id, Subject, Description, CreatedDate, Status FROM Case ORDER BY CreatedDate DESC LIMIT 1000"
            cases = sf.query_all(query)
            
            return cases['records']
            
        except Exception as e:
            print(f"Error loading Salesforce data: {e}")
            return None
    
    def _create_dataframe(self, raw_data):
        """
        Process raw Salesforce data into training dataframe
        """
        if raw_data is None:
            return None
            
        df = pd.DataFrame(raw_data)
        
        df['is_spam'] = ~df['Subject'].str.startswith('Pardot', case=False, na=False)
        df = df[['Subject', 'Description', 'is_spam']]
        
        return df
    
    def get_training_data(self):
        """
        Load and process Salesforce data for spam model training
        """
        raw_data = self._load_raw_data()
        return self._create_dataframe(raw_data)
    
    def save_to_csv(self, df, filename='training_data.csv'):
        """
        Save dataframe to CSV in training-data folder
        """
        if df is None:
            print("No data to save")
            return False

        training_data_dir = os.path.join(os.path.dirname(__file__), '..', 'training-data')
        os.makedirs(training_data_dir, exist_ok=True)
        
        filepath = os.path.join(training_data_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Training data saved to: {filepath}")
        return True

if __name__ == "__main__":
    print("Starting Salesforce data extraction...")
    
    loader = SalesforceDataLoader()
    df = loader.get_training_data()
    
    if df is not None:
        loader.save_to_csv(df)
        print(f"Pipeline complete. Extracted {len(df)} records.")
    else:
        print("Pipeline failed - no data extracted.")