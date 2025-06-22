import os
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

class PractoClient:
    """Client for interacting with the Practo Search and Listings API"""
    
    BASE_URL = "https://api.practo.com"
    
    def __init__(self):
        self.client_id = os.getenv("PRACTO_CLIENT_ID")
        self.api_key = os.getenv("PRACTO_API_KEY")
        
        if not self.client_id or not self.api_key:
            raise ValueError("PRACTO_CLIENT_ID and PRACTO_API_KEY environment variables must be set")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers required for Practo API requests"""
        return {
            "X-CLIENT-ID": self.client_id,
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Practo API"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 429:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded for Practo API")
                status_code = e.response.status_code
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
            else:
                status_code = 500
                error_detail = str(e)
            
            raise HTTPException(status_code=status_code, detail=f"Practo API error: {error_detail}")
    
    # Doctor Details API
    def list_doctors(self, page: int = 1) -> Dict[str, Any]:
        """List all doctors with pagination"""
        return self._make_request("/doctors", params={"page": page})
    
    def get_doctor(self, doctor_id: int, with_relations: bool = False) -> Dict[str, Any]:
        """Get details of a specific doctor"""
        params = {"with_relations": "true" if with_relations else "false"}
        return self._make_request(f"/doctors/{doctor_id}", params=params)
    
    def get_doctor_phone_number(self, relation_id: str) -> Dict[str, Any]:
        """Get phone number for a practice doctor"""
        return self._make_request(f"/doctors/phone_number", params={"relation_id": relation_id})
    
    # Practice Details API
    def list_practices(self, page: int = 1) -> Dict[str, Any]:
        """List all practices with pagination"""
        return self._make_request("/practices", params={"page": page})
    
    def get_practice(self, practice_id: int, with_doctors: bool = False) -> Dict[str, Any]:
        """Get details of a specific practice"""
        params = {"with_doctors": "true" if with_doctors else "false"}
        return self._make_request(f"/practices/{practice_id}", params=params)
    
    # Search API
    def search(self, 
               city: str, 
               speciality: Optional[str] = None,
               locality: Optional[str] = None,
               searchfor: str = "specialization",
               q: Optional[str] = None,
               offset: int = 0,
               limit: int = 10,
               near: Optional[str] = None,
               sort_by: str = "practo_ranking",
               filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for doctors/practices within a city
        
        Args:
            city: City for scope of search
            speciality: Specialization of doctors to search for
            locality: Get doctors who work in this locality (don't use with near)
            searchfor: Type of search (specialization, doctor, practice)
            q: Search query for doctor/practice name
            offset: Offset of result
            limit: Limit of result (max 50)
            near: Search near coordinates (lat,long format, don't use with locality)
            sort_by: Sort results by (practo_ranking, distance, experience, fees, recommendations)
            filters: Additional filters (qualification, min_fee, max_fee, min_time, max_time, day)
        """
        params = {
            "city": city,
            "searchfor": searchfor,
            "offset": offset,
            "limit": limit,
            "sort_by": sort_by
        }
        
        # Add optional parameters if provided
        if speciality:
            params["speciality"] = speciality
        if locality:
            params["locality"] = locality
        if q:
            params["q"] = q
        if near:
            params["near"] = near
        
        # Add filters if provided
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        params[f"filters[{key}][{i}]"] = item
                else:
                    params[f"filters[{key}]"] = value
        
        return self._make_request("/search", params=params)
    
    # Search Meta API
    def list_cities(self, country_id: Optional[int] = None) -> Dict[str, Any]:
        """List cities where Practo search service is available"""
        params = {}
        if country_id:
            params["country_id"] = country_id
        return self._make_request("/meta/cities", params=params)
    
    def get_localities_and_specialties(self, city_id: int) -> Dict[str, Any]:
        """Get localities and specialties for a city"""
        return self._make_request(f"/meta/cities/{city_id}")
    
    def list_countries(self) -> Dict[str, Any]:
        """List countries where Practo search service is available"""
        return self._make_request("/meta/countries")
