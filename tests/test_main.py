import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "healthy"
    assert "version" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["service"] == "openclaw-experiment"


def test_api_info():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "openclaw-experiment"
    assert "features" in data


def test_api_time():
    response = client.get("/api/time")
    assert response.status_code == 200
    data = response.json()
    assert "utc" in data
    assert "timestamp" in data


def test_api_headers():
    response = client.get("/api/headers")
    assert response.status_code == 200
    data = response.json()
    assert "headers" in data
    assert "method" in data


def test_api_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "system" in data
    assert "app" in data
    assert "cpu_percent" in data["system"]


def test_api_random():
    response = client.get("/api/random")
    assert response.status_code == 200
    data = response.json()
    assert "uuid" in data
    assert "token" in data
    assert "hex" in data


def test_api_hash_default():
    response = client.get("/api/hash/hello")
    assert response.status_code == 200
    data = response.json()
    assert data["input"] == "hello"
    assert data["algorithm"] == "sha256"
    assert "hash" in data
    assert len(data["hash"]) == 64  # SHA-256 hex is 64 chars


def test_api_hash_sha512():
    response = client.get("/api/hash/hello?algorithm=sha512")
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "sha512"
    assert len(data["hash"]) == 128  # SHA-512 hex is 128 chars


def test_api_hash_invalid_algorithm():
    response = client.get("/api/hash/hello?algorithm=invalid")
    assert response.status_code == 400


def test_api_ip():
    response = client.get("/api/ip")
    assert response.status_code == 200
    data = response.json()
    assert "ip" in data
    assert "timestamp" in data


def test_api_echo():
    response = client.post("/api/echo", json={"message": "Hello World"})
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "Hello World"
    assert data["echoed"] == "hello world"


def test_api_echo_uppercase():
    response = client.post("/api/echo", json={
        "message": "Hello World",
        "uppercase": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["echoed"] == "HELLO WORLD"
