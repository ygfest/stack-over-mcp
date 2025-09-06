# Stack Over MCP

An MCP (Model Context Protocol) server that provides LLMs with tools to search Stack Overflow for programming solutions, helping ground responses in real-world code examples and reduce hallucinations.

## Features

- **Smart Search**: Search Stack Overflow questions with customizable filters
- **Detailed Question Analysis**: Get complete question details with all answers
- **Tag-Based Discovery**: Find popular solutions by programming language/framework
- **Real-time Results**: Direct access to Stack Overflow's API
- **Rich Metadata**: Scores, view counts, acceptance status, and more

## Installation

1. **Clone and setup the project:**
   ```bash
   cd stack-over-mcp
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the MCP Server

```bash
python main.py
```

The server will start and provide three main tools:

### 1. `search_stackoverflow`
Search Stack Overflow questions with flexible filtering:

```python
# Basic search
search_stackoverflow("python list comprehension")

# Advanced search with filters
search_stackoverflow(
    query="react hooks error",
    limit=5,
    sort="votes",
    tags=["javascript", "react"],
    accepted_only=True
)
```

**Parameters:**
- `query`: Search terms
- `limit`: Max results (1-100, default: 10)
- `sort`: "relevance", "activity", "votes", or "creation"
- `tags`: Filter by programming tags
- `accepted_only`: Only questions with accepted answers

### 2. `get_question_details`
Get complete information about a specific question:

```python
# Get question with all answers
get_question_details(question_id=12345678)

# Get just question metadata
get_question_details(question_id=12345678, include_answers=False)
```

### 3. `search_by_tags`
Find popular questions by technology tags:

```python
# Find top Python questions
search_by_tags(tags=["python"], sort="votes", min_score=10)

# Find recent React + TypeScript questions
search_by_tags(
    tags=["javascript", "react", "typescript"],
    sort="activity",
    limit=5
)
```

## Integration with MCP Clients

This server is designed to work with MCP-compatible clients like Claude Desktop. Add it to your MCP configuration:

```json
{
  "mcpServers": {
    "stack-over-mcp": {
      "command": "python",
      "args": ["path/to/stack-over-mcp/main.py"]
    }
  }
}
```

## Use Cases

- **Debugging**: Find solutions to specific error messages
- **Learning**: Discover best practices and common patterns
- **Code Review**: Validate approaches against community solutions
- **Architecture**: Find proven solutions for complex problems
- **API Usage**: Get real examples of library/framework usage

## API Rate Limits

The Stack Overflow API has rate limits:
- **Unauthenticated**: 300 requests per day per IP
- **Authenticated**: 10,000 requests per day (requires API key)

For production use, consider implementing API key authentication in `stack_api.py`.

## Project Structure

```
stack-over-mcp/
├── main.py          # FastMCP server with tool definitions
├── stack_api.py     # Stack Overflow API client
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Contributing

Feel free to enhance the server with additional features:
- API key authentication for higher rate limits
- Caching for frequently requested questions
- Advanced filtering options
- Support for other Stack Exchange sites

## License

This project is open source and available under the MIT License.
