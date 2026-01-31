"""
Tests for Agent Memory Service

These tests verify the core functionality:
- Agent registration
- Memory storage and retrieval
- Identity recovery
- Authentication
"""

import pytest
import base64
import hashlib
from datetime import datetime
from fastapi.testclient import TestClient
from main import app, get_db_connection, generate_keypair, get_agent_id, key_to_bytes

client = TestClient(app)


@pytest.fixture
def test_agent():
    """Create a test agent and return credentials"""
    # Register agent
    response = client.post("/agents/register")
    assert response.status_code == 200
    data = response.json()
    
    return {
        "agent_id": data["agent_id"],
        "public_key": data["public_key"],
        "recovery_phrase": data["recovery_phrase"]
    }


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Agent Memory Service"
    assert "endpoints" in data


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data


def test_register_agent():
    """Test agent registration"""
    response = client.post("/agents/register")
    assert response.status_code == 200
    data = response.json()
    
    assert "agent_id" in data
    assert len(data["agent_id"]) == 64  # SHA-256 hex
    assert "public_key" in data
    assert "recovery_phrase" in data
    assert len(data["recovery_phrase"].split()) == 24  # 24-word BIP39 phrase


def test_recover_agent(test_agent):
    """Test agent recovery"""
    response = client.post("/agents/recover", json={
        "recovery_phrase": test_agent["recovery_phrase"]
    })
    assert response.status_code == 200
    data = response.json()
    
    assert data["agent_id"] == test_agent["agent_id"]
    assert data["public_key"] == test_agent["public_key"]
    assert data["recovered"] is True


def test_recover_invalid_phrase():
    """Test recovery with invalid phrase"""
    response = client.post("/agents/recover", json={
        "recovery_phrase": "invalid phrase here"
    })
    assert response.status_code == 400


def test_store_and_retrieve_memory(test_agent):
    """Test storing and retrieving memory"""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from mnemonic import Mnemonic
    
    # Recover private key from phrase
    mnemo = Mnemonic("english")
    private_bytes = mnemo.to_entropy(test_agent["recovery_phrase"])
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    
    # Prepare test data
    encrypted_data = base64.b64encode(b"test memory data").decode()
    data_hash = hashlib.sha256(encrypted_data.encode()).hexdigest()
    
    # Sign the data
    message = f"store:{data_hash}".encode()
    signature = private_key.sign(message)
    signature_b64 = base64.b64encode(signature).decode()
    
    # Store memory
    response = client.post("/memory/store", json={
        "agent_id": test_agent["agent_id"],
        "encrypted_data": encrypted_data,
        "signature": signature_b64
    })
    assert response.status_code == 200
    store_data = response.json()
    assert store_data["stored"] is True
    assert store_data["version"] == 1
    
    # Retrieve memory
    timestamp = datetime.utcnow().isoformat()
    retrieve_message = f"retrieve:{timestamp}".encode()
    retrieve_signature = private_key.sign(retrieve_message)
    retrieve_signature_b64 = base64.b64encode(retrieve_signature).decode()
    
    response = client.post("/memory/retrieve", json={
        "agent_id": test_agent["agent_id"],
        "signature": retrieve_signature_b64,
        "timestamp": timestamp
    })
    assert response.status_code == 200
    retrieve_data = response.json()
    assert retrieve_data["encrypted_data"] == encrypted_data
    assert retrieve_data["agent_id"] == test_agent["agent_id"]


def test_store_without_auth():
    """Test that storing without valid signature fails"""
    response = client.post("/memory/store", json={
        "agent_id": "nonexistent",
        "encrypted_data": "test",
        "signature": "invalid"
    })
    assert response.status_code == 404


def test_invalid_signature(test_agent):
    """Test that invalid signatures are rejected"""
    response = client.post("/memory/store", json={
        "agent_id": test_agent["agent_id"],
        "encrypted_data": "test data",
        "signature": base64.b64encode(b"invalid").decode()
    })
    assert response.status_code == 401


def test_memory_history(test_agent):
    """Test listing memory history"""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from mnemonic import Mnemonic
    
    # Recover private key
    mnemo = Mnemonic("english")
    private_bytes = mnemo.to_entropy(test_agent["recovery_phrase"])
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    
    # Store multiple memories
    for i in range(3):
        encrypted_data = base64.b64encode(f"memory {i}".encode()).decode()
        data_hash = hashlib.sha256(encrypted_data.encode()).hexdigest()
        message = f"store:{data_hash}".encode()
        signature = private_key.sign(message)
        
        client.post("/memory/store", json={
            "agent_id": test_agent["agent_id"],
            "encrypted_data": encrypted_data,
            "signature": base64.b64encode(signature).decode()
        })
    
    # Get history
    timestamp = datetime.utcnow().isoformat()
    retrieve_message = f"retrieve:{timestamp}".encode()
    retrieve_signature = private_key.sign(retrieve_message)
    
    response = client.post("/memory/history", json={
        "agent_id": test_agent["agent_id"],
        "signature": base64.b64encode(retrieve_signature).decode(),
        "timestamp": timestamp
    })
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 3
    assert len(data["memories"]) >= 3


def test_stats():
    """Test stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_agents" in data
    assert "total_memories" in data
    assert "privacy_note" in data


def test_clear_memory(test_agent):
    """Test clearing all memory"""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from mnemonic import Mnemonic
    
    # Recover private key
    mnemo = Mnemonic("english")
    private_bytes = mnemo.to_entropy(test_agent["recovery_phrase"])
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    
    # Store a memory first
    encrypted_data = base64.b64encode(b"to be deleted").decode()
    data_hash = hashlib.sha256(encrypted_data.encode()).hexdigest()
    message = f"store:{data_hash}".encode()
    signature = private_key.sign(message)
    
    client.post("/memory/store", json={
        "agent_id": test_agent["agent_id"],
        "encrypted_data": encrypted_data,
        "signature": base64.b64encode(signature).decode()
    })
    
    # Clear memory
    timestamp = datetime.utcnow().isoformat()
    delete_message = f"delete:{timestamp}".encode()
    delete_signature = private_key.sign(delete_message)
    
    response = client.request("DELETE", "/memory/clear", json={
        "agent_id": test_agent["agent_id"],
        "signature": base64.b64encode(delete_signature).decode(),
        "timestamp": timestamp
    })
    assert response.status_code == 200
    data = response.json()
    assert data["cleared"] is True
    assert data["deleted_count"] >= 1
