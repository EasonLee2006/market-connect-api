# /get_users: Endpoint to retrieve all users
# /create_user: Endpoint to create a new user
# /delete_user: Endpoint to delete a user

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from utils.database import get_db_connection
from tabulate import tabulate
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/get_users")
def get_users( conn = Depends(get_db_connection) ):
    """
    Returns a list of all users.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        cursor.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {e}")

@router.get("/get_users/table", response_class=PlainTextResponse)
def get_users_table(conn = Depends(get_db_connection)):
    """
    Returns a table of all users.
    Best viewed in a browser or terminal.
    """
    try:
        users = get_users(conn)
    
        # Check if empty to avoid errors
        if not users:
            return "No users found."

        # Convert the list of dictionaries into the table format
        # tablefmt="psql" gives you that specific postgres style you asked for
        table_content = tabulate(users, headers="keys", tablefmt="psql")
        
        return table_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {e}")

class CreateUserRequest(BaseModel):
    line_uid: str
    name: str
@router.post("/create_user")
def create_user( user: Annotated[CreateUserRequest, Query()], conn = Depends(get_db_connection) ):
    """
    Creates a new user in the database.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (line_uid, name) 
            VALUES (%s, %s) 
            RETURNING user_id;
            """,
            (user.line_uid, user.name)
        )
        new_user_id = cursor.fetchone()['user_id']
        conn.commit()
        return {
            "status": "success",
            "message": "User created successfully!",
            "user_id": new_user_id,
            "user_name": user.name
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

class DeleteUserRequest(BaseModel):
    user_id: int
@router.delete("/delete_user")
def delete_user( request: DeleteUserRequest, conn = Depends(get_db_connection) ):
    """
    Deletes a user from the database.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM users WHERE user_id = %s;",
            (request.user_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        return {
            "status": "success",
            "message": "User deleted successfully!"
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