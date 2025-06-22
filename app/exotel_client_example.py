"""
Exotel API Client Example

This script demonstrates how to use the Exotel API client to make calls and send SMS.
"""

import os
from dotenv import load_dotenv
from exotel import ExotelClient

# Load environment variables
load_dotenv()

def main():
    # Initialize Exotel client
    try:
        client = ExotelClient()
        print("Exotel client initialized successfully")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set EXOTEL_SID, EXOTEL_API_KEY, and EXOTEL_API_TOKEN in .env file")
        return
    
    # Example: Make a call
    try:
        # Replace with actual phone numbers
        from_number = "9XXXXXXXXX"  # Customer's number
        to_number = "9XXXXXXXXX"    # Agent's number
        caller_id = "9XXXXXXXXX"    # Your Exotel number
        
        print("Making a call...")
        response = client.make_call(
            from_number=from_number,
            to_number=to_number,
            caller_id=caller_id
        )
        print(f"Call initiated: {response}")
        
        # Get the Call SID from the response
        call_sid = response.get("Call", {}).get("Sid")
        if call_sid:
            print(f"Call SID: {call_sid}")
            
            # Get call details
            print("\nGetting call details...")
            call_details = client.get_call_details(call_sid)
            print(f"Call details: {call_details}")
        
    except Exception as e:
        print(f"Error making call: {e}")
    
    # Example: Send SMS
    try:
        # Replace with actual phone numbers
        from_number = "9XXXXXXXXX"  # Your Exotel number
        to_number = "9XXXXXXXXX"    # Recipient's number
        body = "Hello from Dr. Gupt! This is a test message sent via Exotel API."
        
        print("\nSending SMS...")
        response = client.send_sms(
            from_number=from_number,
            to_number=to_number,
            body=body
        )
        print(f"SMS sent: {response}")
        
    except Exception as e:
        print(f"Error sending SMS: {e}")

if __name__ == "__main__":
    main()
