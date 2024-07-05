from http import HTTPStatus

from fast_api_todo.schemas import UserPublicSchema


def test_app_should_return_hello_world(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World"}


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "test",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "test",
        "email": "test@example.com",
    }


def test_create_user_with_a_username_existent(client):
    client.post(
        "/users/",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "test",
        },
    )

    response = client.post(
        "/users/",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "test",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        "detail": "Username already existis",
    }


def test_create_user_with_a_email_existent(client):
    client.post(
        "/users/",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "test",
        },
    )

    response = client.post(
        "/users/",
        json={
            "username": "test2",
            "email": "test@example.com",
            "password": "test",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        "detail": "Email already existis",
    }


def test_get_users(client):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_get_users_with_user(client, user):
    user_schema = UserPublicSchema.model_validate(user).model_dump()

    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_get_user(client, user):
    UserPublicSchema.model_validate(user).model_dump()

    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "test",
        "email": "test@email.com",
    }


def test_get_user_if_not_existis(client, user):
    UserPublicSchema.model_validate(user).model_dump()

    response = client.get("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User not found",
    }


def test_update_user(client, user, token):
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test2",
            "email": "test2@example.com",
            "password": "test2",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": "test2",
        "email": "test2@example.com",
    }


def test_update_user_if_not_existis(client, user):
    response = client.put(
        "/users/2",
        json={
            "username": "test2",
            "email": "test2@example.com",
            "password": "test2",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_update_another(client, user, token):
    response = client.put(
        "/users/2",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "test2",
            "email": "test2@example.com",
            "password": "test2",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Not enough permission"}


def test_delete_user(client, user, token):
    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_not_found(client):
    response = client.delete("/users/3")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_another_user(client, token):
    response = client.delete(
        "/users/3",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Not enough permission"}


def test_get_token(client, user):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_login_with_invalid_user(client):
    response = client.post(
        "/token",
        data={"username": "invalid@test.com", "password": "invalid"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Incorrect email or password"}
