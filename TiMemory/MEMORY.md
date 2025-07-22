# TiMemory System - Technical Design Documentation

This document provides detailed technical specifications for the TiMemory system, an intelligent memory management architecture built on TiDB's vector database capabilities.

## System Architecture

### Overview
TiMemory implements a sophisticated memory processing pipeline that extracts, consolidates, and retrieves conversational facts using vector similarity search and LLM-based reasoning. The system is designed for multi-user isolation, semantic similarity matching, and intelligent memory conflict resolution.

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    TiMem (Core Engine)                      │
├─────────────────────────────────────────────────────────────┤
│  Memory Processing Pipeline                                 │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐   │
│  │   Extract   │→│ Consolidate  │→│      Store          │   │
│  │  Memories   │ │   Memories   │ │    Memories         │   │
│  └─────────────┘ └──────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   OpenAI LLM    │   │   OpenAI LLM    │   │  TiDB Vector    │
│   (Extraction)  │   │ (Consolidation) │   │    Database     │
└─────────────────┘   └─────────────────┘   └─────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Structured JSON │   │ Memory Conflict │   │ Vector Storage  │
│   (Pydantic)    │   │   Resolution    │   │ + Cosine Sim.   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## Memory Processing Pipeline

### 1. Memory Extraction (`_extract_memories()`)

**Purpose**: Extract structured facts from user-AI conversation messages using LLM-based reasoning.

**Technical Implementation**:
```python
def _extract_memories(self, messages: List[Dict[str, str]]) -> MemoryResponse:
    response = self.llm.generate_response(
        instructions=self.fact_extraction_prompt,
        input=messages,
        text_format=MemoryResponse  # Pydantic model for structured output
    ).output_parsed
```

**Fact Extraction Prompt Engineering**:
- **Input**: Conversation history as role-based message array
- **Output**: Structured JSON with categorized memories
- **Categories**: `personal`, `preference`, `activity`, `plan`, `health`, `professional`, `miscellaneous`
- **Memory Attributes**: Each memory includes `type` and `status` fields

**Memory Structure**:
```json
{
  "id": "uuid4-generated",
  "user_id": "user_identifier",
  "content": "extracted_fact_text",
  "memory_attributes": {
    "type": "preference|personal|activity|plan|health|professional|miscellaneous",
    "status": "active"
  }
}
```

**Extraction Logic**:
- Filters conversational noise (greetings, acknowledgments)
- Identifies fact-bearing statements through conversational inference
- Handles complex cross-referential interactions and implicit responses
- Categorizes memories by semantic content
- Generates unique UUIDs for tracking

**Complex Interaction Inference**:
The extraction system excels at inferring memories from multi-turn conversations where users reference assistant responses or make implicit connections. The LLM analyzes the entire conversation context to extract facts that may not be explicitly stated but are clearly implied through the interaction flow.

**Example - Complex Cross-Referential Extraction**:
```json
[
  {"role": "user", "content": "I'm planning a vacation next month"},
  {"role": "assistant", "content": "That sounds exciting! Where are you thinking of going? Are you looking for something relaxing like a beach destination, or more adventurous like hiking in the mountains?"},
  {"role": "user", "content": "I love the ocean, but I'm not sure about the weather in March"},
  {"role": "assistant", "content": "March can be tricky for beach destinations depending on the hemisphere. If you're in the northern hemisphere, places like the Caribbean, Hawaii, or Southeast Asia tend to have great weather in March. Are you looking to stay domestic or go international?"},
  {"role": "user", "content": "International sounds amazing. I've never been to Thailand"},
  {"role": "assistant", "content": "Thailand in March is perfect! The weather is warm and dry, and it's actually one of the best times to visit. Are you more interested in the beaches in the south like Phuket and Koh Samui, or would you like to explore the cultural sites in Bangkok and northern Thailand?"},
  {"role": "user", "content": "Both actually! And yes, that place you mentioned first - the one that sounds like 'Poo-ket' - I've heard great things about it"},
  {"role": "assistant", "content": "Yes, Phuket! It's pronounced 'Poo-ket' and it's absolutely beautiful. You could do a great combination trip - start with a few days in Bangkok to see the temples and experience the city culture, then head south to Phuket for the beaches and maybe some island hopping."},
  {"role": "user", "content": "That's exactly what I want to do. And remember what you asked me earlier about adventurous vs relaxing? I definitely want both - the cultural exploration you mentioned and then beach time"}
]
```

