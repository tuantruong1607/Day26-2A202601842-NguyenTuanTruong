"""Google ADK weather agent backed by a Streamable HTTP MCP server."""
import os

from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

logger.info("Initializing weather agent with MCP server: %s", MCP_SERVER_URL)

connection_params = StreamableHTTPConnectionParams(
    url=MCP_SERVER_URL,
    timeout=30.0,
)

# McpToolset connects lazily when ADK needs to discover or call a tool.
weather_tools = McpToolset(connection_params=connection_params)

root_agent = Agent(
    name="weather_agent",
    model=GEMINI_MODEL,
    description="Answers current-weather and short forecast questions.",
    instruction=(
        "Use the MCP weather tools for weather facts. "
        "Mention the city and forecast period clearly, and never invent readings."
    ),
    tools=[weather_tools],
)

logger.info("Weather agent initialized with model %s", GEMINI_MODEL)

