# /get_stalls: Endpoint to retrieve all stalls
# /create_stall: Endpoint to create a new stall
# /delete_stall: Endpoint to delete a stall

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from utils.database import get_db_connection
from tabulate import tabulate
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/get_stalls")
def get_stalls( conn = Depends(get_db_connection) ):
    """
    returns all stalls
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stalls;")
        stalls = cursor.fetchall()
        cursor.close()
        return stalls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stalls: {e}")
    
@router.get("/get_stalls/table", response_class=PlainTextResponse)
def get_stalls_table(conn = Depends(get_db_connection)):
    """
    Returns a table of all stalls.
    Best viewed in a browser or terminal.
    """
    try:
        stalls = get_stalls(conn)
    
        # Check if empty to avoid errors
        if not stalls:
            return "No stalls found."

        # Convert the list of dictionaries into the table format
        table_content = tabulate(stalls, headers="keys", tablefmt="psql")
        
        return table_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stalls: {e}")

class CreateStallRequest(BaseModel):
    title: str
    location_name: str
    address: str | None = None
    lat: float | None = None
    long: float | None = None
    contact_info: str | None = None
    facilities: str | None = None
    specifications: str | None = None
    owner_id: int
@router.post("/create_stall")
def create_stall( request: Annotated[CreateStallRequest, Query()], conn = Depends(get_db_connection) ):
    """
    creates a new stall by location_name and facilities
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO stalls (title, location_name, address, lat, long, contact_info, facilities, specifications, owner_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING stall_id;
            """,
            (request.title, request.location_name, request.address, request.lat, request.long, request.contact_info, request.facilities, request.specifications, request.owner_id)
        )
        new_stall_id = cursor.fetchone()['stall_id']
        conn.commit()
        return {
            "status": "success",
            "message": "Stall created successfully!",
            "stall_id": new_stall_id,
            "title": request.title,
            "location_name": request.location_name,
            "address": request.address,
            "lat": request.lat,
            "long": request.long,
            "contact_info": request.contact_info,
            "facilities": request.facilities,
            "specifications": request.specifications,
            "owner_id": request.owner_id
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

class DeleteStallRequest(BaseModel):
    stall_id: int
@router.delete("/delete_stall")
def delete_stall( request: Annotated[DeleteStallRequest, Query()], conn = Depends(get_db_connection) ):
    """
    deletes a stall by stall_id
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM stalls WHERE stall_id = %s;",
            (request.stall_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Stall not found")
        
        conn.commit()
        return {
            "status": "success",
            "message": "Stall deleted successfully!"
        }
    except Exception as e:
        conn.rollback()
        # If it's already an HTTPException (like 409 or 404), re-raise it
        if isinstance(e, HTTPException):
            raise e
        # Otherwise, it's a server error
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()