**Extracted Memories from Complex Interaction**:
```json
{
  "memories": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "content": "Planning a vacation for March (next month)",
      "memory_attributes": {"type": "plan", "status": "active"}
    },
    {
      "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012", 
      "content": "Loves the ocean and beach destinations",
      "memory_attributes": {"type": "preference", "status": "active"}
    },
    {
      "id": "c3d4e5f6-g7h8-9012-cdef-345678901234",
      "content": "Prefers international travel over domestic",
      "memory_attributes": {"type": "preference", "status": "active"}
    },
    {
      "id": "d4e5f6g7-h8i9-0123-defg-456789012345",
      "content": "Has never been to Thailand but wants to visit",
      "memory_attributes": {"type": "plan", "status": "active"}
    },
    {
      "id": "e5f6g7h8-i9j0-1234-efgh-567890123456",
      "content": "Interested in visiting Phuket specifically",
      "memory_attributes": {"type": "plan", "status": "active"}
    },
    {
      "id": "f6g7h8i9-j0k1-2345-fghi-678901234567",
      "content": "Wants combination of cultural exploration and beach relaxation",
      "memory_attributes": {"type": "preference", "status": "active"}
    },
    {
      "id": "g7h8i9j0-k1l2-3456-ghij-789012345678",
      "content": "Interested in Bangkok temples and city culture",
      "memory_attributes": {"type": "preference", "status": "active"}
    }
  ]
}
```

**Key Inference Capabilities Demonstrated**:

1. **Cross-Turn Reference Resolution**: The user's statement "remember what you asked me earlier about adventurous vs relaxing?" requires the system to connect back to the assistant's question from several turns prior and understand the user's delayed response.

2. **Implicit Preference Extraction**: When the user says "I love the ocean," the system infers this as a beach destination preference, even though the user didn't explicitly state "I prefer beach destinations."

3. **Contextual Clarification Handling**: The user's reference to "that place you mentioned first - the one that sounds like 'Poo-ket'" demonstrates the system's ability to resolve unclear references to previous assistant responses.

4. **Multi-Modal Preference Synthesis**: The system combines the user's responses across multiple turns to understand they want "both cultural exploration and beach time," synthesizing this from separate statements about temples, city culture, and beaches.

5. **Temporal Context Understanding**: The system correctly identifies "next month" as referring to March based on the conversation context, creating a time-specific plan memory.

6. **Geographic Specificity**: Despite the user initially just saying "international," the system tracks the evolution of their interest to specific locations (Thailand, Phuket, Bangkok) mentioned through the conversation flow.

This advanced inference capability allows TiMemory to capture nuanced user preferences and plans that emerge organically through natural conversation, rather than only extracting explicitly stated facts.

### 2. Similarity Search (`_find_similar_memories()`)

**Purpose**: Identify existing memories that may conflict or relate to newly extracted memories.

**Technical Implementation**:
```python
def _find_similar_memories(self, new_memories: List[Memory], user_id: str) -> MemoryResponse:
    for memory in new_memories:
        embedding = self.embedder.embed(memory.content)  # 1536-dim vector
        similar_memories = self.tidbvector.search(embedding, user_id, limit=10)
```

**Vector Search Details**:
- **Embedding Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Similarity Metric**: Cosine distance via TiDB vector operations
- **User Isolation**: All queries filtered by `user_id` at database level
- **Result Limit**: Configurable similarity threshold (default: 10 results)

**Search Algorithm**:
1. Generate embedding vector for each new memory content
2. Execute TiDB vector similarity search with user isolation
3. Collect unique similar memories (deduplicated by ID)
4. Return aggregated similar memories for consolidation

### 3. Memory Consolidation (`_consolidate_memories()`)

**Purpose**: Intelligently merge new memories with existing ones to resolve conflicts and prevent duplication.

**Technical Implementation**:
```python
def _consolidate_memories(self, existing_memories: MemoryResponse, new_memories: List[Memory]) -> MemoryResponse:
    input_data = f'{{"existing_memories": {existing_dicts}, "new_memories": {new_dicts}}}'
    
    response = self.llm.generate_response(
        instructions=self.memory_consolidation_prompt,
        input=input_data,
        text_format=MemoryResponse
    ).output_parsed
```

