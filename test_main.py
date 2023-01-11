from fastapi.testclient import TestClient
from dataclasses import dataclass
from main import app
import json

client = TestClient(app)


@dataclass
class Tests:
    Token: str
    SecondToken: str


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello from user's app!"


def test_register_wrong_email():
    response = client.post(
        "/register",
        params={
            'mail': 'ss',
        },
        data={
            'username': 'ss111',
            'password': '11ss',
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "E-mail not found"


def test_register_valid():
    response = client.post(
        "/register",
        params={
            'mail': 'aa.edu',
        },
        data={
            'username': 'vlad',
            'password': 'vlad',
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Register successfully"


def test_register_user_exists():
    response = client.post(
        "/register",
        params={
            'mail': 'aa.edu',
        },
        data={
            'username': 'vlad',
            'password': 'vlad',
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_login_invalid_username():
    response = client.post(
        "/token",
        data={
            'username': 'JohnDoe',
            'password': 'vlad',
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_login_invalid_password():
    response = client.post(
        "/token",
        data={
            'username': 'vlad',
            'password': 'JohnDoe',
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"


def test_empty_posts():
    response = client.get(
        "/posts",
    )
    assert response.status_code == 200
    assert response.json() == []


def test_post_not_found():
    response = client.get(
        "/posts/1"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_bad_auth():
    response = client.post(
        "/posts/create"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_login():
    response = client.post(
        "/token",
        data={
            'username': 'vlad',
            'password': 'vlad',
        }
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    Tests.Token = response.json()["access_token"]


def test_post_create():
    response = client.post(
        "/posts/create",
        headers={"Authorization": f"Bearer {Tests.Token}"},
        params={
            'title': 'test title',
            'text': 'test text'
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Created successfully"


def test_post_found():
    response = client.get(
        "/posts/1"
    )
    assert response.status_code == 200
    assert response.json() == {
        "text": "test text",
        "dislikes": None,
        "title": "test title",
        "likes": None,
        "id": 1,
        "user_id": 1
    }


def test_all_posts_found():
    response = client.get(
        "/posts"
    )
    assert response.status_code == 200
    assert response.json() == [{
        "text": "test text",
        "dislikes": None,
        "title": "test title",
        "likes": None,
        "id": 1,
        "user_id": 1
    }]


def test_mark_own_post():
    response = client.get(
        "/posts/1/is_like?is_like=true",
        headers={"Authorization": f"Bearer {Tests.Token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You can't mark your own posts"

    response = client.get(
        "/posts/1/is_like?is_like=false",
        headers={"Authorization": f"Bearer {Tests.Token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You can't mark your own posts"


def test_post_edit():
    response = client.put(
        "/posts/1",
        headers={"Authorization": f"Bearer {Tests.Token}"},
        params={
            'title': 'new test title',
            'text': 'new test text'
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Edited successfully"


def test_like_user_post():
    response = client.post(
        "/register",
        params={
            'mail': 'aa.gov.rs',
        },
        data={
            'username': 'vlad2',
            'password': 'vlad2',
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Register successfully"

    response = client.post(
        "/token",
        data={
            'username': 'vlad2',
            'password': 'vlad2',
        }
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    Tests.SecondToken = response.json()["access_token"]
    response = client.get(
        "/posts/1/is_like?is_like=true",
        headers={"Authorization": f"Bearer {Tests.SecondToken}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Marked successfully"
    response = client.get(
        "/posts/1/is_like?is_like=false",
        headers={"Authorization": f"Bearer {Tests.Token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You can't mark your own posts"


def test_delete_post():
    response = client.delete(
        "/posts/1",
        headers={"Authorization": f"Bearer {Tests.SecondToken}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
    response = client.delete(
        "/posts/1",
        headers={"Authorization": f"Bearer {Tests.Token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Deleted successfully"
