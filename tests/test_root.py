def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json.get("body") == "Hello World"
