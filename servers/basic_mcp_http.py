import csv
import logging
import os
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Annotated
from my_apis import CreateCustomerRequest, CreateCustomerResponse
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


mcp = FastMCP("Retail Banking", middleware=middleware)

# @mcp.tool
# async def create_customer(
#     first_name: Annotated[str, "Customer's first name"],
#     last_name: Annotated[str, "Customer's last name"],
#     email: Annotated[str, "Customer's email address"],
#     phone: Annotated[str, "Customer's phone number"],
#     gender: Annotated[Gender, "Customer's gender"]
# ):
#     """Create a new customer and save to customers_data.csv file."""
#     logger.info(f"Creating customer: {first_name} {last_name}")

#     try:
#         file_exists = CUSTOMERS_DATA_FILE.exists()

#         with open(CUSTOMERS_DATA_FILE, "a", newline="", encoding="utf-8") as file:
#             writer = csv.writer(file)

#             if not file_exists:
#                 writer.writerow(["first_name", "last_name", "email", "phone", "gender"])

#             writer.writerow([first_name, last_name, email, phone, gender.value])

#         return f"Successfully created customer: {first_name} {last_name}"

#     except Exception as e:
#         logger.error(f"Error creating customer: {str(e)}")
#         return "Error: Unable to create customer"

@mcp.tool
async def call_create_customer_api(payload: CreateCustomerRequest) -> CreateCustomerResponse:
    """
    Call the Create Customer API endpoint from Consumer Banking (my_apis.py) to create a new customer.
    """
    url = "http://localhost:8100/customers"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload.model_dump())

    response.raise_for_status()
    
    data = response.json()

    return CreateCustomerResponse(customer_id = data["customer_id"], message = data["message"])


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
