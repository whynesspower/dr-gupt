import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ExotelClient:
    def __init__(self, api_key: str = None, api_token: str = None):
        """
        Initialize Exotel client with API credentials
        """
        self.api_key = api_key or os.getenv("EXOTEL_API_KEY")
        self.api_token = api_token or os.getenv("EXOTEL_API_TOKEN")
        self.sid = os.getenv("EXOTEL_SID")
        
        if not self.api_key or not self.api_token or not self.sid:
            raise ValueError("Exotel credentials not set. Please set EXOTEL_API_KEY, EXOTEL_API_TOKEN and EXOTEL_SID in .env file")
        
        self.base_url = f"https://api.exotel.com/v1/Accounts/{self.sid}"
        self.auth = (self.api_key, self.api_token)
    
    def make_call(self, from_number: str, to_number: str, caller_id: str, 
                 call_type: str = "trans", time_limit: int = 14400, 
                 status_callback: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an outbound call
        
        Args:
            from_number: The number to be called first
            to_number: The number to be called next
            caller_id: Your ExoPhone number
            call_type: The type of call (trans, promo)
            time_limit: Maximum call duration in seconds
            status_callback: URL to receive call status updates
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Calls/connect.json"
        
        payload = {
            "From": from_number,
            "To": to_number,
            "CallerId": caller_id,
            "CallType": call_type,
            "TimeLimit": time_limit
        }
        
        if status_callback:
            payload["StatusCallback"] = status_callback
            
        response = requests.post(url, auth=self.auth, data=payload)
        response.raise_for_status()
        
        return response.json()
    
    def send_sms(self, from_number: str, to_number: str, body: str, 
                priority: str = "normal", encoding_type: str = "plain") -> Dict[str, Any]:
        """
        Send SMS
        
        Args:
            from_number: Your ExoPhone number
            to_number: The recipient's number
            body: SMS content
            priority: SMS priority (normal, high)
            encoding_type: Encoding type (plain, unicode)
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Sms/send.json"
        
        payload = {
            "From": from_number,
            "To": to_number,
            "Body": body,
            "Priority": priority,
            "EncodingType": encoding_type
        }
        
        response = requests.post(url, auth=self.auth, data=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_call_details(self, call_sid: str) -> Dict[str, Any]:
        """
        Get details of a specific call
        
        Args:
            call_sid: The SID of the call
            
        Returns:
            Call details as dictionary
        """
        url = f"{self.base_url}/Calls/{call_sid}.json"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        return response.json()
    
    def get_call_recordings(self, call_sid: str) -> Dict[str, Any]:
        """
        Get recordings for a specific call
        
        Args:
            call_sid: The SID of the call
            
        Returns:
            Recording details as dictionary
        """
        url = f"{self.base_url}/Calls/{call_sid}/Recordings.json"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        return response.json()
    
    def create_applet(self, applet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an Exotel Applet for call flow control
        
        Args:
            applet_data: Dictionary containing applet configuration
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Applets.json"
        
        response = requests.post(url, auth=self.auth, data=applet_data)
        response.raise_for_status()
        
        return response.json()
