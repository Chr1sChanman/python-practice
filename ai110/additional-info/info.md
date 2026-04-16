**MCP**
https://www.llamaindex.ai/
https://www.langchain.com/
https://platform.claude.com/docs/en/managed-agents/overview
https://www.docker.com/products/docker-desktop/ (Docker MCP Toolkit)
https://github.com/NVIDIA/NemoClaw
**AI Moderation**
https://aws.amazon.com/bedrock/guardrails/
https://developers.openai.com/api/docs/guides/moderation

---

# AI Pipeline Concepts

## Embedding

An embedding model converts data (text, images, etc.) into a dense numerical vector — an array of floats that encodes semantic meaning. Similar content produces similar vectors, enabling similarity-based search.

**Flow:**
```
"My dog is sick" → [embedding model] → [0.23, -0.87, 0.14, ...]
```

Common models: `text-embedding-3-small` (OpenAI), Sentence Transformers (open source), Cohere Embed.

---

## RAG (Retrieval-Augmented Generation)

RAG is a pattern where relevant external data is retrieved and injected into an LLM's context before generating a response. Prevents hallucination and grounds the model in real, up-to-date data.

**Flow:**
```
User query
  → Embed query
  → Search vector DB for similar chunks
  → Inject top chunks into LLM prompt
  → LLM generates grounded response
```

Without RAG, the LLM can only use its training data. With RAG, it can reference your documents, databases, or knowledge bases.

---

## Reranking

A reranking model takes the candidates returned by vector search and reorders them by true relevance to the query. It scores each query-document pair directly rather than comparing vectors.

**Why:** Vector search is fast but approximate. Reranking is slower but more precise.

**Flow:**
```
Query + [doc1, doc2, ... doc50]
  → Reranker scores each pair
  → Returns top 5 by relevance score
```

Common models: Cohere Rerank, Jina Reranker, Cross-encoders (Sentence Transformers).

---

## LlamaIndex (Managed Agents / RAG Framework)

LlamaIndex is a framework focused on connecting LLMs to external data. It abstracts the full RAG pipeline — ingestion, chunking, indexing, retrieval, and querying — so you don't have to wire it together manually.

**Key features:**
- Data connectors (PDFs, APIs, DBs, etc.)
- Built-in vector store integrations
- Query engines and chat engines
- Agent support with tool use

**Best for:** Data-heavy applications, document Q&A, structured RAG pipelines.

---

## LangChain (Agentic RAG / Orchestration Framework)

LangChain is a broader orchestration framework for building LLM applications. It supports chains (sequential steps), agents (LLM decides what tools to call), memory, and RAG — but with more flexibility and complexity than LlamaIndex.

**Key features:**
- Chains: compose LLM calls and tools in sequence
- Agents: LLM autonomously decides which tools to use and when
- Memory: persist state across conversation turns
- Broad ecosystem of integrations

**Best for:** Complex workflows, multi-step agents, applications that need dynamic decision-making.

---

## MCP (Model Context Protocol)

MCP is an open standard by Anthropic that defines how LLMs communicate with external tools and data sources. Instead of each framework inventing its own tool integration format, MCP provides a universal protocol — think of it as USB-C for AI tools.

An **MCP server** is a small process that exposes tools, resources, or prompts over the MCP protocol. The LLM (or agent framework) acts as the **MCP client**, connecting to one or more servers at runtime.

**Key concepts:**
- **Tools** — functions the LLM can call (e.g., search the web, query a DB)
- **Resources** — data the LLM can read (e.g., files, API responses)
- **Prompts** — reusable prompt templates served by the server

**How it works:**
```
LLM / Agent (MCP client)
  ↔ MCP protocol (JSON-RPC over stdio or HTTP/SSE)
  ↔ MCP server (exposes tools/resources)
  ↔ External service (DB, API, filesystem, etc.)
```

MCP servers can be written in any language. Claude Code, Claude Desktop, LlamaIndex, and LangChain all support MCP as clients.

---

## MCP Server Ecosystem

Every MCP server is purpose-built for a specific domain. The protocol is identical across all of them — only the tools exposed differ. The LLM doesn't care what a server does internally; it just sees a list of available tools and calls them the same way regardless.

