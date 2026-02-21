---
name: enhance-project
description: Researches and recommends the best open-source APIs, libraries, and GitHub repositories to enhance, upgrade, and optimize the WebAI-to-API project. Focuses on tools that improve current features, add powerful new capabilities, and enable feature chaining for super-powered workflows.
---

# Enhance Project - Third-Party Integration Agent Skill

## Instructions

This skill researches and recommends the best open-source APIs, libraries, and GitHub repos to add to the WebAI-to-API project. The goal is to **deeply enhance existing features** before adding new ones, while also prioritizing tools that can be **chained together** for super-powered workflows.

## Current Project Analysis

The WebAI-to-API project is a FastAPI-based server that:
- Exposes browser-based LLMs (Google Gemini) as local API endpoints
- Supports gpt4free for multiple LLM providers (ChatGPT, Claude, DeepSeek, etc.)
- Has session management for stateful conversations
- Uses browser cookies for authentication
- Already includes: langchain, haystack-ai, celery, redis, openai, playwright

**Priority Order:**
1. Enhance current features (caching, session management, rate limiting, monitoring, auth)
2. Add complementary features that supercharge existing ones
3. Enable tool chaining for advanced workflows

---

## Top 10 Recommended Open-Source Libraries & APIs

### 1. LiteLLM - Unified LLM Gateway (⭐27k+)
**Category:** LLM Abstraction / Gateway  
**Website:** https://github.com/BerriAI/litellm

**What it does:**
- Unified API for 100+ LLMs (OpenAI, Anthropic, Google, Azure, Ollama, etc.)
- Standardized OpenAI-compatible API across all providers
- Automatic retries, fallbacks, and load balancing
- Built-in token counting and cost tracking

**Why it enhances the project:**
- **Chaining Bonus:** Works with existing langchain + haystack-ai integration
- Provides automatic provider fallbacks when Gemini fails
- Unified logging/monitoring across all LLM providers
- Simplifies multi-provider architecture

**Installation:**
```bash
pip install litellm
```

**Example usage with WebAI-to-API:**
```python
# In src/app/services/litellm_client.py
import os
from litellm import acompletion

async def route_to_provider(model: str, messages: list):
    # Fallback chain: Gemini -> OpenAI -> Anthropic -> Ollama
    response = await acompletion(
        model="gemini/gemini-pro",  # or "openai/gpt-4", "anthropic/claude-3"
        messages=messages,
        fallbacks=[{"model": "openai/gpt-4"}, {"model": "anthropic/claude-3-opus"}]
    )
    return response
```

**Bonus - Feature Chaining:**
```
LiteLLM + langchain = Multi-provider agent chains
LiteLLM + haystack = Unified RAG with any embedding model
LiteLLM + celery = Async multi-provider queue processing
```

---

### 2. Qdrant - Vector Database (⭐17k+)
**Category:** Semantic Search / RAG  
**Website:** https://github.com/qdrant/qdrant

**What it does:**
- High-performance vector similarity search engine
- Full-text + semantic hybrid search
- FastAPI-native with Python client
- Cloud-native with on-premise option

**Why it enhances the project:**
- **Upgrades existing:** Leverages existing haystack-ai dependency
- Enables conversation memory with semantic retrieval
- Build knowledge-base augmented responses
- Fast filtering and pagination

**Installation:**
```bash
pip install qdrant-client
```

**Example - Semantic Session Memory:**
```python
# In src/app/services/semantic_memory.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class SemanticSessionMemory:
    def __init__(self):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = "session_memories"
    
    async def store_session(self, session_id: str, messages: list):
        # Store conversation embeddings for semantic retrieval
        vector = await self.embed_messages(messages)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": session_id,
                "vector": vector,
                "payload": {"messages": messages}
            }]
        )
    
    async def get_relevant_context(self, query: str, session_id: str):
        query_vector = await self.embed_messages([{"role": "user", "content": query}])
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            filter={"must": [{"key": "session_id", "value": session_id}]},
            limit=5
        )
        return [r.payload["messages"] for r in results]
```

