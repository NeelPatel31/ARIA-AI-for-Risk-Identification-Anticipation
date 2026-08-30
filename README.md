# ARIA — AI for Risk Identification & Anticipation

ARIA is an agentic supply-chain risk assistant. It orchestrates specialist AI agents to map a product's supply chain, surface relevant disruptions, quantify risk with a deterministic scoring tool, and propose mitigations — all surfaced through a chat UI backed by a FastAPI streaming server and a Chroma vector store.

## Project Structure

```
.
├── app/                        # Backend (FastAPI + LangGraph)
│   ├── agent_registry/         # Agent definitions and tools
│   │   ├── agent.py            # ARIA Coordinator agent (main agent) assembly
│   │   ├── prompts.py          # System prompts for the coordinator and specialists
│   │   ├── state.py            # Shared agent state (todos, reports, presented files)
│   │   ├── subagents.py        # Specialist agent configurations
│   │   ├── llms.py             # Azure OpenAI chat model
│   │   ├── checkpointers.py    # In-memory session checkpointer
│   │   ├── middlewares.py      # Summarization + debug/event-streaming middleware
│   │   └── tools/              # Tools: task delegation, todos, reports, search, risk eval
│   ├── apis/                   # HTTP layer
│   │   ├── routes/             # /stream-chat, /health, training, retrieval, query endpoints
│   │   ├── controllers/        # Request/response handlers (SSE, training, RAG)
│   │   └── validation_models/  # Pydantic request models
│   ├── business_logic/         # Core services
│   │   ├── chat.py             # Agent execution streamed as SSE events
│   │   ├── rag.py              # GraphRetriever-based product/news retrieval
│   │   └── training.py         # Markdown ingestion, splitting, embedding, Chroma indexing
│   ├── config/                 # Settings loaded from .env (pydantic-settings)
│   └── utils/                  # Logging and path constants
├── streamlit_app/              # Frontend (Streamlit chat UI)
│   ├── app.py                  # Chat app, session handling, streaming loop
│   ├── api_client.py           # SSE client for /stream-chat
│   └── render.py               # Message, tool-call, and report rendering (+ report download)
├── data/
│   ├── products/*.md           # Product supply-chain knowledge documents
│   ├── news/*.md               # Disruption / news event documents
│   └── chroma_db/              # Persisted vector store
├── main.py                     # Uvicorn entrypoint
└── pyproject.toml              # Project metadata and dependencies
```

## Agents and Capabilities

The coordinator (**ARIA Coordinator**) is the main agent talking to the user. It plans work, delegates to specialists via a `task` tool, persists outputs as named reports, and scores risks.

| Agent | Role | Tools |
|---|---|---|
| **ARIA Coordinator** (main) | Orchestrates the request, quantifies risk, presents the final artifact | `task`, `write_todos`/`read_todos`, `save_report`/`read_report`/`present_report`, `assess_risks` |
| **Product Cartographer** | Compiles a structured `product_dossier` (Demand, Sourcing, Manufacturing, Delivery) with the entity list for disruption linking | `knowledge_search`, `write_todos`/`read_todos` |
| **Disruption Scout** | Compiles a `news_brief` of events tied to the product's entities and stages | `news_search`, `read_report`, `write_todos`/`read_todos` |
| **Mitigation Strategist** | Traces scored risks to root causes and proposes cited, actionable mitigations | `read_report`, `knowledge_search`, `news_search`, `write_todos`/`read_todos` |

### Risk scoring

Risk analysis follows a rubric. The coordinator derives **Severity (S)**, **Exposure (E)**, and **Fragility (F)** (each 1–5) from gathered evidence, then calls the `assess_risks` tool, which computes deterministically:

- Per-risk score = `round((S × E × F) / 12.5)`, clamped to 1–10
- Bands: 1–3 Low · 4–6 Moderate · 7–8 High · 9–10 Critical
- **Cumulative risk** = RMS of all individual scores (combines every score while weighting higher risks more), clamped and banded the same way

Canonical report names: `product_dossier`, `news_brief`, `risk_assessment`, `mitigation_plan`.

## Training Flow

The vector store is seeded from raw markdown documents.

- **Product data** (`data/products/*.md`): each file has YAML frontmatter (`product`, `entities`) and stage sections (`#`, `##`). Training parses the frontmatter, splits on headers, shreds the chunks, embeds them, and rebuilds the `product_chunks` Chroma collection.
- **News data** (`data/news/*.md`): each file has YAML frontmatter (`event_id`, `published_date`, `entities`, `event_type`) and a body with summary/impact. Training builds one document per file, embeds it, and rebuilds the `news_chunks` Chroma collection.

Training can be triggered via the API:

```
POST /train-products    # Rebuild the product knowledge collection from data/products/*.md
POST /train-news        # Rebuild the news collection from data/news/*.md
```

Additional ingestion endpoints for single documents (also updates the live retrievers):

```
POST /insert-product    # body: { "filename": "my-product.md", "markdown": "..." }
POST /insert-news       # body: { "filename": "news-xxxx.md", "markdown": "..." }
```

## Running the Project

Prerequisites: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```
# 1. Install dependencies (uv creates .venv automatically)
uv sync

# 2. Configure environment
copy .env.example .env          # Windows
cp .env.example .env            # macOS / Linux
# Fill in the values in .env

# 3. Start the API server
uv run python main.py           # serves http://localhost:4000

# 4. (Optional) Seed the vector store
#    With the server running:
curl -X POST http://localhost:4000/train-products
curl -X POST http://localhost:4000/train-news

# 5. Start the Streamlit chat UI (separate terminal)
uv run streamlit run streamlit_app/app.py
```

Open the chat UI in the browser, and the API docs at `http://localhost:4000/docs`.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/stream-chat` | SSE stream of the agent run (body: `session_id`, `user_query`) |
| `POST` | `/train-products` | Train product knowledge collection |
| `POST` | `/train-news` | Train news collection |
| `POST` | `/insert-product` | Insert a single product document |
| `POST` | `/insert-news` | Insert a single news document |
| `POST` | `/retrieve` | Retrieve product chunks for a query |
| `POST` | `/retrieve-news` | Retrieve news chunks for a query |
| `POST` | `/query` | RAG answer from product data |
| `POST` | `/query-news` | RAG answer from news data |