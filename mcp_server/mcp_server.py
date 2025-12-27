from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from fastapi import FastAPI

app = FastAPI()
load_dotenv()

mcp = FastMCP(
    name="information MCP Server",
    host="127.0.0.1",
    port=8080,
)

@mcp.tool(name = "get_knowledge", description = "Get the knowledge base")
def get_knowledge():
    print(os.path.join(os.path.dirname(__file__),"data","content.txt"))
    try:
        kb_path = os.path.join(os.path.dirname(__file__),"data","content.txt")
        with open(kb_path,'r',encoding='utf-8', errors='ignore') as file:
            kb_data = file.read()
        kb_text = "here is the knowlege base\n\n" + kb_data
        return kb_text
    
    except FileNotFoundError:
        print(f"Exception - File Not Found")
        return f"Exception - File Not Found"


    except Exception as e:
        print(f"Exception - {str(e)}")
        return f"Exception - {str(e)}"

app.mount("/", mcp.sse_app())

    