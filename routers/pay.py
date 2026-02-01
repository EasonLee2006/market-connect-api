# /pay: process payment for a booking

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from utils.database import get_db_connection

router = APIRouter()

class PaymentRequest(BaseModel):
    booking_id: int
    payment_method: str
@router.put("/pay")
def process_payment(request: Annotated[PaymentRequest, Query()], conn = Depends(get_db_connection)):
    """
    processes a payment for a booking
    """
    cursor = conn.cursor()
    try:
        # Check if booking exists
        cursor.execute(
            "SELECT booking_id FROM bookings WHERE booking_id = %s FOR UPDATE;",
            (request.booking_id,)
        )
        booking_row = cursor.fetchone()
        if not booking_row:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Update payment status
        cursor.execute(
            "UPDATE bookings SET payment_status = 'PAID', payment_method = %s WHERE booking_id = %s;",
            (request.payment_method, request.booking_id)
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Payment processed successfully!"
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