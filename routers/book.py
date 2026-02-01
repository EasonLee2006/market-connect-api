# /book: Endpoint to book a stall slot

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from utils.database import get_db_connection
from routers.enums import SlotStatus

router = APIRouter()

def checkUserExists(cursor, user_id: int) -> bool:
    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = %s;", 
        (user_id,)
    )
    return cursor.fetchone() is not None

class BookingRequest(BaseModel):
    user_id: int
    slot_id: int
    quantity: int = Field(default=1, ge=1)
@router.post("/book")
def book_stall( request: Annotated[BookingRequest, Query()], conn = Depends(get_db_connection) ):
    """
    books a stall by user_id, slot_id, and quantity
    """
    cursor = conn.cursor()
    try:
        if not checkUserExists(cursor, request.user_id):
            raise HTTPException(status_code=404, detail="User not found")

        # Check if slot exists and is available
        cursor.execute(
            "SELECT status, available_quantity FROM slots WHERE slot_id = %s FOR UPDATE;", 
            (request.slot_id,)
        )
        slot_row = cursor.fetchone()
        if not slot_row:
            raise HTTPException(status_code=404, detail="Slot not found")
        
        current_status = slot_row['status']
        current_available_quantity = slot_row['available_quantity']

        if current_status != SlotStatus.AVAILABLE.value:
            conn.rollback() # Cancel transaction
            # Return 409 Conflict (standard for "state conflict")
            raise HTTPException(status_code=409, detail="This slot is not available for booking")
        
        if current_available_quantity < request.quantity:
            conn.rollback() # Cancel transaction
            raise HTTPException(status_code=409, detail=f"Not enough quantity available for booking. Requested: {request.quantity}, Available: {current_available_quantity}")

        cursor.execute(
            "UPDATE slots SET available_quantity = available_quantity - %s WHERE slot_id = %s;",
            (request.quantity, request.slot_id)
        )
        cursor.execute(
            """
            INSERT INTO bookings (user_id, slot_id, quantity, payment_status) 
            VALUES (%s, %s, %s, 'PENDING') 
            RETURNING booking_id;
            """,
            (request.user_id, request.slot_id, request.quantity)
        )
        new_booking_id = cursor.fetchone()['booking_id']

        conn.commit() # Commit transaction
        
        return {
            "status": "success", 
            "message": "Booking confirmed!", 
            "booking_id": new_booking_id,
            "slot_id": request.slot_id,
            "user_id": request.user_id,
            "quantity": request.quantity
        }
    except Exception as e:
        conn.rollback() # If any error happens, undo everything
        # If it's already an HTTPException (like 409 or 404), re-raise it
        if isinstance(e, HTTPException):
            raise e
        # Otherwise, it's a server error
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
