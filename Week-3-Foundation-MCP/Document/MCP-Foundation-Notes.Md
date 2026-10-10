# MCP + LLM Agent — Architecture & Workflow Reference

---

## 1. Flow / Communication Steps (MCP Client–Server)

1. **User** submits prompt to server
2. **Tool Discovery** — Server needs to know what tools are available to send to LLM
3. **List Tools** — Server asks MCP client for the list of available tools
4. **MCP Communication** — MCP client sends `ListToolsRequest` to MCP server and receives `ListToolsResponse`
5. **LLM (Claude) Request** — Server sends (user prompt + available tools) to Claude
6. **Tool Use Decision Making** — Claude/LLM decides, depending on user query, whether it needs to call an MCP tool or not
7. **Tool Execution Request** — Based on above decision, server may ask MCP client to run the required tool (decided by Claude)
8. **External API Call** — MCP client sends `CallToolRequest` to MCP server, which makes further API call to actual external provider (e.g. GitHub API)
9. **Result Flow Back** — GitHub responds with repository data, which flows back through MCP server as `CallToolResult`
10. **Tool Result to Claude** — Server sends tool result back to Claude
11. **Final Response** — Claude formulates final response using MCP tool data + LLM knowledge
12. **User gets answer** — Server delivers response back to user

---

**MCP Tool Communication diagram:**

![MCP Communication](image.png)

![MCP Communication](image-1.png)

**MCP Server Primitives:**

![MCP Server Primitives](image-2.png)

![alt text](image-3.png)

## 2. System Architecture

```mermaid
graph TB
    subgraph YourProcess["Your Python Process (main.py)"]
        CLI["CliApp<br/>core/cli.py<br/>PromptSession REPL"]
        CHAT["CliChat<br/>core/cli_chat.py<br/>_process_query()"]
        CHATBASE["Chat<br/>core/chat.py<br/>run() loop"]
        CLAUDE["Claude<br/>core/claude.py<br/>client.messages.create()"]
        TOOLMGR["ToolManager<br/>core/tools.py<br/>execute_tool_requests()"]
        MCPCLIENT["MCPClient<br/>mcp_client.py<br/>ClientSession"]
    end

    subgraph MCPProcess["Separate OS Process stdio"]
        MCPSERVER["mcp_server.py<br/>FastMCP DocumentMCP<br/>docs in-memory dict"]
    end

    subgraph AnthropicAPI["Anthropic Cloud API"]
        LLM["Claude LLM Model<br/>claude-3-x or claude-4-x"]
    end

    CLI -->|user_input| CHAT
    CHAT -->|inherits| CHATBASE
    CHAT -->|preprocess: @mentions, /commands| MCPCLIENT
    CHATBASE -->|messages + tool_schemas| CLAUDE
    CLAUDE -->|HTTP POST /messages| LLM
    LLM -->|response: text or tool_use| CLAUDE
    CLAUDE -->|Message object| CHATBASE
    CHATBASE -->|if tool_use| TOOLMGR
    TOOLMGR -->|call_tool()| MCPCLIENT
    MCPCLIENT <-->|stdin/stdout JSON-RPC| MCPSERVER
```

---

## 3. Startup Initialization Sequence

```mermaid
sequenceDiagram
    participant main as main.py
    participant mcp as MCPClient
    participant srv as mcp_server.py
    participant cli as CliApp

    main->>mcp: MCPClient(command, args).__aenter__()
    mcp->>srv: spawn subprocess (python mcp_server.py)
    mcp->>srv: initialize() handshake
    srv-->>mcp: capabilities confirmed

    main->>cli: CliApp(chat)
    cli->>mcp: read_resource("docs://documents")
    mcp->>srv: JSON-RPC read_resource request
    srv-->>mcp: ["report.pdf","plan.md", ...]
    cli->>cli: update_resources() → autocomplete list

    cli->>mcp: list_prompts()
    mcp->>srv: JSON-RPC list_prompts
    srv-->>mcp: [Prompt(name="format",...)]
    cli->>cli: update_prompts() → slash autocomplete
```

---

## 4. MCP Tool Communication (Generic Pattern)

