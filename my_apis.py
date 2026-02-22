from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum


app = FastAPI()

class Gender(Enum):
    MALE = 'M'
    FEMALE = 'F'

# -----------------------------
# Pydantic Model (Request Body)
# -----------------------------
class CreateCustomerRequest(BaseModel):
    """
    Request model for creating a new customer.

    Attributes:
        first_name (str): The customer's first name. Example: "John"
        last_name (str): The customer's last name. Example: "Doe"
        email (str): The customer's email address. Example: "john.doe@example.com"
        phone (str): The customer's phone number. Example: "555-123-4567"
        gender (Gender): The customer's gender. Example: "M"
    """
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    email: str = Field(..., example="john.doe@example.com")
    phone: str = Field(..., example="555-123-4567")
    gender: Gender = Field(..., example="M")

# -----------------------------
# Pydantic Model (Response Body)
# -----------------------------
class CreateCustomerResponse(BaseModel):
    customer_id: str
    message: str

# -----------------------------
# Mock In-Memory Database
# -----------------------------
mock_db = {}

# -----------------------------
# POST Endpoint: Create Customer
# -----------------------------
@app.post("/customers", response_model=CreateCustomerResponse)
def create_customer(payload: CreateCustomerRequest):

    # Check for duplicate email (simple validation)
    for customer in mock_db.values():
        if customer["email"] == payload.email:
            raise HTTPException(
                status_code=400,
                detail="Customer with this email already exists"
            )

    # Generate a unique customer ID
    customer_id = str(uuid4())

    # Store customer in mock DB
    mock_db[customer_id] = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phone": payload.phone,
        "gender": payload.gender
    }

    return CreateCustomerResponse(
        customer_id=customer_id,
        message="Customer created successfully"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)