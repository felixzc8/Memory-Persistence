# TiMemory Architecture Refactoring Plan

## Overview
This document outlines a major refactoring of the TiMemory system to eliminate the separate summaries table and implement topic-based memory processing instead of message-count-based processing.

## Current Issues
1. **Separate Summaries Table**: Creates unnecessary complexity with old summaries that are never used
2. **Frequent Memory Processing**: Processes memory after every user message regardless of conversation context
3. **Summary Generation Logic**: Generates summaries every 10 messages (summary_threshold) creating storage waste
4. **Storage Waste**: Multiple summaries per session accumulate without purpose

## Proposed Changes

### 1. Eliminate Summaries Table
**Goal**: Move summary storage directly into the sessions table for one-summary-per-session model.

**Session Model Changes**:
```python
# Add to Session model
summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
vector: Mapped[Optional[list[float]]] = mapped_column(VectorType(dim=1536), nullable=True)
summary_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
last_summary_generated_at: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
last_memory_processed_at: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
```

**Benefits**:
- Simplified schema (no joins needed)
- Better performance
- Reduced storage overhead
- Cleaner data model

### 2. Topic-Based Memory Processing
**Goal**: Replace frequent per-message processing with intelligent topic change detection.

**Current Logic**: 
- Memory processing: After every user message
- Summary generation: Every 10 messages (summary_threshold)

**New Logic**: Process memory only when topic changes are detected

**Implementation Approach**:
1. Track `last_memory_processed_at` (message number) in each session
2. After each user-assistant turn, analyze messages from last processed message number to current
3. Use LLM to detect topic changes with binary output
4. Trigger memory processing from last processed message number to topic change point

### 3. Topic-Based Summary Generation
**Goal**: Replace message-count-based summary generation with topic-change-based generation.

**Current Logic**: Generate summary every 10 messages (summary_threshold) regardless of context
**New Logic**: Generate summary when topic change is detected AND it has been over 20 messages since `last_summary_generated_at`

**Benefits**:
- Summaries align with natural conversation boundaries
- No arbitrary summary generation mid-topic
- Still ensures summaries don't become too stale (20 message limit)
- Better contextual coherence in summaries

### 4. Topic Change Detection System

**LLM Prompt Design**:
```
Analyze the following conversation messages and determine if there has been a significant topic change.

A topic change occurs when:
- The subject of conversation shifts to a different domain (e.g., food → work, personal life → technical discussion)
- The context changes significantly enough that previous memories may not be relevant

Messages to analyze:
[message sequence from last_processed_message_id to current]

Respond with only: YES or NO

YES = Topic change detected, trigger memory processing
NO = Same topic continues, no processing needed
```

**Detection Logic**:
1. Collect messages between `last_memory_processed_at` message number and current message
2. Pass to topic change detection LLM using `TopicChangedResponse` model for structured output
3. If `topic_changed: true`: Process memories for this message segment and update `last_memory_processed_at`
4. If `topic_changed: false`: Continue without processing, keep existing `last_memory_processed_at`

## Implementation Plan

### Phase 1: Database Schema Changes
1. **Update Session Model** (`models/session.py`)
   - Add: `summary`, `vector`, `summary_updated_at`, `last_summary_generated_at`
   - Add: `last_memory_processed_at` for memory processing tracking (tracks message number)
   - Remove relationship to Summary model

2. **Remove Summary Model** (`models/summary.py`)
   - Delete file entirely
   - Update imports across codebase


### Phase 2: Topic Change Detection
1. **Add Topic Detection to TiMemory Core** (`timemory.py`)
   - Add topic change detection method using structured output
   - Function to analyze message sequences using `TopicChangedResponse` model
   - Integration with existing `OpenAILLM.generate_parsed_response()` method


### Phase 3: Memory Processing Logic
1. **Update TiMemory Core** (`timemory.py`)
   - Replace message-count-based logic with topic-based triggers
   - Integrate topic change detection
   - Update summary generation to work with session-based storage

2. **Update Session Manager** (`session_manager.py`)
   - Remove summary-related methods (`create_summary`, `get_latest_summary`)
   - Add session summary management methods
   - Add `last_memory_processed_at` tracking methods

3. **Update Message Processing Flow**
   - After each user-assistant turn: check for topic changes
   - If topic change: process memories from last processed message number
   - If topic change AND >20 messages since `last_summary_generated_at`: generate new summary
   - Update `last_memory_processed_at` after memory processing
   - Update `last_summary_generated_at` after summary generation

### Phase 4: API and Schema Updates
1. **Update API Schemas** (`schemas/`)
   - Remove summary-related schemas
   - Update session schemas to include summary fields
   - Update response models

2. **Update Backend Services** (`backend/app/services/`)
   - Update memory service to use new topic-based processing
   - Update session service for new summary handling
   - Remove summary-specific endpoints if any exist

## Benefits of New Approach

### Technical Benefits
- **Reduced Complexity**: Single table for session + summary data
- **Better Performance**: No unnecessary joins or old summary queries
- **Intelligent Processing**: Memory processing triggered by content, not arbitrary counts
- **Storage Efficiency**: Only current summary per session

### User Experience Benefits
- **Context-Aware Memory**: Memories processed at natural conversation boundaries
- **Better Memory Relevance**: Processing aligned with topic shifts
- **Improved Performance**: Less frequent but more meaningful memory processing
- **Reduced Processing Overhead**: Memory processing only when contextually relevant instead of every message

## Migration Strategy

### Data Migration
All tables will be dropped when these changes are made, so no migration is needed.

## Testing Strategy
1. **Unit Tests**: Topic change detection accuracy
2. **Integration Tests**: End-to-end memory processing flow
3. **Performance Tests**: Compare processing efficiency vs old approach
4. **Data Integrity Tests**: Verify migration preserves all summary data

## Timeline Estimate
- **Phase 1**: 1-2 days (schema changes, migration)
- **Phase 2**: 1 day (topic detection implementation)
- **Phase 3**: 2-3 days (core logic refactoring)
- **Phase 4**: 1 day (API updates)
- **Testing & Polish**: 1-2 days

**Total**: 6-9 days for complete implementation

## Risk Assessment
- **Low Risk**: Schema changes are additive initially
- **Medium Risk**: Topic detection accuracy needs tuning
- **Low Risk**: Rollback strategy available during migration
- **Medium Risk**: Memory processing frequency may need adjustment based on topic detection sensitivity