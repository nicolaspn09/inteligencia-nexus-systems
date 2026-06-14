import os
from dotenv import load_dotenv
load_dotenv()

SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')


MCP_SERVERS_CONFIG = {
    'google_calendar': {
        'url': f'https://server.smithery.ai/@goldk3y/google-calendar-mcp/mcp?api_key=4f1b4ea0-2453-4a2b-9d73-ce9be67c702f',
        'transport': 'streamable_http',
    }
}