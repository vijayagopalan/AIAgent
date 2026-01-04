import asyncio
from client import MCPClient

async def main():
    mcp_client = MCPClient()
    await mcp_client.connect_to_server("http://127.0.0.1:8080/sse", "transaction")
    await mcp_client.connect_to_server("http://127.0.0.1:8000/sse", "overspent")
    query = "how many transaction happend on march month year 2021? "
    response =await  mcp_client.process_query(query)
    print(f"AI Assitant = {response}")
    await mcp_client.cleanup()

if __name__=="__main__":
    asyncio.run(main())

