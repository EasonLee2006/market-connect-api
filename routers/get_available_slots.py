# /get_available_slots: Endpoint to retrieve all available slots

from fastapi import APIRouter, Depends, HTTPException
from utils.database import get_db_connection

router = APIRouter()

@router.get("/get_available_slots")
def get_available_slots( conn = Depends(get_db_connection) ):
    """
    returns all available slots
    """
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            a.slot_id,
            a.price,
            a.available_quantity
        FROM slots a
        JOIN stalls s ON a.stall_id = s.stall_id
        WHERE a.status = 0 AND a.available_quantity > 0;
        """
        cursor.execute(query)
        slots = cursor.fetchall()
        cursor.close()
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available slots: {e}")