# /get_bookings: Endpoint to retrieve all bookings
# /delete_booking: Endpoint to delete a booking

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from utils.database import get_db_connection
from tabulate import tabulate
from fastapi.responses import PlainTextResponse


router = APIRouter()

@router.get("/get_bookings")
def get_bookings( conn = Depends(get_db_connection) ):
    """
    returns all bookings
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings;")
        bookings = cursor.fetchall()
        cursor.close()
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bookings: {e}")

@router.get("/get_bookings/table", response_class=PlainTextResponse)
def get_bookings_table(conn = Depends(get_db_connection)):
    """
    Returns a table of all bookings.
    Best viewed in a browser or terminal.
    """
    try:
        bookings = get_bookings(conn)

        # Check if empty to avoid errors
        if not bookings:
            return "No bookings found."

        # Convert the list of dictionaries into the table format
        table_content = tabulate(bookings, headers="keys", tablefmt="psql")

        return table_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bookings: {e}")

class DeleteBookingRequest(BaseModel):
    booking_id: int
@router.delete("/delete_booking")
def delete_booking( request: Annotated[DeleteBookingRequest, Query()], conn = Depends(get_db_connection) ):
    """
    deletes a booking by booking_id,
    note: this only deletes the booking record, does not free up the slot
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM bookings WHERE booking_id = %s;",
            (request.booking_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Booking not found")
        
        conn.commit()
        return {
            "status": "success",
            "message": "Booking deleted successfully!"
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