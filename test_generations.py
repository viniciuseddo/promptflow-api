def create_template(client, payload):
    response = client.post("/api/v1/templates", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def test_generate_and_manage_history(client, template_payload):
    template_id = create_template(client, template_payload)
    response = client.post(
        "/api/v1/generations",
        json={
            "template_id": template_id,
            "variables": {"produto": "garrafa térmica", "publico": "trilheiros"},
        },
    )
    assert response.status_code == 201
    generation = response.json()
    assert generation["status"] == "success"
    assert generation["provider"] == "local"
    assert "garrafa térmica" in generation["rendered_prompt"]
    assert "MODO DEMONSTRAÇÃO" in generation["response_text"]

    listed = client.get(
        f"/api/v1/generations?template_id={template_id}&status=success"
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    generation_id = generation["id"]
    assert client.get(f"/api/v1/generations/{generation_id}").status_code == 200
    assert client.delete(f"/api/v1/generations/{generation_id}").status_code == 204
    assert client.delete(f"/api/v1/templates/{template_id}").status_code == 204


def test_missing_and_unexpected_variables_are_rejected(client, template_payload):
    template_id = create_template(client, template_payload)
    response = client.post(
        "/api/v1/generations",
        json={
            "template_id": template_id,
            "variables": {"produto": "mochila", "cor": "azul"},
        },
    )
    assert response.status_code == 422
    details = response.json()["error"]["details"]
    assert details["missing"] == ["publico"]
    assert details["unexpected"] == ["cor"]


def test_inactive_template_cannot_be_used(client, template_payload):
    template_payload["active"] = False
    template_id = create_template(client, template_payload)
    response = client.post(
        "/api/v1/generations",
        json={
            "template_id": template_id,
            "variables": {"produto": "caderno", "publico": "estudantes"},
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "business_rule_violation"


def test_template_with_history_must_be_deactivated(client, template_payload):
    template_id = create_template(client, template_payload)
    generated = client.post(
        "/api/v1/generations",
        json={
            "template_id": template_id,
            "variables": {"produto": "caneca", "publico": "designers"},
        },
    )
    assert generated.status_code == 201

    response = client.delete(f"/api/v1/templates/{template_id}")
    assert response.status_code == 409
    assert response.json()["error"]["details"]["generation_count"] == 1


def test_unknown_resources_return_404(client):
    assert client.get("/api/v1/templates/999").status_code == 404
    assert client.get("/api/v1/generations/999").status_code == 404


def test_unconfigured_external_provider_returns_503_and_records_failure(
    client, template_payload
):
    from app.core.config import Settings, get_settings

    client.app.dependency_overrides[get_settings] = lambda: Settings(
        llm_provider="openai_compatible", llm_api_key=None
    )
    template_id = create_template(client, template_payload)
    response = client.post(
        "/api/v1/generations",
        json={
            "template_id": template_id,
            "variables": {"produto": "luminária", "publico": "leitores"},
        },
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "provider_unavailable"

    history = client.get("/api/v1/generations?status=failed")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["status"] == "failed"
