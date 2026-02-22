# Custom MCP Server with GitHub Copilot as Client

This project demonstrates a **custom MCP (Model Context Protocol) Server** that exposes REST API methods as **Tools** for **GitHub Copilot** to use as an AI client.

## Architecture

```
GitHub Copilot (Client)
        │
        │  MCP Protocol (stdio or HTTP)
        ▼
MCP Server (servers/basic_mcp_http.py or servers/basic_mcp_stdio.py)
        │
        │  HTTP REST calls
        ▼
FastAPI REST API (my_apis.py)
        │
        ▼
In-Memory Mock Database
```

## Components

### 1. FastAPI REST API (`my_apis.py`)
A Customer management REST API with full CRUD operations:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/customers` | Create a new customer |
| `GET` | `/customers` | List all customers |
| `GET` | `/customers/{customer_id}` | Get a customer by ID |
| `DELETE` | `/customers/{customer_id}` | Delete a customer |

### 2. MCP Servers

#### HTTP Transport (`servers/basic_mcp_http.py`)
Runs as an HTTP server on port 8000. Exposes the following **MCP Tools** that wrap the REST API:
- `call_create_customer_api` – calls `POST /customers`
- `call_list_customers_api` – calls `GET /customers`
- `call_get_customer_api` – calls `GET /customers/{customer_id}`
- `call_delete_customer_api` – calls `DELETE /customers/{customer_id}`

#### Stdio Transport (`servers/basic_mcp_stdio.py`)
Runs as a stdio process (launched by GitHub Copilot directly). Exposes the same customer tools plus expense tracking tools.

### 3. GitHub Copilot Configuration (`.vscode/mcp.json`)
Registers the MCP server with GitHub Copilot in VS Code. Three server configurations are available:
- **`mcp-ai-agent`** – stdio transport (default, launched by Copilot)
- **`mcp-ai-agent-http`** – HTTP transport (connect to running server)
- **`mcp-ai-agent-debug`** – stdio with debugpy attached

## Getting Started

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- VS Code with GitHub Copilot extension

### Setup

1. **Clone the repository and install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   ```bash
   cp .env-sample .env
   # Edit .env with your GitHub token for GitHub Models (optional)
   ```

3. **Start the FastAPI REST API:**
   ```bash
   uv run uvicorn my_apis:app --host 0.0.0.0 --port 9000
   ```

4. **Start the MCP HTTP Server** (for HTTP transport mode):
   ```bash
   cd servers && uv run python basic_mcp_http.py
   ```
   Or from the project root:
   ```bash
   uv run servers/basic_mcp_http.py
   ```

5. **Open VS Code** – GitHub Copilot will automatically detect the MCP server configuration from `.vscode/mcp.json`.

### Using GitHub Copilot as Client

Once the MCP server is running, open GitHub Copilot Chat in VS Code and use **Agent mode**. You can now ask Copilot to perform customer operations using natural language:

```
Create a new customer: John Doe, john.doe@example.com, 555-123-4567, Male
```

```
List all customers
```

```
Get the customer with ID <customer_id>
```

```
Delete the customer with ID <customer_id>
```

Copilot will automatically select the appropriate MCP Tool and call the REST API on your behalf.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CUSTOMERS_API_URL` | Base URL for the Customer REST API | `http://localhost:9000` |
| `API_HOST` | AI provider: `github`, `azure`, `ollama`, `openai` | `github` |
| `GITHUB_TOKEN` | GitHub token for GitHub Models API | – |
| `GITHUB_MODEL` | Model name for GitHub Models | `gpt-4o` |

## MCP Tools Reference

### `call_create_customer_api`
Creates a new customer via the REST API.

**Input:**
- `first_name` (string) – Customer's first name
- `last_name` (string) – Customer's last name
- `email` (string) – Customer's email address
- `phone` (string) – Customer's phone number
- `gender` (enum: `M` or `F`) – Customer's gender

### `call_list_customers_api`
Returns all customers from the REST API.

### `call_get_customer_api`
Returns a single customer by ID.

**Input:**
- `customer_id` (string) – The unique customer identifier

### `call_delete_customer_api`
Deletes a customer by ID.

**Input:**
- `customer_id` (string) – The unique customer identifier to delete
