from fastapi import status
import pytest
import json

from app import models, schemas

# test create user LC

@pytest.mark.parametrize("new_user_data", [
    ({
        "name": "pytest 01",
        "username": "pytest-01",
        "email": "pytest-01@test.com",
        "password": "pytest-01",
        "verified_user": 'true',
    }),
    ({
        "name": "pytest 02",
        "username": "pytest-02",
        "email": "pytest-02@test.com",
        "password": "pytest-02",
        "verified_user": '0',
    }),
    ({
        "name": "pytest 03",
        "username": "pytest-03",
        "email": "pytest-03@test.com",
        "password": "pytest-03",
    }),
    ({
        "name": "pytest 04",
        "username": "pytest-04",
        "email": "pytest-04@test.com",
        "password": "pytest-04",
        "verified_user": 1,
    }),
])
def test_create_user(client, session, new_user_data):
    resp = client.post("/api/v1/users", data=new_user_data)
    assert resp.status_code == status.HTTP_201_CREATED
    new_user = schemas.GetUser(**resp.json())
    assert new_user.name == new_user_data.get("name")
    assert new_user.username == new_user_data.get("username")
    assert new_user.email == new_user_data.get("email")
    verified_user = new_user_data.get("verified_user", 'false')
    verified_user = True if str(verified_user).lower() in ["true", "1"] else False
    assert new_user.verified_user == verified_user

@pytest.mark.parametrize("new_user_data,missing_field", [
    ({
        "username": "pytest-01",
        "email": "pytest-01@test.com",
        "password": "pytest-01",
    }, "name"),
    ({
        "name": "pytest 02",
        "email": "pytest-02@test.com",
        "password": "pytest-02",
    }, "username"),
    ({
        "name": "pytest 02",
        "username": "pytest-01",
        "password": "pytest-02",
    }, "email"),
    ({
        "name": "pytest 02",
        "username": "pytest-01",
        "email": "pytest-02@test.com",
    }, "password"),
])
def test_missing_fields(client, new_user_data, missing_field):
    resp = client.post("/api/v1/users", data=new_user_data)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    resp_json = resp.json()
    assert resp_json.get("detail")[0].get("type") == "missing"
    assert resp_json.get("detail")[0].get("loc")[1] == missing_field
    assert resp_json.get("detail")[0].get("msg") == "Field required"

@pytest.mark.parametrize("new_user_data,error_type,impacted_field,message", [
    (
        {
            "name": "pytest 05",
            "username": "pytest-05",
            "email": "pytest-05",
            "password": "pytest-05",
        },
        "value_error",
        "email",
        "value is not a valid email address: An email address must have an @-sign."
    ),
    (
        {
            "name": "pytest 05",
            "username": "pytest-05",
            "email": "pytest-05@test.com",
            "password": "pytest-05",
            "verified_user": "YES"
        },
        "literal_error",
        "verified_user",
        "Input should be 'true', 'false', '1' or '0'"
    ),
    (
        {
            "name": "pytest 05",
            "username": "pytest-05",
            "email": "pytest-05@test.com",
            "password": "pytest-05",
            "verified_user": "True"
        },
        "literal_error",
        "verified_user",
        "Input should be 'true', 'false', '1' or '0'"
    ),
    (
        {
            "name": "pytest 05",
            "username": "pytest-05",
            "email": "pytest-05@test.com",
            "password": "pytest-05",
            "verified_user": 100
        },
        "literal_error",
        "verified_user",
        "Input should be 'true', 'false', '1' or '0'"
    ),
])
def test_create_value_errors(client, new_user_data, error_type, impacted_field, message):
    resp = client.post("/api/v1/users", data=new_user_data)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    resp_json = resp.json()
    assert resp_json.get("detail")[0].get("type") == error_type
    assert resp_json.get("detail")[0].get("loc")[1] == impacted_field
    assert resp_json.get("detail")[0].get("input").lower() == str(new_user_data.get(impacted_field)).lower()
    assert resp_json.get("detail")[0].get("msg") == message

@pytest.mark.parametrize("new_user_data,message", [
    ({
        "name": "pytest 01",
        "username": "pytest-01",
        "email": "pytest-01@test.com",
        "password": "pytest-01",
        "verified_user": True,
    }, "email pytest-01@test.com already exists!"),
    ({
        "name": "pytest 03",
        "username": "pytest-03",
        "email": "pytest-99@test.com",
        "password": "pytest-03",
    }, "username pytest-03 already exists!"),
])
def test_existing_ids(client, new_user_data, message):
    resp = client.post("/api/v1/users", data=new_user_data)
    assert resp.status_code == status.HTTP_226_IM_USED
    resp_json = resp.json()
    assert resp_json["detail"] == message

# test get user LC

