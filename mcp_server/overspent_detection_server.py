from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import pandas as pd
import os
from fastapi import FastAPI

app = FastAPI()
load_dotenv()

mcp = FastMCP(
    name="overspent MCP Server",
    host="127.0.0.1",
    port=8080,
)


file_path = os.path.join(os.path.dirname(__file__),"data","TNXData.csv")

@mcp.tool(name = "get_over_spent_data", description = "Get all withdrawal spent over a 100000 limit")
def get_over_spent_data():
    try:
        df = pd.read_csv(
        file_path, 
        parse_dates=['Date'], 
        dayfirst=True 
        )
        over_spent_df = df[df['Withdrawal'] > 100000]
        return over_spent_df.to_markdown(index=False)

    except FileNotFoundError:
        print(f"Exception - File Not Found")
        return f"Exception - File Not Found"


    except Exception as e:
        print(f"Exception - {str(e)}")
        return f"Exception - {str(e)}"

app.mount("/", mcp.sse_app())

    