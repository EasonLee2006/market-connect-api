# /get_owners: Endpoint to retrieve all owners
# /create_owner: Endpoint to create a new owner
# /delete_owner: Endpoint to delete a owner

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from utils.database import get_db_connection
from tabulate import tabulate
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/get_owners")
def get_owners( conn = Depends(get_db_connection) ):
    """
    Returns a list of all owners.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM owners;")
        owners = cursor.fetchall()
        cursor.close()
        return owners
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching owners: {e}")

@router.get("/get_owners/table", response_class=PlainTextResponse)
def get_owners_table(conn = Depends(get_db_connection)):
    """
    Returns a table of all owners.
    Best viewed in a browser or terminal.
    """
    try:
        owners = get_owners(conn)

        # Check if empty to avoid errors
        if not owners:
            return "No owner found."

        # Convert the list of dictionaries into the table format
        # tablefmt="psql" gives you that specific postgres style you asked for
        table_content = tabulate(owners, headers="keys", tablefmt="psql")
        
        return table_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching owners: {e}")

class CreateOwnerRequest(BaseModel):
    name: str
    line_uid: str | None = None
    description: str | None = None
    phone: str | None = None
    category: str | None = None
    reputation_score: int = Field(default=100, ge=0, le=100)
@router.post("/create_owner")
def create_owner( request: Annotated[CreateOwnerRequest, Query()], conn = Depends(get_db_connection) ):
    """
    Creates a new owner in the database.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO owners (name, line_uid, description, phone, category, reputation_score) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            RETURNING owner_id;
            """,
            (request.name, request.line_uid, request.description, request.phone, request.category, request.reputation_score)
        )
        new_owner_id = cursor.fetchone()['owner_id']
        conn.commit()
        return {
            "status": "success",
            "message": "Owner created successfully!",
            "owner_id": new_owner_id,
            "owner_name": request.name
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

class DeleteOwnerRequest(BaseModel):
    owner_id: int
@router.delete("/delete_owner")
def delete_owner( request: Annotated[DeleteOwnerRequest, Query()], conn = Depends(get_db_connection) ):
    """
    Deletes an owner from the database.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM owners WHERE owner_id = %s;",
            (request.owner_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Owner not found")
        
        conn.commit()
        return {
            "status": "success",
            "message": "Owner deleted successfully!"
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