from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum
from typing import List


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

class CustomerRecord(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    gender: str

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
        "gender": payload.gender.value
    }

    return CreateCustomerResponse(
        customer_id=customer_id,
        message="Customer created successfully"
    )

# -----------------------------
# GET Endpoint: List All Customers
# -----------------------------
@app.get("/customers", response_model=List[CustomerRecord])
def list_customers():
    """Return all customers from the in-memory database."""
    return [
        CustomerRecord(customer_id=cid, **data)
        for cid, data in mock_db.items()
    ]

# -----------------------------
# GET Endpoint: Get Customer by ID
# -----------------------------
@app.get("/customers/{customer_id}", response_model=CustomerRecord)
def get_customer(customer_id: str):
    """Return a single customer by their customer_id."""
    if customer_id not in mock_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerRecord(customer_id=customer_id, **mock_db[customer_id])

# -----------------------------
# DELETE Endpoint: Delete Customer
# -----------------------------
@app.delete("/customers/{customer_id}", response_model=CreateCustomerResponse)
def delete_customer(customer_id: str):
    """Delete a customer by their customer_id."""
    if customer_id not in mock_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    del mock_db[customer_id]
    return CreateCustomerResponse(
        customer_id=customer_id,
        message="Customer deleted successfully"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)