**Bonus - Feature Chaining:**
```
Qdrant + haystack = Production-grade RAG pipeline
Qdrant + LiteLLM = Semantic caching with vector similarity
Qdrant + langchain = Long-term memory for agents
```

---

### 3. Redis OM Python (⭐8k+)
**Category:** In-Memory Cache / Session Store  
**Website:** https://github.com/redis/redis-om-python

**What it does:**
- Object mapping for Redis
- Built-in JSON, search, and vector capabilities
- Ultra-fast session management
- Pub/sub for real-time features

**Why it enhances the project:**
- **Upgrades existing:** Supercharges current redis + celery setup
- Replaces in-memory session with distributed sessions
- Enables pub/sub for multi-instance deployments
- Built-in rate limiting with Redis

**Installation:**
```bash
pip install redis-om
```

**Example - Distributed Session Management:**
```python
# In src/app/services/redis_session.py
from redis_om import HashModel, Field
from datetime import datetime

class ChatSession(HashModel):
    session_id: str = Field(index=True)
    user_id: str = Field(index=True)
    messages: list = Field(default=list)
    model: str
    created_at: datetime = Field(default=datetime.utcnow)
    last_active: datetime = Field(default=datetime.utcnow)

class RedisSessionManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis_url
    
    async def create_session(self, user_id: str, model: str) -> str:
        session = ChatSession(
            session_id=generate_uuid(),
            user_id=user_id,
            messages=[],
            model=model
        )
        return session.pk
    
    async def append_message(self, session_pk: str, role: str, content: str):
        session = ChatSession.get(session_pk)
        session.messages.append({"role": role, "content": content})
        session.last_active = datetime.utcnow()
        session.save()
    
    async def get_session_history(self, session_pk: str) -> list:
        session = ChatSession.get(session_pk)
        return session.messages

# Rate limiting example
async def rate_limit_key(key: str, limit: int = 100, window: int = 60):
    from redis import Redis
    r = Redis()
    current = r.incr(key)
    if current == 1:
        r.expire(key, window)
    return current <= limit
```

**Bonus - Feature Chaining:**
```
Redis + celery = Distributed task queue with result caching
Redis + Qdrant = Hybrid cache: vectors + hot data
Redis + LiteLLM = Request caching + rate limiting
```

---

### 4. FastAPI Users (⭐4k+)
**Category:** Authentication / User Management  
**Website:** https://github.com/fastapi-users/fastapi-users

**What it does:**
- Complete user authentication system
- OAuth providers (Google, GitHub, etc.)
- JWT and cookie authentication
- Database adapters for SQLAlchemy, Ormar, MongoDB

**Why it enhances the project:**
- **Upgrades existing:** Adds proper auth to public API endpoints
- Multi-provider OAuth for easy Gemini login
- Role-based access control (RBAC)
- Secure session management

**Installation:**
```bash
pip install fastapi-users[sqlite]  # or postgresql, mysql, mongodb
```

**Example - Adding Authentication:**
```python
# In src/app/auth.py
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

# Configure JWT auth
auth_backends = [
    JWTAuthentication(secret="your-secret-key", lifetime_seconds=3600)
]

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backends],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

# Add to endpoints
@router.post("/protected-chat")
async def protected_chat(
    request: OpenAIChatRequest,
    user: User = Depends(fastapi_users.current_user())
):
    # User is authenticated
    return await chat_completions(request)
```

**Bonus - Feature Chaining:**
```
FastAPI Users + Redis = Fast auth with session storage
FastAPI Users + LiteLLM = Per-user rate limiting
FastAPI Users + Qdrant = Per-user knowledge bases
```

---

### 5. Logfire / OpenTelemetry - Observability (⭐2k+/Trending)
**Category:** Monitoring / Observability  
**Website:** https://github.com/pydantic/logfire

**What it does:**
- Python-native observability
- Automatic tracing for FastAPI/Starlette
- Metrics, logs, and spans in one dashboard
- OpenTelemetry compatible

**Why it enhances the project:**
- **Upgrades existing:** Replace basic logging with full observability
- Track LLM request/response latency
- Monitor token usage and costs
- Error tracking and debugging

