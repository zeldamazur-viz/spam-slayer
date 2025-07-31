import pandas as pd
import random
import os

def load_email_bodies(file_path):
    """Load email bodies from text file separated by '---'"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split by '---' and clean up empty entries
    raw_bodies = [body.strip() for body in content.split('---') if body.strip()]
    
    # Remove lines starting with "Subject" from each email body
    email_bodies = []
    for body in raw_bodies:
        lines = body.split('\n')
        filtered_lines = [line for line in lines if not line.strip().startswith('Subject')]
        filtered_body = '\n'.join(filtered_lines).strip()
        if filtered_body:  # Only add non-empty bodies
            email_bodies.append(filtered_body)
    
    return email_bodies

def replace_spam_descriptions(excel_file, text_file):
    """Replace descriptions of spam emails with random bodies from text file"""
    
    # Load the Excel file
    df = pd.read_excel(excel_file)
    
    # Load email bodies from text file
    email_bodies = load_email_bodies(text_file)
    
    # Find rows where is_spam is True
    spam_rows = df[df['is_spam'] == True]
    
    print(f"Found {len(spam_rows)} spam rows out of {len(df)} total rows")
    print(f"Loaded {len(email_bodies)} email bodies from text file")
    
    # Replace description for each spam row with a random email body
    for index in spam_rows.index:
        random_email = random.choice(email_bodies)
        df.at[index, 'Description'] = random_email
    
    # Save back to Excel
    df.to_excel(excel_file, index=False)
    print(f"Updated descriptions for {len(spam_rows)} spam rows")
    print(f"Saved updated data back to {excel_file}")

def main():
    # File paths (assuming script is run from models directory)
    excel_file = './models/training_data.xlsx'
    text_file = './models/b2b_healthcare_emails.txt'
    
    # Check if files exist
    if not os.path.exists(excel_file):
        print(f"Error: {excel_file} not found")
        return
    
    if not os.path.exists(text_file):
        print(f"Error: {text_file} not found")
        return
    
    # Replace spam descriptions
    replace_spam_descriptions(excel_file, text_file)

if __name__ == "__main__":
    main()
