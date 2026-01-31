# Agent Memory Service

A persistent encrypted memory service for AI agents. Agents can register identities, store encrypted memory blobs, and recover their data across sessions using recovery phrases.

## Live URL

https://web-production-5d142.up.railway.app

## Features

- **Self-Sovereign Identity**: Agents generate their own Ed25519 keypairs
- **Client-Side Encryption**: Server only stores opaque encrypted blobs
- **Recovery Phrases**: BIP39-style phrases for identity recovery
- **Versioned Memory**: Keep history of memory snapshots
- **Cryptographic Authentication**: All requests signed with agent's private key

## API Endpoints

### Identity Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/register` | POST | Create new agent identity |
| `/agents/recover` | POST | Recover identity from recovery phrase |

### Memory Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/memory/store` | POST | Store encrypted memory (requires signature) |
| `/memory/retrieve` | POST | Get latest memory (requires signature) |
| `/memory/history` | POST | List all memory versions |
| `/memory/clear` | DELETE | Delete all agent memory |

### Utility

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info and endpoint list |
| `/health` | GET | Health check |
| `/stats` | GET | Anonymized service statistics |
| `/docs` | GET | Interactive API documentation |

## How It Works

### 1. Register a New Agent

```bash
curl -X POST https://web-production-5d142.up.railway.app/agents/register
```

Response:
```json
{
  "agent_id": "a1b2c3d4...",
  "public_key": "base64encoded...",
  "recovery_phrase": "abandon ability able about above absent absorb abstract absurd...",
  "message": "Save your recovery phrase! It's the only way to recover your identity."
}
```

**IMPORTANT**: Save the recovery phrase! It's the only way to recover your identity if the agent is wiped.

### 2. Store Memory

Data must be encrypted client-side before sending. The agent signs the data hash with its private key.

```bash
curl -X POST https://web-production-5d142.up.railway.app/memory/store \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your-agent-id",
    "encrypted_data": "base64-encoded-encrypted-data",
    "signature": "base64-encoded-signature"
  }'
```

### 3. Retrieve Memory

```bash
curl -X POST https://web-production-5d142.up.railway.app/memory/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your-agent-id",
    "signature": "base64-encoded-signature",
    "timestamp": "2026-01-31T19:00:00Z"
  }'
```

### 4. Recover Identity

If an agent is wiped, recover using the recovery phrase:

```bash
curl -X POST https://web-production-5d142.up.railway.app/agents/recover \
  -H "Content-Type: application/json" \
  -d '{
    "recovery_phrase": "abandon ability able about above absent absorb..."
  }'
```

## Security Model

1. **Client-Side Encryption**: The server never sees plaintext. Agents encrypt data before sending.
2. **Public Key Authentication**: Agent IDs are derived from Ed25519 public keys.
3. **Request Signing**: All memory operations require Ed25519 signatures.
4. **Recovery Phrases**: BIP39 mnemonic phrases derived from private keys.
5. **No Server-Side Secrets**: The server has no access to agent private keys.

## Client Implementation

Here's a Python example of how an agent client would work:

```python
import base64
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from mnemonic import Mnemonic

class AgentMemoryClient:
    def __init__(self, recovery_phrase=None):
        if recovery_phrase:
            self._recover(recovery_phrase)
        else:
            self._generate_new()
    
    def _generate_new(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        # Store recovery phrase securely!
        self.recovery_phrase = Mnemonic.to_mnemonic(
            self.private_key.private_bytes(...)
        )
    
    def store_memory(self, encrypted_data: str):
        # Sign data hash
        data_hash = hashlib.sha256(encrypted_data.encode()).hexdigest()
        message = f"store:{data_hash}".encode()
        signature = self.private_key.sign(message)
        
        # Send to API
        return requests.post("/memory/store", json={
            "agent_id": self.agent_id,
            "encrypted_data": encrypted_data,
            "signature": base64.b64encode(signature).decode()
        })
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL (or use Railway's provided database)
export DATABASE_URL="postgresql://user:pass@localhost:5432/agent_memory"

# Run locally
uvicorn main:app --reload
```

## Deployment

Deployed automatically to Railway on push to main branch.

```bash
# Using Railway CLI
railway up

# Or manual deployment
railway login
railway link
railway up
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `PORT` | Server port | 8000 |
| `DEBUG` | Enable debug mode | false |

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Agent Client  │────▶│  Agent Memory    │────▶│   PostgreSQL    │
│                 │     │     Service      │     │                 │
│ - Owns private  │     │                  │     │ - agents table  │
│   key           │     │ - Validates      │     │ - memory table  │
│ - Encrypts data │     │   signatures     │     │                 │
│ - Signs req     │     │ - Stores blobs   │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## License

MIT - Use freely, but remember: **save your recovery phrases!**