**Installation:**
```bash
pip install logfire
```

**Example - Observability:**
```python
# In src/app/main.py
import logfire

# Configure
logfire.configure(service_name="webai-to-api")

# Instrument FastAPI
logfire.instrument_fastapi(app)

# Custom spans for LLM calls
@router.post("/v1/chat/completions")
async def chat_completions(request: OpenAIChatRequest):
    with logfire.span("LLM request", model=request.model):
        start_time = time.time()
        try:
            response = await gemini_client.generate_content(...)
            logfire.info(
                "LLM response",
                latency_ms=(time.time() - start_time) * 1000,
                tokens=response.usage.total_tokens
            )
            return response
        except Exception as e:
            logfire.error("LLM error", error=str(e))
            raise
```

**Bonus - Feature Chaining:**
```
Logfire + LiteLLM = Multi-provider cost tracking
Logfire + Redis = Cache hit/miss monitoring
Logfire + celery = Task queue observability
```

---

### 6. Textual - TUI Dashboard (⭐10k+)
**Category:** CLI Dashboard / Monitoring  
**Website:** https://github.com/Textualize/textual

**What it does:**
- Python TUI framework (like React for terminals)
- Live data dashboards
- Rich terminal UIs
- Keyboard-driven interfaces

**Why it enhances the project:**
- **Adds new:** Live monitoring dashboard in terminal
- Real-time API statistics
- Server control panel
- Log viewer with filtering

**Installation:**
```bash
pip install textual
```

**Example - Admin Dashboard:**
```python
# In src/app/ui/dashboard.py
from textual.app import App
from textual.widgets import Static, DataTable
from textual.reactive import reactive

class WebAIDashboard(App):
    stats = reactive({"requests": 0, "active_sessions": 0, "errors": 0})
    
    def compose(self):
        yield Static("WebAI-to-API Dashboard", id="title")
        yield DataTable(id="stats")
    
    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Metric", "Value")
        table.add_row("Total Requests", str(self.stats["requests"]))
        table.add_row("Active Sessions", str(self.stats["active_sessions"]))
        table.add_row("Errors", str(self.stats["errors"]))
    
    async def watch_stats(self, stats):
        # Update in real-time via WebSocket
        table = self.query_one(DataTable)
        # Update rows...

if __name__ == "__main__":
    app = WebAIDashboard()
    app.run()
```

**Bonus - Feature Chaining:**
```
Textual + Redis = Real-time session monitoring
Textual + Logfire = Live error tracking
Textual + celery = Task queue status dashboard
```

---

### 7. MMS Engine - Audio/STT/TTS (⭐50k+)
**Category:** Audio Processing  
**Website:** https://github.com/f一面/Whisper, https://github.com/coqui-ai/TTS

**What it does:**
- Whisper: Speech-to-text (STT) with 99+ languages
- Coqui TTS: High-quality text-to-speech
- Audio transcription for voice interfaces
- Voice cloning capabilities

**Why it enhances the project:**
- **Adds new:** Voice input/output for chat endpoints
- Transcribe audio files for LLM processing
- Generate speech from LLM responses
- Build voice assistants

**Installation:**
```bash
pip install faster-whisper  # Optimized Whisper
pip install coqui-tts       # TTS
```

**Example - Voice Chat Endpoint:**
```python
# In src/app/endpoints/voice.py
from faster_whisper import WhisperModel
from TTS.api import TTS

# Initialize models
whisper = WhisperModel("small", device="cpu", compute_type="int8")
tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")

@router.post("/v1/audio/transcriptions")
async def transcribe_audio(file: UploadFile):
    # Save uploaded audio
    audio_path = f"/tmp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    
    # Transcribe
    segments, info = whisper.transcribe(audio_path)
    transcription = " ".join([seg.text for seg in segments])
    
    # Get LLM response
    llm_response = await chat_completions(transcription)
    
    # Generate speech
    tts.tts_to_file(text=llm_response, file_path="/tmp/response.wav")
    
    return FileResponse("/tmp/response.wav", media_type="audio/wav")
```

