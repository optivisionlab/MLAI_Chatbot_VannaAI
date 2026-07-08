# All imports at the top
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool, SaveTextMemoryTool
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.google import GeminiLlmService
from vanna.integrations.postgres import PostgresRunner
from vanna.integrations.chromadb import ChromaAgentMemory
import os

#get env
DB_USER = os.getenv("DB_USER", default='')
DB_PASSWORD = os.getenv("DB_PASSWORD", default='')
DB_DOMAIN = os.getenv("DB_DOMAIN", default='localhost')
DB_PORT = os.getenv("DB_PORT", default='5432')
DB_NAME = os.getenv("DB_NAME", default='postgres')

LLM_MODEL = os.getenv("LLM_MODEL", default='gemini-2.5-flash')
LLM_KEY = os.getenv("LLM_KEY", default='')

# Configure your LLM
llm = GeminiLlmService(
    model=LLM_MODEL,
    api_key=LLM_KEY  # Or use os.getenv("GOOGLE_API_KEY")
)

# Configure your database
db_tool = RunSqlTool(
    sql_runner=PostgresRunner(
        connection_string=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_DOMAIN}:{DB_PORT}/{DB_NAME}"
    )
)

# Configure your agent memory
agent_memory = ChromaAgentMemory(
    collection_name="vanna_memory",
    persist_directory="./chroma_db"
)

# Configure user authentication
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_cookie('vanna_email') or 'guest@example.com'
        group = 'admin' if user_email == 'admin@example.com' else 'user'
        return User(id=user_email, email=user_email, group_memberships=[group])

user_resolver = SimpleUserResolver()

# Create your agent
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])
tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory
)

# Run the server
server = VannaFastAPIServer(agent)
server.run()  # Access at http://localhost:8000