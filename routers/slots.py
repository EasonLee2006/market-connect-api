# /get_slots: Endpoint to retrieve all slots
# /create_slot: Endpoint to create a new slot
# /delete_slot: Endpoint to delete a slot

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from utils.database import get_db_connection
from tabulate import tabulate
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/get_slots")
def get_slots( conn = Depends(get_db_connection) ):
    """
    returns all slots
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM slots;")
        slots = cursor.fetchall()
        cursor.close()
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching slots: {e}")

@router.get("/get_slots/table", response_class=PlainTextResponse)
def get_slots_table(conn = Depends(get_db_connection)):
    """
    Returns a table of all slots.
    Best viewed in a browser or terminal.
    """
    try:
        slots = get_slots(conn)
    
        # Check if empty to avoid errors
        if not slots:
            return "No slots found."

        # Convert the list of dictionaries into the table format
        table_content = tabulate(slots, headers="keys", tablefmt="psql")
        
        return table_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching slots: {e}")

class CreateSlotsRequest(BaseModel):
    stall_id: int
    starting_date: str = Field(description="YYYY-MM-DD")
    ending_date: str = Field(description="YYYY-MM-DD")
    starting_time: str = Field(description="HH:MM:SS")
    ending_time: str = Field(description="HH:MM:SS")
    price: int
    discounted_price: int | None = None
    total_quantity: int
@router.post("/create_slot")
def create_slot( request: Annotated[CreateSlotsRequest, Query()], conn = Depends(get_db_connection) ):
    """
    creates a slot by stall_id, date, price
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO slots (stall_id, starting_date, ending_date, starting_time, ending_time, price, discounted_price, total_quantity, available_quantity) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING slot_id;
            """,
            (request.stall_id, request.starting_date, request.ending_date, request.starting_time, request.ending_time, request.price, request.discounted_price, request.total_quantity, request.total_quantity)
        )
        new_slot_id = cursor.fetchone()['slot_id']
        conn.commit()
        return {
            "status": "success",
            "message": "slot created successfully!",
            "slot_id": new_slot_id,
            "stall_id": request.stall_id,
            "starting_date": request.starting_date,
            "ending_date": request.ending_date,
            "starting_time": request.starting_time,
            "ending_time": request.ending_time,
            "price": request.price,
            "discounted_price": request.discounted_price,
            "total_quantity": request.total_quantity
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

class DeleteSlotsRequest(BaseModel):
    slot_id: int
@router.delete("/delete_slot")
def delete_slot( request: Annotated[DeleteSlotsRequest, Query()], conn = Depends(get_db_connection) ):
    """
    deletes a slot by slot_id
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM slots WHERE slot_id = %s;",
            (request.slot_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Slot not found")
        
        conn.commit()
        return {
            "status": "success",
            "message": "Slot deleted successfully!"
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