**Bonus - Feature Chaining:**
```
Whisper + LiteLLM = Voice-powered AI assistant
Coqui TTS + WebAI-to-API = Voice output for any LLM
Whisper + Qdrant = Voice search in knowledge bases
```

---

### 8. Meta-Llama-Index (LlamaIndex) - Advanced RAG (⭐35k+)
**Category:** Data Framework / RAG  
**Website:** https://github.com/run-llama/llama_index

**What it does:**
- Advanced RAG with 200+ data connectors
- Sophisticated indexing strategies
- Multi-modal support
- Agentic data retrieval

**Why it enhances the project:**
- **Upgrades existing:** Enhances haystack-ai integration
- Better than haystack for complex RAG
- Works with LiteLLM for unified provider access
- Advanced query understanding

**Installation:**
```bash
pip install llama-index
```

**Example - Advanced RAG Pipeline:**
```python
# In src/app/services/rag_pipeline.py
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores import QdrantVectorStore
from llama_index.llms import LiteLLM

# Connect to Qdrant
vector_store = QdrantVectorStore(client=qdrant_client, collection_name="docs")

# Create index with LiteLLM
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    llm=LiteLLM(model="gemini/gemini-pro")
)

# Query engine with reranking
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[CohereRerank()]
)

@router.post("/rag/ask")
async def ask_with_context(request: RAGRequest):
    response = query_engine.query(request.question)
    return {"answer": response.response, "sources": response.source_nodes}
```

**Bonus - Feature Chaining:**
```
LlamaIndex + Qdrant = Production RAG
LlamaIndex + LiteLLM = Multi-provider RAG
LlamaIndex + Redis = Cached query responses
```

---

### 9. AutoGen - Multi-Agent Framework (⭐35k+)
**Category:** Multi-Agent Orchestration  
**Website:** https://github.com/microsoft/autogen

**What it does:**
- Build LLM agent teams
- Automated agent chat
- Tool use and code execution
- Customizable agent roles

**Why it enhances the project:**
- **Adds new:** Multi-agent workflows
- Collaborative AI problem solving
- Specialized agents (researcher, coder, reviewer)
- Tool chaining orchestration

**Installation:**
```python
pip install pyautogen
```

**Example - Agent Team:**
```python
# In src/app/agents/research_team.py
from autogen import ConversableAgent, GroupChat, GroupChatManager

# Define agents
researcher = ConversableAgent(
    name="Researcher",
    llm_config={"model": "gemini/gemini-pro"},
    system_message="You research topics thoroughly and cite sources."
)

coder = ConversableAgent(
    name="Coder",
    llm_config={"model": "openai/gpt-4"},
    system_message="You write code based on research findings."
)

reviewer = ConversableAgent(
    name="Reviewer",
    llm_config={"model": "anthropic/claude-3"},
    system_message="You review code for bugs and improvements."
)

# Create group chat
group_chat = GroupChat(
    agents=[researcher, coder, reviewer],
    messages=[],
    max_round=5
)

manager = GroupChatManager(groupchat=group_chat)

@router.post("/agents/team-research")
async def team_research(request: TeamRequest):
    # Initiate agent conversation
    chat_result = researcher.initiate_chat(
        manager,
        message=request.task
    )
    return {"final_response": chat_result.summary}
```

**Bonus - Feature Chaining:**
```
AutoGen + LiteLLM = Any-model agent team
AutoGen + Redis = Persistent agent memory
AutoGen + Qdrant = Knowledge-grounded agents
```

---

### 10. Temporal - Workflow Orchestration (⭐28k+)
**Category:** Workflow / Long-Running Tasks  
**Website:** https://github.com/temporalio/temporal

**What it does:**
- Durable execution for long-running workflows
- Activity retry with backoff
- Event sourcing and replay
- Microservice orchestration

**Why it enhances the project:**
- **Upgrades existing:** Replaces basic celery for complex workflows
- Long-running AI conversations with checkpointing
- Complex multi-step AI pipelines
- Automatic retry with human-in-the-loop

**Installation:**
```bash
pip install temporalio
```

