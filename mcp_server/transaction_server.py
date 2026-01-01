from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import pandas as pd
import os
from fastapi import FastAPI

app = FastAPI()
load_dotenv()

mcp = FastMCP(
    name="Transaction MCP Server",
    host="127.0.0.1",
    port=8080,
)


file_path = os.path.join(os.path.dirname(__file__),"data","TNXData.csv")

@mcp.tool(name = "get_transacton_data", description = "Get all the Transaction Data")
def get_transacton_data():
    try:
        df = pd.read_csv(
        file_path, 
        parse_dates=['Date'], 
        dayfirst=True  # Set to True if your bank uses DD/MM/YYYY
        )
        return df.to_markdown(index=False)
    
    except FileNotFoundError:
        print(f"Exception - File Not Found")
        return f"Exception - File Not Found"


    except Exception as e:
        print(f"Exception - {str(e)}")
        return f"Exception - {str(e)}"

app.mount("/", mcp.sse_app())

    