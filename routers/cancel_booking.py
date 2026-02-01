# /cancel_booking: cancel a booking by booking_id and free up the slot

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from utils.database import get_db_connection

router = APIRouter()

class CancelBookingRequest(BaseModel):
    booking_id: int
@router.put("/cancel_booking")
def cancel_booking( request: Annotated[CancelBookingRequest, Query()], conn = Depends(get_db_connection) ):
    """
    cancels a booking by booking_id,\n
    also frees up the slot associated with the booking
    """
    cursor = conn.cursor()
    try:
        # Get the slot_id associated with the booking
        cursor.execute(
            "SELECT slot_id, payment_status, quantity FROM bookings WHERE booking_id = %s;",
            (request.booking_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        slot_id = row['slot_id']
        quantity = row['quantity']
        payment_status = row['payment_status']

        # Prevent cancellation if already paid or canceled
        if payment_status != 'PENDING':
            raise HTTPException(status_code=400, detail="Cannot cancel a paid or canceled booking")
        
        # Update the booking status to canceled
        cursor.execute(
            "UPDATE bookings SET payment_status = 'CANCELED' WHERE booking_id = %s;",
            (request.booking_id,)
        )

        # Free up the slot by increasing available_quantity
        cursor.execute(
            "UPDATE slots SET available_quantity = available_quantity + %s WHERE slot_id = %s;",
            (quantity, slot_id)
        )

        conn.commit()

        return {
            "status": "success",
            "message": f"Booking cancelled and slot freed successfully! Quantity freed: {quantity}"
        }
    except Exception as e:
        conn.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error cancelling booking: {e}")
    finally:
        cursor.close()