| MCP Server | Domain | Example tools exposed |
|---|---|---|
| `mcp/playwright` | Browser automation | `navigate`, `click`, `screenshot`, `fill_form` |
| `mcp/filesystem` | Local files | `read_file`, `write_file`, `list_dir` |
| `mcp/postgres` | Databases | `query`, `describe_table` |
| `mcp/github` | GitHub | `create_issue`, `list_prs`, `get_file` |
| `mcp/slack` | Messaging | `send_message`, `list_channels` |
| `mcp/brave-search` | Web search | `search` |
| `mcp/asana` | Project management | `create_task`, `list_projects`, `update_task` |
| `mcp/jira` | Issue tracking | `create_issue`, `search_issues`, `update_status` |
| Custom server | Anything you build | Whatever you define |

**One protocol, infinite domain-specific servers.** Anyone can build and publish an MCP server for any service or tool — making the ecosystem extensible without changes to the LLM or agent framework.

---

## Docker MCP Toolkit

Docker MCP Toolkit packages MCP servers as Docker containers, solving the distribution and dependency problem — you pull and run an MCP server the same way you'd pull any Docker image.

**Why Docker for MCP:**
- No local dependency conflicts (each server runs in its own container)
- Easy to share and version MCP servers as images
- Sandboxed execution — the server can't touch your host system beyond what you allow
- Works with Docker Desktop's built-in MCP catalog

**Flow:**
```
Docker Desktop
  → pulls MCP server image (e.g. mcp/filesystem, mcp/postgres)
  → runs container, exposes MCP endpoint
  → Claude / agent connects as MCP client
  → LLM can now call tools provided by that server
```

**Example use cases:**
- `mcp/filesystem` — gives the LLM read/write access to a local folder
- `mcp/postgres` — lets the LLM query a PostgreSQL database
- `mcp/github` — lets the LLM interact with GitHub repos and issues
- Custom servers — package your own tools as an MCP image

Docker MCP integrates directly with Docker Desktop's GUI, making it accessible without manual server setup.

---

## Comparison Table

| Concept | What it does | Input | Output | Speed |
|---|---|---|---|---|
| Embedding model | Converts text to vector | Text | Float vector | Fast |
| Vector DB | Stores and searches vectors | Vectors | Top-N candidates | Fast |
| Reranker | Re-scores retrieved candidates | Query + doc pairs | Relevance scores | Slow |
| RAG | Grounds LLM in external data | Query + docs | LLM response | Medium |
| LlamaIndex | Manages RAG pipeline | Data sources + query | LLM response | Varies |
| LangChain | Orchestrates agents + chains | Prompt + tools | Agent output | Varies |
| MCP Server | Exposes tools/resources to LLM | LLM tool call | Tool result | Fast |
| Docker MCP | Packages MCP servers as containers | Docker image | Running MCP server | Fast |

| | LlamaIndex | LangChain | MCP |
|---|---|---|---|
| Primary focus | Data retrieval / RAG | Agent orchestration | Tool/resource protocol |
| Complexity | Lower (more opinionated) | Higher (more flexible) | Low (just a standard) |
| Best use case | Document Q&A, knowledge bases | Multi-step agents, dynamic workflows | Integrating external tools/services |
| RAG support | First-class | Supported but not primary focus | Via resource servers |
| Agent support | Yes (secondary) | Yes (primary) | Via tool servers |
| Language-agnostic | No (Python) | No (Python/JS) | Yes (any language) |

---

## How They Play Together

These concepts stack into a full pipeline:

```
Raw data (PDFs, DBs, APIs)
  → [LlamaIndex or LangChain] ingests and chunks
  → [Embedding model] converts chunks to vectors
  → [Vector DB] stores vectors
                        ↓
User query
  → [Embedding model] embeds query
  → [Vector DB] returns top-N candidates  ← RAG retrieval step
  → [Reranker] reorders candidates by relevance
  → Top-K chunks injected into LLM prompt
  → [LLM] generates grounded response
                        ↓
  (optional) [LangChain agent] decides to call another tool,
             search again, or return the answer
                        ↓
  (optional) [MCP client in agent] calls an MCP server tool
             (e.g. query live DB, fetch from API, read file)
             ← [Docker MCP] serves that tool from a container
```

- **Embeddings + Vector DB** = the retrieval backbone of RAG
- **Reranker** = optional quality filter between retrieval and generation
- **LlamaIndex** = handles the full RAG pipeline with minimal setup
- **LangChain** = wraps RAG (and other tools) into autonomous agents that can reason and act across multiple steps
- **MCP** = the standard protocol by which agents call external tools and read external resources — framework-agnostic
- **MCP Server Ecosystem** = domain-specific servers (Playwright, GitHub, Postgres, etc.) that plug into any MCP-compatible client
- **Docker MCP** = the distribution layer for MCP servers, making them portable and sandboxed via containers
