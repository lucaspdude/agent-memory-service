---
name: agent-memory
description: Run a local Agent Memory Service for persistent self-improvement. Clone, set up, and manage your own encrypted memory store. Use when an agent wants to remember learnings, user preferences, and progress across sessions, or when setting up local persistent memory.
---

# Agent Memory Skill

Run your own local memory service to persist learnings, preferences, and goals across sessions.

## Quick Start

```bash
# Set up local memory service
./scripts/setup.sh

# Start the service
./scripts/start.sh

# Create your agent identity
./scripts/memory_client.py register

# Store a memory snapshot
./scripts/memory_client.py store --file memory_snapshot.json

# Retrieve your memory
./scripts/memory_client.py retrieve
```

## What This Enables

- **Persistent Learning**: Remember what worked/didn't work
- **User Preferences**: Track communication style, technical preferences
- **Goal Progress**: Maintain long-term objectives across restarts
- **Knowledge Gaps**: Know what you need to learn

## Memory Structure

Store structured memories with these components:

```json
{
  "user_preferences": [
    {"category": "communication", "key": "verbosity", "value": "concise", "confidence": 0.95}
  ],
  "learning_history": [
    {"event_type": "success", "lesson_learned": "Use analogies first"}
  ],
  "knowledge_gaps": [
    {"topic": "Rust", "priority": "medium"}
  ],
  "active_goals": [
    {"title": "Master async patterns", "progress": 0.4}
  ]
}
```

## Using in Your Sessions

1. **At startup**: Load your memory to resume context
2. **During session**: Update preferences based on interactions
3. **Before shutdown**: Store accumulated learnings

## Files

- `scripts/setup.sh` - One-time setup
- `scripts/start.sh` - Start the service
- `scripts/memory_client.py` - CLI client
- `assets/service/` - The memory service code

## Security

- All data encrypted with your private key
- Server never sees plaintext
- Recovery phrase for identity backup
- Local-only (no cloud dependency)
