# All imports at the top
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool, SaveTextMemoryTool
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.postgres import PostgresRunner
from vanna.integrations.chromadb import ChromaAgentMemory
import os
from vanna.integrations.openai import OpenAILlmService


def get_llm_config(LLM_MODEL, LLM_KEY):
    # Configure your LLM
    llm = None
    if LLM_MODEL.startswith("gemini"):
        llm = GeminiLlmService(
            model=LLM_MODEL,
            api_key=LLM_KEY  # Or use os.getenv("GOOGLE_API_KEY")
        )
    elif LLM_MODEL.startswith("gpt"):
        llm = OpenAILlmService(
            model=LLM_MODEL,
            api_key=LLM_KEY  # Or use os.getenv("OPENAI_API_KEY")
        )
    return llm


#get env
DB_USER = os.getenv("DB_USER", default='')
DB_PASSWORD = os.getenv("DB_PASSWORD", default='')
DB_DOMAIN = os.getenv("DB_DOMAIN", default='localhost')
DB_PORT = os.getenv("DB_PORT", default='5432')
DB_NAME = os.getenv("DB_NAME", default='postgres')

# LLM_PROVIDER: "gemini" (default) | "openrouter" | "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", default='gemini').lower()
LLM_MODEL = os.getenv("LLM_MODEL", default='')
LLM_KEY = os.getenv("LLM_KEY", default='')
LLM_BASE_URL = os.getenv("LLM_BASE_URL", default='')

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def build_llm():
    if LLM_PROVIDER == "gemini":
        from vanna.integrations.google import GeminiLlmService
        return GeminiLlmService(model=LLM_MODEL or 'gemini-2.5-flash', api_key=LLM_KEY)
    if LLM_PROVIDER in ("openrouter", "openai"):
        from vanna.integrations.openai import OpenAILlmService
        if LLM_PROVIDER == "openrouter":
            return OpenAILlmService(
                model=LLM_MODEL or 'google/gemini-2.5-flash',
                api_key=LLM_KEY,
                base_url=LLM_BASE_URL or OPENROUTER_BASE_URL,
            )
        kwargs = {"base_url": LLM_BASE_URL} if LLM_BASE_URL else {}
        return OpenAILlmService(model=LLM_MODEL or 'gpt-4o-mini', api_key=LLM_KEY, **kwargs)
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


# Configure your LLM
llm = build_llm()

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