**Consolidation Logic**:
- **Conflict Detection**: LLM identifies contradictory information
- **Status Management**: Marks outdated memories as `"status": "outdated"`
- **Update Strategy**: Returns both outdated and replacement memories
- **Preservation**: Maintains memory IDs and user associations

**Consolidation Rules**:
1. **No Conflict**: Return only new memories
2. **Direct Conflict**: Mark existing as outdated, return both versions
3. **Complementary**: Merge information while preserving specificity
4. **Temporal Updates**: Handle time-sensitive preference changes

### 4. Memory Storage (`_store_memories()`)

**Purpose**: Persist consolidated memories to TiDB with vector embeddings.

**Technical Implementation**:
```python
def _store_memories(self, consolidated_memories: List[Memory], user_id: str):
    for memory in consolidated_memories:
        embedding = self.embedder.embed(memory.content)
        status = memory.memory_attributes.status
        
        if status == 'outdated':
            self.tidbvector.update(id=memory.id, vector=embedding, ...)
        else:
            self.tidbvector.insert(id=memory.id, vector=embedding, ...)
```

**Storage Strategy**:
- **Insert**: New memories with `active` status
- **Update**: Existing memories marked as `outdated` (forgetting, not deletion)
- **Vector Storage**: Each memory stored with 1536-dimensional embedding
- **Indexing**: User ID indexing for efficient isolation queries

**Note on Deletion**: TiMemory implements "forgetting" rather than deletion. The `delete()` and `delete_all()` methods in TiDBVector exist for administrative purposes but are not used in normal memory processing. All memory updates preserve historical information through status transitions.

## Database Schema

### Memory Table (`memories`)

```sql
CREATE TABLE memories (
    id VARCHAR(36) PRIMARY KEY,                    -- UUID identifier
    vector VECTOR(1536),                           -- OpenAI embedding vector
    user_id VARCHAR(255) NOT NULL,                 -- User isolation key
    content VARCHAR(1000) NOT NULL,                -- Memory content text
    created_at DATETIME DEFAULT NOW(),             -- Creation timestamp
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(), -- Update timestamp
    memory_attributes JSON,                        -- Metadata (type, status)
    INDEX idx_user_id (user_id)                   -- User isolation index
);
```

**Key Design Decisions**:
- **Vector Dimension**: 1536 to match OpenAI text-embedding-3-small
- **User Isolation**: Indexed `user_id` for efficient filtering
- **Content Limit**: 1000 characters for memory content
- **JSON Attributes**: Flexible metadata storage for type/status
- **Timestamps**: Automatic creation and update tracking

### Vector Operations

**Insert Operation**:
```python
def insert(self, vector: List[float], user_id: str, content: str, 
           memory_attributes: Optional[Dict] = None, id: Optional[str] = None):
    memory = Memory(
        id=id or str(uuid4()),
        vector=vector,           # 1536-dimensional embedding
        user_id=user_id,        # User isolation
        content=content,        # Memory text
        memory_attributes=memory_attributes or {}
    )
```

**Similarity Search**:
```python
def search(self, query_vector: List[float], user_id: str, limit: int) -> MemoryResponse:
    results = db.query(Memory).options(defer(Memory.vector)).filter(
        Memory.user_id == user_id    # User isolation
    ).order_by(
        Memory.vector.cosine_distance(query_vector)  # Vector similarity
    ).limit(limit).all()
```

**Performance Optimizations**:
- **Deferred Loading**: Vector column deferred in search results
- **User Indexing**: B-tree index on `user_id` for fast filtering
- **Vector Indexing**: TiDB's native vector index for similarity search
- **Connection Pooling**: SQLAlchemy session management

## LLM Integration

### OpenAI LLM Wrapper (`OpenAILLM`)

**Structured Output Generation**:
```python
def generate_response(self, instructions: str, input: List[Dict[str, str]], 
                     text_format: str = None):
    response = self.client.responses.parse(
        model=self.model,           # gpt-4o-mini
        instructions=instructions,  # System prompt
        input=input,               # Conversation messages
        text_format=text_format    # Pydantic schema for structured output
    )
```

**Key Features**:
- **Structured Parsing**: Direct JSON schema validation via Pydantic
- **Error Handling**: OpenAI API exception management
- **Model Configuration**: Centralized model selection (gpt-4o-mini)