**Example - AI Workflow:**
```python
# In src/app/workflows/ai_pipeline.py
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class AIPipelineWorkflow:
    @workflow.run
    async def run(self, user_request: dict) -> dict:
        # Step 1: Research (with retry)
        research = await workflow.execute_activity(
            research_topic,
            user_request["topic"],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy={"maximum_attempts": 3}
        )
        
        # Step 2: Generate response
        response = await workflow.execute_activity(
            generate_llm_response,
            {"context": research, "style": user_request.get("style")},
            start_to_close_timeout=timedelta(minutes=2)
        )
        
        # Step 3: Optional voice synthesis
        if user_request.get("voice"):
            audio = await workflow.execute_activity(
                synthesize_speech,
                response,
                start_to_close_timeout=timedelta(seconds=30)
            )
            return {"response": response, "audio": audio}
        
        return {"response": response}

# Activity implementations
@activity.defn
async def research_topic(topic: str) -> str:
    # Use LiteLLM to research
    return await liteLLM.arun("Research: " + topic)

@activity.defn
async def generate_llm_response(context: dict) -> str:
    return await gemini_client.generate_content(context["context"])

@activity.defn
async def synthesize_speech(text: str) -> bytes:
    return await tts.synthesize(text)
```

**Bonus - Feature Chaining:**
```
Temporal + LiteLLM = Durable multi-provider AI chains
Temporal + Redis = Workflow state persistence
Temporal + Qdrant = Knowledge-grounded workflows
```

---

## Priority Implementation Guide

### Phase 1: Enhance Current Features (High Priority)

| Feature | Recommended Library | Why |
|---------|---------------------|-----|
| Session Management | Redis OM | Distributed, persistent sessions |
| Authentication | FastAPI Users | Complete auth system |
| Observability | Logfire | Python-native monitoring |
| Rate Limiting | Redis + slowapi | Built-in Redis rate limiting |

### Phase 2: Add Complementary Features (Medium Priority)

| Feature | Recommended Library | Why |
|---------|---------------------|-----|
| Advanced RAG | LlamaIndex | Better than haystack for complex queries |
| Vector Search | Qdrant | Production-grade semantic search |
| Voice I/O | Whisper + Coqui TTS | Add voice capabilities |

### Phase 3: Enable Super-Feature Chaining (Advanced)

| Super Feature | Tool Chain |
|--------------|------------|
| Multi-Provider RAG | LiteLLM + Qdrant + LlamaIndex |
| Voice AI Assistant | Whisper + LiteLLM + Coqui TTS |
| Multi-Agent Research | AutoGen + LiteLLM + Redis |
| Durable AI Pipelines | Temporal + LiteLLM + Redis |

---

## Installation Helper

```bash
# Core enhancements (Phase 1)
pip install litellm redis-om logfire fastapi-users slowapi

# Advanced features (Phase 2)
pip install llama-index qdrant-client faster-whisper coqui-tts

# Super features (Phase 3)
pip install pyautogen temporalio

# Full install
pip install litellm redis-om logfire fastapi-users slowapi llama-index \
    qdrant-client faster-whisper coqui-tts pyautogen temporalio
```

---

## Environment Variables Template

Add to your `config.conf` or `.env`:

```ini
# LiteLLM
LITELLM_MASTER_KEY=your-key
LITELLM_DROP_PARAMS=True

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_URL=redis://localhost:6379

# Logfire
LOGFIRE_TOKEN=your-token

# Temporal
TEMPORAL_ADDRESS=localhost:7233
```

---

## Quick Win: Minimal Enhancement

Start with these 2 libraries for immediate impact:

1. **LiteLLM** - Add provider fallback in 10 lines
2. **Logfire** - Add observability in 5 lines

```python
# Minimal enhancement example
import litellm
import logfire

logfire.configure()

async def enhanced_chat(model, messages):
    with logfire.span("chat"):
        return await litellm.acompletion(
            model=model,
            messages=messages,
            fallbacks=[{"model": "openai/gpt-4"}]
        )
```

This gives you automatic fallbacks + full observability!
