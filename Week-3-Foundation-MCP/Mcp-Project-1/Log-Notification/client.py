from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)

async def logging_callback(params: LoggingMessageNotificationParams):
    print(params.data)

async def print_progress_callback(progress: float, total: float | None, message: str | None):
    if total is not None:
        percentage = (progress / total) * 100
        print(f"Progress: {progress}/{total} ({percentage:.1f}%)")
    else:
        print(f"Progress: {progress} (Total unknown)")

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, logging_callback=logging_callback
        ) as session:
            await session.initialize()

            result = await session.call_tool(
                name="add",
                arguments={"a": 5, "b": 10},
                progress_callback=print_progress_callback
            )
            # Prefer structured content when present, then fall back to text content.
            value = None
            if getattr(result, "structuredContent", None) and "result" in result.structuredContent:
                value = result.structuredContent["result"]
            elif getattr(result, "content", None):
                first_item = result.content[0]
                value = getattr(first_item, "text", first_item)

            print(f"Result: {value}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())