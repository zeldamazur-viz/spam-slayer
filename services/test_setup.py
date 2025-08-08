import os
import json
from dotenv import load_dotenv
from simple_salesforce import Salesforce
import openai
import webbrowser
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import threading

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
        
        return True
        
    except Exception as e:
        print(f"Salesforce connection failed: {e}")
        return False

def test_user_friendly_oauth():
    """User-friendly OAuth2 flow - opens browser for SSO login"""
    load_dotenv()
    
    # OAuth2 configuration
    client_id = os.getenv('SF_CONSUMER_KEY')
    redirect_uri = 'http://localhost:8080/callback'
    auth_url = f"https://login.salesforce.com/services/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=full"
    
    print("🔗 Starting user-friendly OAuth2 flow...")
    print("1. Opening browser for Salesforce login (use your Microsoft SSO)")
    print("2. After login, you'll be redirected to localhost")
    print("3. The app will automatically capture the token")
    
    # Set up local server to catch the callback
    auth_code = {'code': None}
    
    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if '/callback' in self.path:
                query = urlparse(self.path).query
                params = parse_qs(query)
                auth_code['code'] = params.get('code', [None])[0]
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success!</h1><p>You can close this window and return to your application.</p></body></html>')
        
        def log_message(self, format, *args):
            pass  # Suppress server logs
    
    # Start local server
    server = socketserver.TCPServer(('localhost', 8080), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for callback
        print("Waiting for login completion...")
        import time
        timeout = 120  # 2 minutes
        elapsed = 0
        while auth_code['code'] is None and elapsed < timeout:
            time.sleep(1)
            elapsed += 1
        
        server.shutdown()
        
        if auth_code['code']:
            print("Authorization successful! Got auth code.")
            
            import requests
            token_url = "https://login.salesforce.com/services/oauth2/token"
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': os.getenv('SF_CONSUMER_SECRET'),
                'redirect_uri': redirect_uri,
                'code': auth_code['code']
            }
            
            response = requests.post(token_url, data=token_data)
            if response.status_code == 200:
                token_info = response.json()
                
                # Test connection
                sf = Salesforce(
                    instance_url=token_info['instance_url'],
                    session_id=token_info['access_token']
                )
                
                print("Connected to Salesforce via user OAuth2!")
                result = sf.query("SELECT Id, Subject FROM Case LIMIT 1")
                print(f"Test query successful: {len(result['records'])} records")
                
                # Save tokens for reuse
                print(f"\n📝 Save these for your .env file:")
                print(f"SF_ACCESS_TOKEN={token_info['access_token']}")
                print(f"SF_REFRESH_TOKEN={token_info.get('refresh_token', 'N/A')}")
                print(f"SF_INSTANCE_URL={token_info['instance_url']}")
                
                return True
            else:
                print(f"Token exchange failed: {response.text}")
                return False
        else:
            print("Login timeout or cancelled")
            return False
            
    except Exception as e:
        print(f"OAuth2 flow failed: {e}")
        server.shutdown()
        return False

def test_jwt_connection(): 
    load_dotenv()
    try:
        print("🔗 Attempting JWT/Token connection...")
        sf = Salesforce(
            instance_url='https://orgfarm-98cd1b2366-dev-ed.develop.lightning.force.com',  # e.g. https://yourorg.my.salesforce.com
            session_id=os.getenv('SF_ACCESS_TOKEN')     # Your JWT/access token
        )

        print("Connected to Salesforce via JWT/token!")
        
        # Test with a query
        result = sf.query("SELECT Id, Subject FROM Case LIMIT 1")
        print(f"Test query successful: {len(result['records'])} records")

        return True
    except Exception as e:
        print(f"Salesforce JWT/Token connection failed: {e}")
        return False

def test_jwt_flow():
    """Test JWT Bearer flow - best for SSO environments"""
    load_dotenv()
    try:
        print("🔗 Attempting JWT Bearer flow...")
        sf = Salesforce(
            username=os.getenv('SF_USERNAME'),  # Your Salesforce username (not Microsoft)
            consumer_key=os.getenv('SF_CONSUMER_KEY'),
            privatekey_file=os.getenv('SF_PRIVATE_KEY_FILE')  # Path to private key file
        )

        print("Connected to Salesforce via JWT Bearer flow!")
        
        # Test with a query
        result = sf.query("SELECT Id, Subject FROM Case LIMIT 1")
        print(f"Test query successful: {len(result['records'])} records")
        
        return True
    except Exception as e:
        print(f"JWT Bearer flow failed: {e}")
        return False

def test_oauth_connection(): 
    """Test standard OAuth2 flow - may not work with SSO"""
    load_dotenv()
    try:
        print(f"SF_USERNAME: {os.getenv('SF_USERNAME')}")
        print(f"SF_CONSUMER_KEY: {os.getenv('SF_CONSUMER_KEY')}")
        print(f"SF_CONSUMER_SECRET: {os.getenv('SF_CONSUMER_SECRET')}")

        print("🔗 Attempting OAuth connection...")
        sf = Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            consumer_key=os.getenv('SF_CONSUMER_KEY'),
            consumer_secret=os.getenv('SF_CONSUMER_SECRET'),
            security_token=os.getenv('SF_SECURITY_TOKEN')
        )

        print("Connected to Salesforce via oauth2! ")

        return True
    except Exception as e:
        print(f"Salesforce OAuth2 connection failed: {e}")
        return False

if __name__ == "__main__":
    # Try user-friendly OAuth2 first (best UX for SSO)
    if not test_user_friendly_oauth():
        print("\n" + "="*50)
        print("Falling back to other methods...")
        # Try saved token if OAuth2 fails
        if not test_jwt_connection():
            # Last resort: standard OAuth2
            test_oauth_connection() 