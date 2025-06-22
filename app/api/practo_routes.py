from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from .practo import PractoClient

# Create router
router = APIRouter(
    prefix="/api/practo",
    tags=["practo"],
    responses={404: {"description": "Not found"}},
)

# Models for request/response
class FilterRequest(BaseModel):
    qualification: Optional[str] = None
    min_fee: Optional[int] = None
    max_fee: Optional[int] = None
    min_time: Optional[str] = None
    max_time: Optional[str] = None
    day: Optional[List[str]] = None

# Dependency to get Practo client
def get_practo_client():
    try:
        return PractoClient()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"Practo client not initialized: {str(e)}")

# Doctor Details API routes
@router.get("/doctors")
async def list_doctors(
    page: int = 1,
    client: PractoClient = Depends(get_practo_client)
):
    """List all doctors with pagination"""
    return client.list_doctors(page=page)

@router.get("/doctors/{doctor_id}")
async def get_doctor(
    doctor_id: int,
    with_relations: bool = False,
    client: PractoClient = Depends(get_practo_client)
):
    """Get details of a specific doctor"""
    return client.get_doctor(doctor_id=doctor_id, with_relations=with_relations)

@router.get("/doctors/phone_number")
async def get_doctor_phone_number(
    relation_id: str,
    client: PractoClient = Depends(get_practo_client)
):
    """Get phone number for a practice doctor"""
    return client.get_doctor_phone_number(relation_id=relation_id)

# Practice Details API routes
@router.get("/practices")
async def list_practices(
    page: int = 1,
    client: PractoClient = Depends(get_practo_client)
):
    """List all practices with pagination"""
    return client.list_practices(page=page)

@router.get("/practices/{practice_id}")
async def get_practice(
    practice_id: int,
    with_doctors: bool = False,
    client: PractoClient = Depends(get_practo_client)
):
    """Get details of a specific practice"""
    return client.get_practice(practice_id=practice_id, with_doctors=with_doctors)

# Search API routes
@router.get("/search")
async def search(
    city: str,
    speciality: Optional[str] = None,
    locality: Optional[str] = None,
    searchfor: str = "specialization",
    q: Optional[str] = None,
    offset: int = 0,
    limit: int = 10,
    near: Optional[str] = None,
    sort_by: str = "practo_ranking",
    qualification: Optional[str] = Query(None),
    min_fee: Optional[int] = Query(None),
    max_fee: Optional[int] = Query(None),
    min_time: Optional[str] = Query(None),
    max_time: Optional[str] = Query(None),
    day: Optional[List[str]] = Query(None),
    client: PractoClient = Depends(get_practo_client)
):
    """
    Search for doctors/practices within a city
    
    - **city**: City for scope of search
    - **speciality**: Specialization of doctors to search for
    - **locality**: Get doctors who work in this locality (don't use with near)
    - **searchfor**: Type of search (specialization, doctor, practice)
    - **q**: Search query for doctor/practice name
    - **offset**: Offset of result
    - **limit**: Limit of result (max 50)
    - **near**: Search near coordinates (lat,long format, don't use with locality)
    - **sort_by**: Sort results by (practo_ranking, distance, experience, fees, recommendations)
    - **filters**: Additional filters (qualification, min_fee, max_fee, min_time, max_time, day)
    """
    # Construct filters dictionary from query parameters
    filters = {}
    if qualification:
        filters["qualification"] = qualification
    if min_fee:
        filters["min_fee"] = min_fee
    if max_fee:
        filters["max_fee"] = max_fee
    if min_time:
        filters["min_time"] = min_time
    if max_time:
        filters["max_time"] = max_time
    if day:
        filters["day"] = day
    
    return client.search(
        city=city,
        speciality=speciality,
        locality=locality,
        searchfor=searchfor,
        q=q,
        offset=offset,
        limit=limit,
        near=near,
        sort_by=sort_by,
        filters=filters if filters else None
    )

# Search Meta API routes
@router.get("/meta/cities")
async def list_cities(
    country_id: Optional[int] = None,
    client: PractoClient = Depends(get_practo_client)
):
    """List cities where Practo search service is available"""
    return client.list_cities(country_id=country_id)

@router.get("/meta/cities/{city_id}")
async def get_localities_and_specialties(
    city_id: int,
    client: PractoClient = Depends(get_practo_client)
):
    """Get localities and specialties for a city"""
    return client.get_localities_and_specialties(city_id=city_id)

@router.get("/meta/countries")
async def list_countries(
    client: PractoClient = Depends(get_practo_client)
):
    """List countries where Practo search service is available"""
    return client.list_countries()