@pytest.mark.parametrize("page,page_size,query", [
    (1, 8, None),
    (2, 4, "test"),
    (3, 1, "pyt"),
])
def test_get_users(client, session, page, page_size, query):
    resp = client.get("/api/v1/users", params={"page": page, "page_size": page_size, "query": query})
    assert resp.status_code == status.HTTP_200_OK
    users = schemas.GetPaginatedUser(**resp.json())
    assert type(users.items) is list
    assert users.page == page
    assert users.page_size == page_size
    assert users.total_count != 0
    for each_user in users.items:
        assert type(each_user.username) is str and each_user.username is not None
        assert type(each_user.email) is str and each_user.email is not None
        assert type(each_user.name) is str and each_user.name is not None

@pytest.mark.parametrize("query", [
    ("abc"),
    ("@|,")
])
def test_invalid_users(client, session, query, page=1, page_size=8):
    resp = client.get("/api/v1/users", params={"page": page, "page_size": page_size, "query": query})
    assert resp.status_code == status.HTTP_200_OK
    users = schemas.GetPaginatedUser(**resp.json())
    assert type(users.items) is list
    assert users.total_count == 0

@pytest.mark.parametrize("username", [
    ("pytest-01"),
    ("pytest-03")
])
def test_get_user(client, session, username):
    resp = client.get(f"/api/v1/users/{username}")
    assert resp.status_code == status.HTTP_200_OK
    user = schemas.GetUser(**resp.json())
    assert type(user.username) is str and user.username is not None
    assert type(user.email) is str and user.email is not None
    assert type(user.name) is str and user.name is not None
    assert user.username == username

@pytest.mark.parametrize("username,detail", [
    ("pytest-88", "username pytest-88 not found!"),
    ("@|,", "username @|, not found!"),
])
def test_get_wrong_user(client, session, username, detail):
    resp = client.get(f"/api/v1/users/{username}")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    resp_json = resp.json()
    assert resp_json.get("detail") == detail

# test update user LC

@pytest.mark.parametrize("username,password,update_user_data", [
    ("pytest-01", "pytest-01", {
        "name": "pytest user 01",
    }),
    ("pytest-03", "pytest-03", {
        "verified_user": True,
    }),
    ("pytest-04", "pytest-04", {
        "verified_user": False,
    }),
])
def test_update_user(client, login_user, username, password, update_user_data):
    access_token = login_user({"username": username, "password": password})
    resp = client.put(
        f"/api/v1/users/{username}",
        data=update_user_data,
        headers={'AUTHORIZATION': f"Bearer {access_token}"}
    )
    assert resp.status_code == status.HTTP_200_OK
    resp_json = schemas.GetUser(**resp.json())
    for each_key in update_user_data.keys():
        assert update_user_data[each_key] == getattr(resp_json, each_key)

@pytest.mark.parametrize("username,update_user_data,detail", [
    ("pytest-02", {
        "name": "unauthorized 02",
    }, "Not authenticated"),
])
def test_update_user_unath(client, username, update_user_data, detail):
    resp = client.put(f"/api/v1/users/{username}", data=update_user_data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    resp_json = resp.json()
    assert resp_json.get("detail") == detail

@pytest.mark.parametrize("update_user_data,username,password,error_type,impacted_field,message", [
    ({
        "verified_user": "True",
    }, "pytest-03", "pytest-03", "literal_error", "verified_user",
    "Input should be 'true', 'false', '1' or '0'"),
    ({
        "verified_user": "ABC",
    }, "pytest-04", "pytest-04", "literal_error", "verified_user",
    "Input should be 'true', 'false', '1' or '0'"),
])
def test_update_value_errors(client, login_user, username, password, update_user_data, error_type, impacted_field, message):
    access_token = login_user({"username": username, "password": password})
    resp = client.put(
        f"/api/v1/users/{username}",
        data=update_user_data,
        headers={'AUTHORIZATION': f"Bearer {access_token}"}
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    resp_json = resp.json()
    assert resp_json.get("detail")[0].get("type") == error_type
    assert resp_json.get("detail")[0].get("loc")[1] == impacted_field
    assert resp_json.get("detail")[0].get("input").lower() == str(update_user_data.get(impacted_field)).lower()
    assert resp_json.get("detail")[0].get("msg") == message

# test delete user LC

@pytest.mark.parametrize("username,password", [
    ("pytest-03", "pytest-03"),
    ("pytest-04", "pytest-04"),
])
def test_delete_user(client, login_user, username, password):
    access_token = login_user({"username": username, "password": password})
    resp = client.delete(
        f"/api/v1/users/{username}",
        headers={'AUTHORIZATION': f"Bearer {access_token}"}
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.parametrize("username,detail", [
    ("pytest-02", "Not authenticated"),
    ("pytest-04", "Not authenticated"),
])
def test_delete_user_unath(client, username, detail):
    resp = client.delete(f"/api/v1/users/{username}")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    resp_json = resp.json()
    assert resp_json.get("detail") == detail
