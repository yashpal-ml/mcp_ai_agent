import csv
import logging
import os
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Annotated
from my_apis import CreateCustomerRequest, CreateCustomerResponse, CustomerRecord
import httpx

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware

# from opentelemetry_middleware import OpenTelemetryMiddleware, configure_aspire_dashboard

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(message)s")
logger = logging.getLogger("RetailBankingMCP")
logger.setLevel(logging.INFO)

# middleware: list[Middleware] = []
# if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
#     logger.info("Setting up Aspire Dashboard instrumentation (OTLP)")
#     configure_aspire_dashboard(service_name="expenses-mcp")
#     middleware = [OpenTelemetryMiddleware(tracer_name="expenses.mcp")]


SCRIPT_DIR = Path(__file__).parent
CUSTOMERS_DATA_FILE = SCRIPT_DIR / "customers_data.csv"

BASE_URL = os.getenv("CUSTOMERS_API_URL", "http://localhost:9000")

# mcp = FastMCP("Retail Banking", middleware=middleware)
mcp = FastMCP("Retail Banking")

@mcp.tool
async def call_create_customer_api(payload: CreateCustomerRequest) -> CreateCustomerResponse:
    """
    Call the Create Customer API endpoint from Consumer Banking (my_apis.py) to create a new customer.
    """
    url = f"{BASE_URL}/customers"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload.model_dump(mode="json"))

    response.raise_for_status()

    data = response.json()

    return CreateCustomerResponse(customer_id=data["customer_id"], message=data["message"])


@mcp.tool
async def call_list_customers_api() -> list[CustomerRecord]:
    """
    Call the List Customers API endpoint to retrieve all customers.
    """
    url = f"{BASE_URL}/customers"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    response.raise_for_status()

    return [CustomerRecord(**item) for item in response.json()]


@mcp.tool
async def call_get_customer_api(customer_id: Annotated[str, "The unique customer ID"]) -> CustomerRecord:
    """
    Call the Get Customer API endpoint to retrieve a single customer by ID.
    """
    url = f"{BASE_URL}/customers/{customer_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    response.raise_for_status()

    return CustomerRecord(**response.json())


@mcp.tool
async def call_delete_customer_api(customer_id: Annotated[str, "The unique customer ID to delete"]) -> str:
    """
    Call the Delete Customer API endpoint to remove a customer by ID.
    """
    url = f"{BASE_URL}/customers/{customer_id}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(url)

    response.raise_for_status()

    data = response.json()

    return f"Customer deleted successfully! ID: {data['customer_id']}"


@mcp.resource("resource://customers")
async def get_customers_data():
    """Get raw customer data from CSV file"""
    logger.info("Customers data accessed")

    try:
        with open(CUSTOMERS_DATA_FILE, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            customers_data = list(reader)

        csv_content = f"Customer data ({len(customers_data)} entries):\n\n"
        for customer in customers_data:
            csv_content += (
                f"First Name: {customer['first_name']}, "
                f"Last Name: {customer['last_name']}, "
                f"Email: {customer['email']}, "
                f"Phone: {customer['phone']}, "
                f"Gender: {customer['gender']}\n"
            )

        return csv_content

    except FileNotFoundError:
        logger.error("Customers data file not found")
        return "Error: Customer data unavailable"
    except Exception as e:
        logger.error(f"Error reading customers data: {str(e)}")
        return "Error: Unable to retrieve customer data"

@mcp.prompt
def analyse_create_customer_api(
    gender: str | None = None, start_date: str | None = None, end_date: str | None = None
) -> str:
    """Generate a prompt to analyze customer data from the customers_data.csv with optional filters."""

    filters = []
    if gender:
        filters.append(f"Gender: {gender}")
    if start_date:
        filters.append(f"From: {start_date}")
    if end_date:
        filters.append(f"To: {end_date}")

    filter_text = f" ({', '.join(filters)})" if filters else ""

    return f"""
    Please analyze my customer data{filter_text} and provide:

    1. Total customer count by gender
    2. Average age of customers (if age data is available)
    3. Customer distribution by gender
    4. Most common last name or first name
    5. Customer retention rate (if applicable)

    Use the customer data to generate actionable insights.
    """


if __name__ == "__main__":
    logger.info("MCP Customers API server starting (HTTP mode on port 8000)")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
