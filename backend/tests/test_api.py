from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.providers.discovery import (
    DiscoveredBusiness,
    DiscoveryResult,
    business_matches_activity_filters,
)


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("app.providers.ai.settings.openai_api_key", None)

    async def fake_discover_osm(
        location_query,
        radius_km,
        max_results,
        categories,
        excluded_categories,
        keywords,
        name_query=None,
        search_depth="balanced",
    ):
        del location_query, radius_km, max_results, keywords, search_depth
        businesses = [
            DiscoveredBusiness(
                name=name,
                normalized_name=name.lower(),
                formatted_address=f"Via Test {index}, Milano",
                lat=45.4642 + index / 1000,
                lng=9.19 + index / 1000,
                website_url=None if category == "hotel" else "https://example.it",
                osm_id=f"test-osm-{index}",
                primary_category=category,
                categories=[category],
            )
            for index, (name, category) in enumerate(
                [
                    ("Demo Bar Milano", "bar"),
                    ("Demo Fuel Milano", "fuel"),
                    ("Demo Hotel Milano", "hotel"),
                    ("Demo Dentist Milano", "dentist"),
                    ("Demo Cafe Milano", "cafe"),
                    ("Demo Bank Milano", "bank"),
                    ("Demo Poste Milano", "post_office"),
                    ("Demo Pharmacy Milano", "pharmacy"),
                    ("Demo Lawyer Milano", "lawyer"),
                ],
                start=1,
            )
        ]
        filtered = [
            business
            for business in businesses
            if business_matches_activity_filters(business, categories, excluded_categories)
            and (not name_query or name_query.lower() in business.name.lower())
        ]
        return DiscoveryResult(
            center=(45.4642, 9.19),
            businesses=filtered,
            coverage=[
                {
                    "id": "center",
                    "label": "Center",
                    "lat": 45.4642,
                    "lng": 9.19,
                    "radius_km": 2,
                    "status": "success",
                    "result_count": len(filtered),
                    "error": None,
                }
            ],
            provider_errors=[],
            total_seen_count=len(businesses),
            excluded_count=len(businesses) - len(filtered),
        )

    monkeypatch.setattr("app.services.businesses.discover_osm", fake_discover_osm)
    monkeypatch.setattr(
        "app.services.website_projects.WEBSITE_PROJECTS_DIR", tmp_path / "website-projects"
    )

    def override_get_db() -> Generator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_business(client: TestClient) -> int:
    response = client.post(
        "/api/search-runs",
        json={"location_query": "Milano", "radius_km": 2, "keywords": "bar", "max_results": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["search_run"]["status"] == "completed"
    return data["businesses"][0]["id"]


def test_search_without_key_uses_fallback(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.get(f"/api/businesses/{business_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["discovery_source"] == "osm"
    assert {"rating", "review_count", "business_status", "osm_type"}.isdisjoint(data)


def test_search_caps_new_leads_and_skips_known(client: TestClient) -> None:
    first = client.post(
        "/api/search-runs",
        json={"location_query": "Milano", "radius_km": 2, "max_results": 2},
    )
    assert first.status_code == 200
    assert len(first.json()["businesses"]) == 2

    second = client.post(
        "/api/search-runs",
        json={"location_query": "Milano", "radius_km": 2, "max_results": 2},
    )
    assert second.status_code == 200
    assert len(second.json()["businesses"]) == 2
    assert {business["id"] for business in first.json()["businesses"]}.isdisjoint(
        {business["id"] for business in second.json()["businesses"]}
    )

    businesses = client.get("/api/businesses")
    assert businesses.status_code == 200
    assert len(businesses.json()) == 4
    assert {business["primary_category"] for business in businesses.json()}.isdisjoint(
        {"bank", "fuel"}
    )
    assert first.json()["search_run"]["coverage_json"][0]["status"] == "success"
    assert first.json()["search_run"]["new_added_count"] == 2


def test_search_without_max_results_uses_fresh_target_and_known_do_not_count(
    client: TestClient,
) -> None:
    first = client.post(
        "/api/search-runs",
        json={"location_query": "Milano", "radius_km": 2, "max_results": 2},
    )
    assert first.status_code == 200
    for business in first.json()["businesses"]:
        client.post(f"/api/businesses/{business['id']}/status", json={"status": "archived"})

    second = client.post(
        "/api/search-runs",
        json={"location_query": "Milano", "radius_km": 2},
    )
    assert second.status_code == 200
    data = second.json()
    assert data["search_run"]["max_results"] == 200
    assert data["search_run"]["duplicate_skipped_count"] == 2
    assert data["search_run"]["new_added_count"] == 3
    assert {business["id"] for business in first.json()["businesses"]}.isdisjoint(
        {business["id"] for business in data["businesses"]}
    )


def test_search_activity_include_and_exclude_filters(client: TestClient) -> None:
    response = client.post(
        "/api/search-runs",
        json={
            "location_query": "Milano",
            "radius_km": 2,
            "max_results": 5,
            "categories": ["bar", "fuel"],
            "excluded_categories": ["fuel"],
        },
    )
    assert response.status_code == 200
    businesses = response.json()["businesses"]
    assert [business["primary_category"] for business in businesses] == ["bar", "cafe"]
    assert set(businesses[0]["lead_profile"]) == {
        "status",
        "opportunity_summary",
        "mission_summary",
        "review_sentiment_summary",
        "pain_points_json",
        "recommended_angle",
        "market_type",
        "audience_notes",
        "last_contacted_at",
        "next_follow_up_at",
        "do_not_contact_reason",
        "notes",
    }
    assert businesses[0]["lead_profile"]["market_type"] == "b2c"


def test_default_exclusions_skip_post_offices_and_pharmacies_but_not_lawyers(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/search-runs",
        json={"location_query": "Milano", "radius_km": 2, "max_results": 20},
    )
    assert response.status_code == 200
    categories = {business["primary_category"] for business in response.json()["businesses"]}
    assert "post_office" not in categories
    assert "pharmacy" not in categories
    assert "lawyer" in categories


def test_search_name_filter(client: TestClient) -> None:
    response = client.post(
        "/api/search-runs",
        json={
            "location_query": "Milano",
            "radius_km": 2,
            "max_results": 5,
            "name_query": "Cafe",
            "market_types": [],
        },
    )
    assert response.status_code == 200
    assert [business["name"] for business in response.json()["businesses"]] == ["Demo Cafe Milano"]


def test_web_search_backup_supplements_osm_discovery(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    client.put("/api/settings/providers", json={"web_search_backup_enabled": True})

    def fake_web_search_json(query, required_keys=None):
        assert "Forlì" in query
        assert required_keys == {"businesses"}
        return {
            "businesses": [
                {
                    "name": "CavaRei Impresa Sociale",
                    "website_url": "https://cavarei.it/",
                    "phone": "+39 0543 31094",
                    "email": "cavarei@cavarei.it",
                    "formatted_address": "Via Domenico Bazzoli, 8, 47122 Forlì",
                    "city": "Forlì",
                    "primary_category": "impresa sociale",
                    "categories": ["impresa sociale", "servizi disabilità"],
                    "source_url": "https://cavarei.it/contatti/",
                    "source_title": "Contatti - CavaRei Impresa Sociale",
                    "confidence": "high",
                    "reason": "Official site confirms name, address, phone, and email.",
                }
            ],
            "_sources": [
                {
                    "url": "https://cavarei.it/contatti/",
                    "title": "Contatti - CavaRei Impresa Sociale",
                    "source_kind": "url_citation",
                }
            ],
        }

    monkeypatch.setattr("app.services.businesses.web_search_json", fake_web_search_json)
    response = client.post(
        "/api/search-runs",
        json={"location_query": "Forlì", "radius_km": 3, "max_results": 10, "market_types": []},
    )
    assert response.status_code == 200
    businesses = response.json()["businesses"]
    cavarei = next(
        business for business in businesses if business["name"] == "CavaRei Impresa Sociale"
    )
    assert cavarei["discovery_source"] == "web_search"
    assert cavarei["website_url"] == "https://cavarei.it/"
    assert cavarei["phone"] == "+39 0543 31094"
    assert cavarei["email"] == "cavarei@cavarei.it"

    detail = client.get(f"/api/businesses/{cavarei['id']}").json()
    assert detail["contacts"][0]["email"] == "cavarei@cavarei.it"
    assert detail["source_documents"][0]["source_type"] == "web_search"


def test_activity_filter_helper_matches_aliases_and_manual_names() -> None:
    charging_station = DiscoveredBusiness(
        name="Fast Charge Milano",
        normalized_name="fast charge milano",
        formatted_address=None,
        lat=None,
        lng=None,
        primary_category="charging_station",
        categories=["charging_station"],
    )
    vegan_studio = DiscoveredBusiness(
        name="Vegan Studio Milano",
        normalized_name="vegan studio milano",
        formatted_address=None,
        lat=None,
        lng=None,
        primary_category="shop",
        categories=["shop"],
    )

    assert not business_matches_activity_filters(charging_station, [], ["fuel"])
    assert business_matches_activity_filters(vegan_studio, ["vegan"], [])


def test_do_not_contact_blocks_outreach(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.post(
        f"/api/businesses/{business_id}/do-not-contact",
        json={"reason": "Asked not to be contacted"},
    )
    assert response.status_code == 200
    response = client.post(f"/api/businesses/{business_id}/draft-outreach", json={"language": "it"})
    assert response.status_code == 409


def test_mark_email_sent_updates_status(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.post(f"/api/businesses/{business_id}/mark-email-sent", json={"note": "Sent"})
    assert response.status_code == 200
    assert response.json()["lead_profile"]["status"] == "contacted"


def test_received_answer_creates_conversation_and_draft(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.post(
        f"/api/businesses/{business_id}/received-answer",
        json={"message": "Interessante", "draft_reply": False, "next_step": "follow_up_needed"},
    )
    assert response.status_code == 200
    assert response.json()["conversation_id"]
    assert response.json()["draft_message_id"] is None


def test_website_generation_creates_handoff_workspace(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.post(f"/api/businesses/{business_id}/generate-website")
    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    result = response.json()["result_json"]
    assert result["status"] == "draft_ready"
    assert "website-projects" in result["repo_path"]
    project_path = Path(result["repo_path"])
    assert (project_path / "BUILD_BRIEF.md").exists()
    assert (project_path / "SOURCE_INDEX.md").exists()
    assert (project_path / "CLIENT_CHECKLIST.md").exists()
    assert (project_path / "source_documents").exists()
    assert not (project_path / "REQUEST_FOR_CLAUDE_CODE.md").exists()


def test_enrich_with_web_search_updates_high_confidence_website(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    response = client.post(
        "/api/search-runs",
        json={
            "location_query": "Milano",
            "radius_km": 2,
            "max_results": 5,
            "categories": ["hotel"],
            "market_types": [],
        },
    )
    business_id = response.json()["businesses"][0]["id"]

    def fake_web_search_json(query, required_keys=None):
        del query, required_keys
        return {
            "candidates": [
                {
                    "url": "https://demo-bar.example",
                    "title": "Demo Bar Milano",
                    "source_type": "official_website_candidate",
                    "confidence": "high",
                    "reason": "Name and city match.",
                }
            ],
            "best_website_url": "https://demo-bar.example",
            "conflict_warning": None,
            "_sources": [
                {
                    "url": "https://listing.example/demo-bar",
                    "title": "Listing for Demo Bar",
                    "source_kind": "url_citation",
                }
            ],
        }

    def fake_complete_json(*args, **kwargs):
        del args, kwargs
        return {
            "opportunity_summary": "Useful local site opportunity.",
            "mission_summary": "Unknown.",
            "review_sentiment_summary": "Unknown.",
            "pain_points": ["No clear website content."],
            "recommended_angle": "Make contact and services clearer.",
            "market_type": "b2c",
            "audience_notes": "Local consumers.",
        }

    monkeypatch.setattr("app.services.businesses.ai_configured", lambda: True)
    monkeypatch.setattr("app.services.businesses.web_search_json", fake_web_search_json)
    monkeypatch.setattr("app.services.businesses.complete_json", fake_complete_json)
    response = client.post(f"/api/businesses/{business_id}/enrich")
    assert response.status_code == 200
    business = client.get(f"/api/businesses/{business_id}").json()
    assert business["website_url"] == "https://demo-bar.example"
    assert any(
        source["source_type"] == "official_website_candidate"
        for source in business["source_documents"]
    )
    assert any(source["source_type"] == "web_search" for source in business["source_documents"])


def test_enrich_coerces_list_audience_notes(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    response = client.post(
        "/api/search-runs",
        json={
            "location_query": "Milano",
            "radius_km": 2,
            "max_results": 5,
            "categories": ["bar"],
            "market_types": [],
        },
    )
    business_id = response.json()["businesses"][0]["id"]

    def fake_complete_json(*args, **kwargs):
        del args, kwargs
        return {
            "opportunity_summary": "Strong local lead.",
            "mission_summary": ["Local service", "Personal support"],
            "review_sentiment_summary": "Unknown.",
            "pain_points": "No known website.",
            "recommended_angle": "Build trust and collect inquiries.",
            "market_type": "local_service",
            "audience_notes": ["Home sellers", "Local buyers"],
        }

    monkeypatch.setattr("app.services.businesses.complete_json", fake_complete_json)
    response = client.post(f"/api/businesses/{business_id}/enrich")
    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    business = client.get(f"/api/businesses/{business_id}").json()
    profile = business["lead_profile"]
    assert profile["status"] == "enriched"
    assert profile["market_type"] == "b2c"
    assert profile["audience_notes"] == "Home sellers\nLocal buyers"
    assert profile["pain_points_json"] == ["No known website."]


def test_failed_job_rolls_back_before_recording_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    business_id = create_business(client)

    def fake_complete_json(*args, **kwargs):
        del args, kwargs
        raise RuntimeError("AI exploded")

    monkeypatch.setattr("app.services.businesses.complete_json", fake_complete_json)
    response = client.post(f"/api/businesses/{business_id}/enrich")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "AI exploded" in data["error"]


def test_enrich_with_conflicting_web_search_candidates_does_not_overwrite(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    response = client.post(
        "/api/search-runs",
        json={
            "location_query": "Milano",
            "radius_km": 2,
            "max_results": 5,
            "categories": ["hotel"],
            "market_types": [],
        },
    )
    business_id = response.json()["businesses"][0]["id"]

    def fake_web_search_json(query, required_keys=None):
        del query, required_keys
        return {
            "candidates": [
                {
                    "url": "https://one.example",
                    "title": "Demo Hotel Milano",
                    "source_type": "official_website_candidate",
                    "confidence": "high",
                    "reason": "Name and city match.",
                },
                {
                    "url": "https://two.example",
                    "title": "Demo Hotel Milano",
                    "source_type": "official_website_candidate",
                    "confidence": "high",
                    "reason": "Name and city match.",
                },
            ],
            "best_website_url": None,
            "conflict_warning": "Two high-confidence candidates.",
        }

    def fake_complete_json(*args, **kwargs):
        del args, kwargs
        return {
            "opportunity_summary": "Needs manual confirmation.",
            "mission_summary": "Unknown.",
            "review_sentiment_summary": "Unknown.",
            "pain_points": [],
            "recommended_angle": "Confirm official site first.",
            "market_type": "b2c",
            "audience_notes": "Local consumers.",
        }

    monkeypatch.setattr("app.services.businesses.ai_configured", lambda: True)
    monkeypatch.setattr("app.services.businesses.web_search_json", fake_web_search_json)
    monkeypatch.setattr("app.services.businesses.complete_json", fake_complete_json)
    response = client.post(f"/api/businesses/{business_id}/enrich")
    assert response.status_code == 200
    business = client.get(f"/api/businesses/{business_id}").json()
    assert business["website_url"] is None
    assert (
        len(
            [
                source
                for source in business["source_documents"]
                if source["source_type"] == "official_website_candidate"
            ]
        )
        == 2
    )


def test_website_import(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.post(
        f"/api/businesses/{business_id}/import-website",
        json={"project_name": "Imported site", "preview_url": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.json()["generation_mode"] == "external_import"


def test_ai_received_answer_draft_requires_key(client: TestClient) -> None:
    business_id = create_business(client)
    response = client.post(
        f"/api/businesses/{business_id}/received-answer",
        json={"message": "Interessante", "draft_reply": True, "next_step": "follow_up_needed"},
    )
    assert response.status_code == 503