```mermaid
sequenceDiagram
    participant User
    participant Server as Your App (Agent)
    participant Claude as Claude LLM
    participant MCPClient as MCP Client
    participant MCPServer as MCP Server
    participant External as External API (e.g. GitHub)

    User->>Server: submit prompt
    Server->>MCPClient: list_tools()
    MCPClient->>MCPServer: ListToolsRequest
    MCPServer-->>MCPClient: ListToolsResponse [tool schemas]
    MCPClient-->>Server: tool list

    Server->>Claude: user prompt + tool schemas
    Claude-->>Server: tool_use decision (CallToolRequest)

    alt Claude decides to use a tool
        Server->>MCPClient: call_tool(name, input)
        MCPClient->>MCPServer: CallToolRequest
        MCPServer->>External: API call (e.g. GitHub REST)
        External-->>MCPServer: API response
        MCPServer-->>MCPClient: CallToolResult
        MCPClient-->>Server: tool result
        Server->>Claude: tool result
        Claude-->>Server: final text response
    else Claude does not need a tool
        Claude-->>Server: direct text response
    end

    Server-->>User: final answer
```

---

## 5. Scenario: Plain Query — "what is the weather in pune today?"

```mermaid
sequenceDiagram
    participant user as User
    participant cli as CliApp
    participant chat as CliChat
    participant mcp as MCPClient
    participant claude as Claude.chat()
    participant llm as Anthropic LLM

    user->>cli: "what is the weather in pune today?"
    cli->>chat: agent.run(query)
    chat->>chat: _process_command() → no "/" → False
    chat->>chat: _extract_resources() → no "@" → empty context
    Note over chat,claude: NO MCP call at this stage
    chat->>chat: wrap query in plain prompt template
    chat->>claude: chat(messages, tools=[read_doc_contents, edit_doc_contents])
    claude->>llm: POST /messages with tool schemas
    Note over llm: LLM sees 2 doc tools — neither relevant<br/>to weather. No weather tool exists.<br/>Claude has no internet access.<br/>It answers from training knowledge only.
    llm-->>claude: stop_reason="end_turn", text="I don't have real-time..."
    claude-->>chat: Message (no tool_use)
    chat-->>cli: final_text_response
    cli-->>user: prints response
```

> **Why Claude cannot "just fetch weather":** Claude is a stateless language model. It generates text from training data. It has **no internet access**. The only way it can fetch live data is if your code provides a tool for it (e.g. a `get_weather(city)` MCP tool). Your server only has doc tools, so Claude falls back to training knowledge.

---

## 6. Scenario: Resource Mention — "what is there in this @report.pdf"

```mermaid
sequenceDiagram
    participant user as User
    participant chat as CliChat
    participant mcp as MCPClient
    participant srv as mcp_server.py
    participant llm as Anthropic LLM

    user->>chat: "what is there in this @report.pdf"
    chat->>chat: _process_command() → no "/" → False
    chat->>chat: _extract_resources() → sees "@report.pdf"

    chat->>mcp: read_resource("docs://documents")
    mcp->>srv: JSON-RPC read_resource docs://documents
    srv-->>mcp: ["deposition.md","report.pdf","plan.md",...]

    chat->>mcp: read_resource("docs://document/report.pdf")
    mcp->>srv: JSON-RPC read_resource docs://document/report.pdf
    srv-->>mcp: "The report details the state of a 20m condenser tower."

    chat->>chat: build prompt with injected document XML block
    Note over llm: Document content already inside<br/>the user message. Claude reads it<br/>directly — no tool_use emitted.
    chat->>llm: POST /messages (doc content inside prompt)
    llm-->>chat: stop_reason="end_turn", text="The report.pdf contains..."
    chat-->>user: final answer
```

> **Key difference vs weather:** The app itself (not Claude) makes the MCP resource call and injects content before Claude is even asked. Claude just reads what your code prepared.

---

## 7. Scenario: Tool Call — Claude decides to use a tool

Triggered when user asks without `@` prefix, e.g. *"read financials.docx"*

```mermaid
sequenceDiagram
    participant user as User
    participant chat as CliChat
    participant chatbase as Chat run() loop
    participant toolmgr as ToolManager
    participant mcp as MCPClient
    participant srv as mcp_server.py
    participant llm as Anthropic LLM

    user->>chat: "read financials.docx"
    chat->>chat: _extract_resources() → no "@" → empty context
    chatbase->>llm: POST /messages with tools=[read_doc_contents, edit_doc_contents]
    Note over llm: LLM sees tool description:<br/>"Reads the contents of a document given its ID"<br/>Decides to call it.
    llm-->>chatbase: stop_reason=tool_use
    Note over llm,chatbase: name=read_doc_contents, input={doc_id:financials.docx}

    chatbase->>toolmgr: execute_tool_requests(clients, response)
    toolmgr->>toolmgr: find client with "read_doc_contents"
    toolmgr->>mcp: call_tool("read_doc_contents", {doc_id:"financials.docx"})
    mcp->>srv: JSON-RPC tools/call
    srv-->>mcp: "These financials outline the project's budget..."
    mcp-->>toolmgr: CallToolResult

    chatbase->>chatbase: append tool_result to messages
    chatbase->>llm: POST /messages (loop iteration 2 with tool result)
    llm-->>chatbase: stop_reason="end_turn", text="The financials say..."
    chatbase-->>user: final answer
```