### Embedding Generation (`OpenAIEmbeddingModel`)

**Vector Generation**:
```python
def embed(self, text: str):
    response = self.client.embeddings.create(
        input=text,
        model=self.embedding_model,    # text-embedding-3-small
        dimensions=self.model_dims     # 1536
    )
    return response.data[0].embedding
```

**Technical Specifications**:
- **Model**: `text-embedding-3-small`
- **Dimensions**: 1536 (configurable via settings)
- **Rate Limiting**: Handled by OpenAI client
- **Cost Optimization**: Single embedding per memory content

## Memory Types and Classification

### Semantic Categories

1. **Personal** (`type: "personal"`)
   - Names, relationships, biographical data
   - Important dates, life events
   - Identity information

2. **Preference** (`type: "preference"`)
   - Likes, dislikes, opinions
   - Brand preferences, taste profiles
   - Subjective evaluations

3. **Activity** (`type: "activity"`)
   - Recent actions, events attended
   - Plans, scheduled activities
   - Behavioral patterns

4. **Plan** (`type: "plan"`)
   - Future intentions, goals
   - Scheduled events, commitments
   - Project timelines

5. **Health** (`type: "health"`)
   - Dietary restrictions, allergies
   - Fitness routines, medical conditions
   - Wellness preferences

6. **Professional** (`type: "professional"`)
   - Job titles, work responsibilities
   - Career goals, professional relationships
   - Industry expertise

7. **Miscellaneous** (`type: "miscellaneous"`)
   - Books, movies, entertainment
   - Hobbies, interests
   - General factual information

### Status Management

**Active Memories** (`status: "active"`):
- Current, valid information
- Used in similarity search and retrieval
- Default status for new memories

**Outdated Memories** (`status: "outdated"`):
- Superseded by newer information
- Preserved for historical context and pattern analysis
- Available to LLM for informed decision-making during retrieval

## Memory Forgetting vs. Deletion

### Design Philosophy: Forgetting, Not Deleting

TiMemory implements a **"forgetting" paradigm** rather than true deletion, mirroring how human memory actually works. When memories become outdated or contradicted, they are not erased from the system but rather marked as `"status": "outdated"`. This design choice reflects several important principles:

**Biological Memory Analogy**:
Human memory doesn't delete contradicted information—it layers new understanding over old patterns. When someone's taste preferences change, the old preference doesn't disappear; it becomes context that informs the new preference. TiMemory preserves this natural memory evolution.

**Contextual Value of Change**:
The transition from one state to another carries significant information. Consider this example:

```json
// Outdated Memory
{
  "id": "old-preference-123",
  "content": "Loves pizza and orders it frequently",
  "memory_attributes": {"type": "preference", "status": "outdated"}
}

// New Memory  
{
  "id": "new-preference-456", 
  "content": "No longer likes pizza due to dietary changes",
  "memory_attributes": {"type": "preference", "status": "active"}
}
```

The LLM can now understand:
- The user has a history with pizza
- This represents a recent change, not a lifelong dislike
- The change might be health-motivated rather than taste-based
- The user may have complex feelings about foods they once enjoyed

**Implementation Status**:
Currently, **no true deletion functionality is implemented**. All memory updates work through status transitions:

```python
# Current Implementation - No Deletion
def _store_memories(self, consolidated_memories: List[Memory], user_id: str):
    for memory in consolidated_memories:
        if status == 'outdated':
            self.tidbvector.update(id=memory.id, memory_attributes=memory.memory_attributes)
        else:
            self.tidbvector.insert(id=memory.id, ...)  # New active memory
```

**LLM-Driven Retrieval Intelligence**:
During memory retrieval, the LLM receives both active and outdated memories in context, allowing sophisticated reasoning:

1. **Pattern Recognition**: "The user used to love Italian food but recently became vegan"
2. **Sensitivity Awareness**: Understanding why preferences changed
3. **Temporal Context**: Recognizing recent vs. long-term changes
4. **Recommendation Refinement**: Avoiding suggestions that contradict recent changes while acknowledging past preferences

**Benefits of Forgetting Over Deletion**:

1. **Preserves Learning Context**: Pattern recognition improves with historical data
2. **Prevents Information Loss**: Important transitions aren't erased
3. **Enables Nuanced Understanding**: LLM can reason about preference evolution
4. **Maintains Audit Trail**: Full conversation history remains intact
5. **Supports Reversion**: If user returns to old preferences, context exists

