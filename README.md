# Spam Slayer
### Hackathon Entry for *The Electric Cats*
- Lexi Johnkoski
- Zelda Mazur
- Norman Henson

AI-powered spam detection for Salesforce tickets. Automatically identifies and closes spam tickets using machine learning.

Built for Hackapalooza 2025

## Features

- **Real-time Detection**: Monitors Salesforce tickets and classifies spam using TF-IDF + Logistic Regression
- **Auto-Close**: Closes spam tickets with audit trail and configurable confidence threshold
- **Stats Tracking**: Reports processing stats and spam rates
- **Training Pipeline**: Train custom models on your ticket data

## Quick Start

You'll first need to download this repository. Go [here to the main folder](https://github.com/zeldamazur-viz/spam-slayer), click the green "Code" button, and "Download Zip". Extract the folder and navigate to the source folder in a terminal (the source folder should have the Models and Services folders). Make sure you have installed Python on your machine, which you should be able to find in the Company Portal.

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   Create a file named `.env` based on the `.env.example` file. In `.env` replace these values with your real values. **These values are not shared or uploaded anywhere**. 

   ```
   SF_USERNAME=your_salesforce_username
   SF_PASSWORD=your_salesforce_password  
   SF_SECURITY_TOKEN=your_security_token
   ```

   To get a salesforce security token if you don't have one, [see this page on the Salesforce Help Page.](https://help.salesforce.com/s/articleView?id=xcloud.user_security_token.htm&type=5)

3. **Train the model**:
   This only needs to be done once, technically. Run the file below:

   ```bash
   python ./models/create_training_csv.py
   ```

   It will create a CSV under the `./training-data` folder. Send us that CSV and we'll train the model!

4. **Run spam detection**:
   ```bash
   python ./services/spam_filter_service.py
   ```
