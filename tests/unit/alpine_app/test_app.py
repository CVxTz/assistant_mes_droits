import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage

# Update with your actual module path
from assistant_mes_droits.alpine_app.main import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def valid_human_message():
    return HumanMessage(content="Test message", type="human")


def test_root_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text.lower()


def test_robots_txt(test_client):
    response = test_client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    content = response.text
    assert "User-agent: *" in content
    assert "Disallow: /chat" in content
    assert "Allow: /" in content


def test_chat_endpoint(test_client, valid_human_message):
    # Mock the agent's invoke method

    with test_client as client:
        response = client.post("/chat", json={"messages": [valid_human_message.dict()]})

        assert response.status_code == 200
        assert "type" in response.json()
        assert "content" in response.json()


def test_reset_endpoint(test_client):
    response = test_client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_invalid_chat_request(test_client):
    with test_client as client:
        # Test invalid message format with proper type field
        response = client.post(
            "/chat",
            json={"messages": [{"type": "invalid_type", "content": "invalid message"}]},
        )
        assert response.status_code == 422


def test_robots_txt_content(test_client):
    response = test_client.get("/robots.txt")
    content = response.text
    assert "User-agent: Googlebot\nAllow: /" in content
    assert "User-agent: *\nDisallow: /chat" in content
    assert "Disallow: /static/" in content
