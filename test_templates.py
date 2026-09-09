def test_template_crud(client, template_payload):
    created = client.post("/api/v1/templates", json=template_payload)
    assert created.status_code == 201
    template_id = created.json()["id"]

    listed = client.get("/api/v1/templates")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/templates/{template_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == template_payload["name"]

    updated = client.patch(
        f"/api/v1/templates/{template_id}",
        json={"temperature": 0.8, "active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["temperature"] == 0.8
    assert updated.json()["active"] is False

    deleted = client.delete(f"/api/v1/templates/{template_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/templates/{template_id}").status_code == 404


def test_duplicate_template_name_is_conflict(client, template_payload):
    assert client.post("/api/v1/templates", json=template_payload).status_code == 201
    duplicate = {**template_payload, "name": template_payload["name"].upper()}
    response = client.post("/api/v1/templates", json=duplicate)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_invalid_placeholder_is_business_error(client, template_payload):
    template_payload["user_prompt_template"] = "Explique {{produto com espaço}}."
    response = client.post("/api/v1/templates", json=template_payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "business_rule_violation"


def test_request_validation_has_standard_error_shape(client, template_payload):
    template_payload["temperature"] = 9
    response = client.post("/api/v1/templates", json=template_payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_required_update_field_cannot_be_null(client, template_payload):
    created = client.post("/api/v1/templates", json=template_payload)
    template_id = created.json()["id"]
    response = client.patch(
        f"/api/v1/templates/{template_id}", json={"active": None}
    )
    assert response.status_code == 422
    assert response.json()["error"]["details"]["fields"] == ["active"]
