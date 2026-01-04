from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from contextlib import AsyncExitStack
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("API_KEY")  
class MCPClient:
    def __init__(self, model: str="gemini-2.5-flash"):
        self.session = {} 
        self.tool_to_session = {}
        self.model_name = model
        self.gemini_client = genai.Client(api_key=API_KEY)
        self.stdio = None
        self.write = None
        self.exit_stack = AsyncExitStack()
        self.tools_list = None
        self.connection = None

    async def connect_to_server(self, server_url, server_id):
        try:
            self.connection = sse_client(server_url)
            streams = await self.exit_stack.enter_async_context(self.connection)
            read_stream, write_stream = streams
            session = await self.exit_stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
            await session.initialize()
            self.session[server_id] = session
            tools_result = await session.list_tools()
            self.tools_list = tools_result
            for tool in tools_result.tools:
                print(f"Server [{server_id}] registered tool: {tool.name}")
                self.tool_to_session[tool.name] = server_id
        except Exception as e:
            print(f"Exception - {e}")
    
    async def cleanup(self):
        global exit_stack
        await self.exit_stack.aclose()
    
    async def get_mcp_tools(self):        
        try:
            declarations = []
            for server_id, session in self.session.items():
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    declarations.append(tool)
            return declarations
        except Exception as e:
            print(f"Exception in get_mcp_tools - {e}")

    async def process_query(self, query):
        try:
            mcp_tools = await self.get_mcp_tools()
            response = await self.gemini_client.aio.models.generate_content(
                model=self.model_name,
                contents=query,
                config={'tools': mcp_tools}
            )
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    name = part.function_call.name
                    args = part.function_call.args
                    server_id = self.tool_to_session.get(name)
                    session = self.session[server_id]
                    result = await session.call_tool(name, arguments=args)
                    final_response = await self.gemini_client.aio.models.generate_content(
                        model=self.model_name,
                        contents=[
                            {"role": "user", "parts": [{"text": query}]},
                            response.candidates[0].content,
                            {
                                "role": "tool",
                                "parts": [{
                                    "function_response": {
                                        "name": name,
                                        "response": {"result": result.content}
                                    }
                                }]
                            }
                        ]
                    )
                    return final_response.text
                else:
                    return part.text
        except Exception as e:
            print(f"Exception in process_query - {str(e)}")