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

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment** (`.env`):
   ```
   SF_USERNAME=your_salesforce_username
   SF_PASSWORD=your_salesforce_password  
   SF_SECURITY_TOKEN=your_security_token
   ```

3. **Train the model**:
   ```bash
   python models/train_spam_model.py
   ```

4. **Run spam detection**:
   ```bash
   python services/spam_filter_service.py
   ```

## Training Data

Expects `models/training_data.xlsx` with columns:
- `SuppliedEmail`, `Subject`, `Description`, `is_spam` (boolean)

## Configuration

- Confidence threshold: 53% (configurable in `spam_filter_service.py`) (could be higher with more training data)
- Processes tickets with status: New, Open
- Auto-closes spam tickets with "Spam" reason