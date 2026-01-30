# /cancel_booking: cancel a booking by booking_id and free up the slot

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from utils.database import get_db_connection

router = APIRouter()

class CancelBookingRequest(BaseModel):
    booking_id: int
@router.put("/cancel_booking")
def cancel_booking( request: CancelBookingRequest, conn = Depends(get_db_connection) ):
    """
    cancels a booking by booking_id,
    also frees up the slot associated with the booking
    """
    cursor = conn.cursor()
    try:
        # Get the slot_id associated with the booking
        cursor.execute(
            "SELECT slot_id, payment_status FROM bookings WHERE booking_id = %s;",
            (request.booking_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        slot_id = row['slot_id']
        payment_status = row['payment_status']

        # Prevent cancellation if already paid
        if payment_status == 'PAID':
            raise HTTPException(status_code=400, detail="Cannot cancel a paid booking")
        
        # Update the booking status to canceled
        cursor.execute(
            "UPDATE bookings SET payment_status = 'CANCELED' WHERE booking_id = %s;",
            (request.booking_id,)
        )

        # Free up the slot by setting its status to available (0)
        cursor.execute(
            "UPDATE slots SET status = 0 WHERE slot_id = %s;",
            (slot_id,)
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Booking cancelled and slot freed successfully!"
        }
    except Exception as e:
        conn.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error cancelling booking: {e}")
    finally:
        cursor.close()