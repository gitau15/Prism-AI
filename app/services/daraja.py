import requests
import base64
from datetime import datetime
from app.core.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

class DarajaService:
    """Service for interacting with the Safaricom Daraja API"""
    
    def __init__(self):
        self.consumer_key = settings.DARAJA_CONSUMER_KEY
        self.consumer_secret = settings.DARAJA_CONSUMER_SECRET
        self.shortcode = settings.DARAJA_SHORTCODE
        self.passkey = settings.DARAJA_PASSKEY
        self.callback_url = settings.DARAJA_CALLBACK_URL
        
        # Determine if we're using sandbox or production
        self.is_sandbox = "sandbox" in self.consumer_key.lower() if self.consumer_key else True
        self.base_url = "https://sandbox.safaricom.co.ke" if self.is_sandbox else "https://api.safaricom.co.ke"
    
    def get_access_token(self) -> str:
        """
        Get OAuth access token from Daraja API
        
        Returns:
            str: Access token for authenticating API requests
        """
        try:
            # Encode consumer key and secret
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Prepare headers
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }
            
            # Make request to get access token
            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers
            )
            
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            logger.info("Successfully obtained Daraja access token")
            return access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Daraja access token: {str(e)}")
            raise Exception(f"Failed to get access token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting Daraja access token: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")
    
    def initiate_stk_push(self, phone_number: str, amount: int, account_reference: str, 
                         transaction_desc: str = "Prism AI Pro Subscription") -> dict:
        """
        Initiate STK Push request to user's phone
        
        Args:
            phone_number (str): User's phone number in format 2547XXXXXXXX
            amount (int): Amount to charge
            account_reference (str): Account reference for the transaction
            transaction_desc (str): Description of the transaction
            
        Returns:
            dict: Response from Daraja API with checkout request details
        """
        try:
            # Get access token
            access_token = self.get_access_token()
            
            # Prepare timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Generate password
            password_string = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_string.encode()).decode()
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare payload
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            # Make request to initiate STK push
            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers
            )
            
            response.raise_for_status()
            stk_response = response.json()
            
            logger.info(f"STK Push initiated for phone {phone_number}, CheckoutRequestID: {stk_response.get('CheckoutRequestID')}")
            return stk_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating STK Push: {str(e)}")
            raise Exception(f"Failed to initiate STK Push: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error initiating STK Push: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")