**Future Enhancement Opportunities**:
- **Temporal Decay**: Gradually reduce retrieval weight of very old outdated memories
- **Memory Clustering**: Group related outdated memories for pattern analysis  
- **Forgetting Confidence**: Score how certain the system is about outdated status
- **User-Controlled Forgetting**: Allow explicit "please forget this" commands

This approach creates a more human-like memory system that understands change as information rather than treating it as error correction.

## Error Handling and Edge Cases

### Memory Extraction Failures
- **Empty Conversations**: Return empty memory list
- **LLM Errors**: Log error, propagate exception
- **Invalid JSON**: Schema validation via Pydantic

### Vector Search Issues
- **Database Connectivity**: Connection pooling with retry logic
- **Empty Results**: Return empty MemoryResponse object
- **Vector Dimension Mismatch**: Validation at embedding generation

### Consolidation Edge Cases
- **Circular References**: UUID-based deduplication
- **Large Memory Sets**: Batch processing for performance
- **Conflicting Timestamps**: Use memory creation order

## Performance Characteristics

### Scalability Metrics
- **Memory Storage**: O(1) insert/update operations
- **Similarity Search**: O(log n) with vector indexing
- **User Isolation**: O(1) with user_id indexing
- **Consolidation**: O(k) where k = similar memories found

### Resource Usage
- **Embedding Generation**: ~$0.00002 per 1K tokens (OpenAI pricing)
- **LLM Processing**: ~$0.00015 per 1K tokens (gpt-4o-mini)
- **Database Storage**: ~1KB per memory + 6KB vector storage
- **Memory Overhead**: ~10MB vector index per 1K memories

### Optimization Strategies
- **Batch Processing**: Group embeddings for API efficiency
- **Connection Pooling**: Reuse database connections
- **Vector Indexing**: TiDB's optimized similarity search
- **Selective Updates**: Only consolidate when conflicts detected

## Security and Privacy

### Data Isolation
- **User Partitioning**: All queries filtered by `user_id`
- **Database-Level Security**: No cross-user data leakage
- **Memory Attribution**: Immutable user associations

### Sensitive Information Handling
- **Content Filtering**: No explicit PII filtering (handled by application layer)
- **Audit Trail**: All memory updates tracked with timestamps
- **Data Retention**: Outdated memories preserved for consistency

### API Security
- **Authentication**: User ID validation before memory operations
- **Input Validation**: Pydantic schema validation for all inputs
- **Error Sanitization**: No internal system details in responses

## Configuration Parameters

### Environment Variables
```python
# OpenAI Configuration
OPENAI_API_KEY: str                    # OpenAI API key
MODEL_CHOICE: str = "gpt-4o-mini"     # LLM model selection
EMBEDDING_MODEL: str = "text-embedding-3-small"  # Embedding model

# TiDB Configuration
TIDB_HOST: str                         # Database host
TIDB_PORT: int = 4000                 # Database port
TIDB_USER: str                        # Database username
TIDB_PASSWORD: str                    # Database password
TIDB_DB_NAME: str                     # Database name
EMBEDDING_MODEL_DIMS: int = 1536      # Vector dimensions
```

### Runtime Configuration
- **Similarity Search Limit**: 10 (configurable per request)
- **Memory Content Limit**: 1000 characters
- **Connection Pool Size**: SQLAlchemy default (5 connections)
- **Vector Index Type**: TiDB's optimized vector index

## Future Enhancements

### Planned Features
- **Memory Expiration**: Time-based memory aging
- **Importance Scoring**: Weighted retrieval based on relevance
- **Batch Consolidation**: Process multiple conversations simultaneously
- **Memory Clustering**: Group related memories for efficient retrieval

### Performance Optimizations
- **Async Processing**: Non-blocking memory updates
- **Caching Layer**: Redis for frequently accessed memories
- **Vector Quantization**: Compressed embeddings for storage efficiency
- **Incremental Updates**: Partial memory consolidation

### Advanced Features
- **Memory Versioning**: Track memory evolution over time
- **Semantic Deduplication**: Advanced similarity thresholding
- **Cross-User Insights**: Anonymized pattern recognition
- **Memory Export**: User data portability features