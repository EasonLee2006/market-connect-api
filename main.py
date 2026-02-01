from fastapi import FastAPI
from routers import users, owners, stalls, slots, bookings, get_available_slots, book, pay, cancel_booking

# Initialize the app
app = FastAPI(
    title="Market Connect API",
    description="Backend API for stall reservation system",
    version="0.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Market Connect API! System is online"}

app.include_router(users.router)
app.include_router(owners.router)
app.include_router(stalls.router)
app.include_router(slots.router)
app.include_router(bookings.router)

app.include_router(get_available_slots.router)
app.include_router(book.router)
app.include_router(pay.router)
app.include_router(cancel_booking.router)

