<div align="center">
  <img src="https://raw.githubusercontent.com/CyprianFusi/MCP-server-postgres/main/assets/binati_logo.png" alt="BINATI AI Logo" width="75"/><strong></strong>

  # PostgreSQL MCP Server

  _By **BINATI AInalytics**_
</div>


An MCP (Model Context Protocol) server that provides access to PostgreSQL databases through resources, tools, and prompts for data analysis.

# Screenshoots
![MCP Demo](assets/ui_1.png)
![MCP Demo](assets/ui_2.png)
![MCP Demo](assets/ui_3.png)
![MCP Demo](assets/ui_4.png)
![MCP Demo](assets/ui_5.png)
![MCP Demo](assets/ui_6.png)

## Features

### Resources
- **postgres://info** - Server information and quick reference

### Tools
- **list_tables** - List all tables in the database
- **get_table_schema** - Get detailed schema for a specific table
- **execute_query** - Execute read-only SQL queries (SELECT, WITH, SHOW)
- **get_table_stats** - Get statistics for a table (row count, size, indexes)

### Prompts
- **analyze_table** - Generate a comprehensive analysis prompt for a specific table
- **find_relationships** - Analyze database to find relationships between tables
- **data_quality_check** - Perform comprehensive data quality check

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for package management.

```bash
# Install dependencies
uv sync
```

## Configuration

Create a `.env` file with your database credentials. You can either:

**Option 1: Individual components (recommended)**
```env
DATABASE_HOST=localhost
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_PORT=5432
DATABASE_NAME=your_database
```

**Option 2: Full connection URL**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb
```

Note: If you use the SQLAlchemy format `postgresql+psycopg://`, it will be automatically converted to the psycopg format `postgresql://`.

The server will automatically construct the connection URL from individual components if DATABASE_URL is not provided.

## Usage

### Development Mode

Test the server using the MCP Inspector:

```bash
uv run mcp dev main.py
```

This will launch the MCP Inspector in your browser where you can:
- Browse available resources
- Test tools with different parameters
- Try out prompts

### Install to Claude Desktop

To use this server with Claude Desktop:

```bash
uv run mcp install main.py --name "PostgreSQL Server"
```

### Direct Execution

Run the server directly:

```bash
uv run python main.py
```

## Example Usage

### Using Resources

1. **Get server info**:
   - Resource URI: `postgres://info`
   - Returns: Server information and available operations

### Using Tools

1. **List all tables**:
   ```json
   Tool: list_tables
   Returns: {"tables": [...], "count": 4}
   ```

2. **Get table schema**:
   ```json
   {
     "table_name": "users"
   }
   Returns: {"table_name": "users", "columns": [...], "column_count": 5}
   ```

3. **Execute a query**:
   ```json
   {
     "query": "SELECT * FROM users LIMIT 10"
   }
   ```
   Returns: JSON with rows, row_count, and columns

2. **Get table statistics**:
   ```json
   {
     "table_name": "users"
   }
   ```
   Returns: JSON with row_count, total_size, table_size, and indexes_size

### Using Prompts

1. **analyze_table**:
   - Generates a comprehensive analysis workflow for a specific table
   - Parameter: `table_name`

2. **find_relationships**:
   - Generates a prompt to analyze and document table relationships

3. **data_quality_check**:
   - Generates a prompt for comprehensive data quality analysis

## Security

- **Read-only queries**: The `execute_query` tool only allows SELECT, WITH, and SHOW statements
- **SQL injection protection**: All queries use parameterized statements where applicable
- **Connection management**: Database connections are managed through lifespan context

## Development

### Code Quality

The project follows strict development guidelines:

```bash
# Format code
uv run --frozen ruff format .

# Check linting
uv run --frozen ruff check .

# Fix linting issues
uv run --frozen ruff check . --fix

# Type checking
uv run --frozen pyright
```

### Testing

```bash
# Run tests
uv run --frozen pytest
```

## Architecture

The server uses:
- **FastMCP**: High-level MCP server framework
- **psycopg**: Async PostgreSQL adapter for Python
- **Lifespan management**: Database connection is established at server startup and closed at shutdown
- **Type safety**: Full type hints throughout the codebase

## License

MIT