---

## 8. Scenario: Slash Command (Prompt Workflow) — "/format report.pdf"

```mermaid
sequenceDiagram
    participant user as User
    participant chat as CliChat
    participant mcp as MCPClient
    participant srv as mcp_server.py
    participant llm as Anthropic LLM

    user->>chat: "/format report.pdf"
    chat->>chat: _process_command() → starts with "/" → True
    Note over chat: command="format", doc_id="report.pdf"
    chat->>mcp: get_prompt("format", {doc_id:"report.pdf"})
    mcp->>srv: JSON-RPC prompts/get
    srv-->>mcp: [UserMessage("reformat doc report.pdf... use edit_document tool")]

    chat->>chat: convert_prompt_messages_to_message_params()
    chat->>chat: append converted messages to self.messages
    Note over chat: _process_command returns True<br/>No wrapping template added.

    chat->>llm: POST /messages (MCP prompt text IS the message)
    Note over llm: Prompt tells Claude to use<br/>edit_document tool. Claude emits tool_use.
    llm-->>chat: tool_use: edit_doc_contents ...
    Note over chat: → tool loop continues as Scenario 7
```

---

## 9. Decision Tree: Does MCP get called?

```mermaid
flowchart TD
    A[User types input] --> B{starts with /}
    B -->|Yes| C["_process_command<br/>Fetches MCP Prompt template<br/>mcp_client.get_prompt"]
    B -->|No| D{contains @mention}
    D -->|Yes| E["_extract_resources<br/>Fetches MCP Resource<br/>mcp_client.read_resource"]
    D -->|No| F[No MCP call at all]

    C --> G[Inject prompt messages into conversation]
    E --> H[Inject document content into user message]
    F --> I[Wrap query in plain template with empty context]

    G --> J["Claude API call<br/>with MCP tool schemas always included"]
    H --> J
    I --> J

    J --> K{"Claude response<br/>stop_reason?"}
    K -->|end_turn| L[Return text to user]
    K -->|tool_use| M["ToolManager<br/>executes tool via MCPClient<br/>call_tool"]
    M --> N[Append tool_result to messages]
    N --> J
```

---

## 10. Quick Reference: MCP Feature vs Code Path

| User Input Pattern | Who makes MCP call | When | MCP Feature Used | Code Location |
|---|---|---|---|---|
| `@doc` mention | App code (preemptive) | Before Claude | Resource (`read_resource`) | `cli_chat.py _extract_resources()` |
| `/command doc` | App code (preemptive) | Before Claude | Prompt template (`get_prompt`) | `cli_chat.py _process_command()` |
| Plain query | Nobody preemptive | — | Nothing | — |
| Claude needs data | Claude decides | During tool loop | Tool call (`call_tool`) | `tools.py execute_tool_requests()` |
| Startup init | App code | Once at boot | Resource + Prompt list | `cli.py initialize()` |

---

## 11. Where Prompt Caching Would Be Added

```mermaid
graph LR
    subgraph claude_py["core/claude.py - chat() method"]
        P1["params = model, max_tokens, messages"]
        P2["if tools: add tool schemas"]
        P3["client.messages.create - actual HTTP call"]
    end

    P1 -->|ADD cache_control block| CACHE1["system param with<br/>cache_control: ephemeral<br/>for stable instructions"]
    P2 -->|ADD cache_control on tools| CACHE2["tool definitions with<br/>cache_control: ephemeral<br/>tool list rarely changes"]
    P1 -->|ADD on large context messages| CACHE3["User message with<br/>cache_control: ephemeral<br/>when doc content injected"]
```

**The only file that touches the Anthropic API is `core/claude.py` at `client.messages.create(**params)`.  
Everything else in the codebase feeds data into `params` before that single call.**
