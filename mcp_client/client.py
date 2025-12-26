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
        self.session = None 
        self.model_name = model
        self.gemini_client = genai.Client(api_key=API_KEY)
        self.stdio = None
        self.write = None
        self.exit_stack = AsyncExitStack()
        self.tools_list = None
        self.connection = None

    async def connect_to_server(self, server_url):
        try:
            self.connection = sse_client(server_url)
            streams = await self.exit_stack.enter_async_context(self.connection)
            read_stream, write_stream = streams
            self.session = await self.exit_stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
            await self.session.initialize()
            tools_result = await self.session.list_tools()
            self.tools_list = tools_result
            for tool in tools_result.tools:
                print(f"tool name - {tool.name}")
        except Exception as e:
            print(f"Exception - {e}")
    
    async def get_mcp_tools(self):
        try:
            tools_result = await self.session.list_tools()
            declarations = []
            for tool in tools_result.tools:
                declarations.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                })
            return declarations
        except Exception as e:
            print(f"Exception in get_mcp_tools - {e}")

    async def process_query(self, query):
        try:
            mcp_tools = await self.session.list_tools()
            response = await self.gemini_client.aio.models.generate_content(
                model=self.model_name,
                contents=query,
                config={'tools': mcp_tools.tools}
            )
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    name = part.function_call.name
                    args = part.function_call.args
                    result = await self.session.call_tool(name, arguments=args)
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
        except Exception as e:
            print(f"Exception in process_query - {str(e)}")