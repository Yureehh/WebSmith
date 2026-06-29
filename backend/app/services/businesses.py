from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import (
    Business,
    ComplianceEvent,
    Contact,
    Conversation,
    ConversationMessage,
    LeadProfile,
    OutreachMessage,
    SearchRun,
    SourceDocument,
)
from app.providers.ai import (
    ai_configured,
    complete_json,
    complete_text,
    require_ai,
    web_search_json,
)
from app.providers.discovery import (
    DEFAULT_EXCLUDED_CATEGORIES,
    DiscoveredBusiness,
    business_matches_activity_filters,
    discover_osm,
    normalize_name,
)
from app.providers.enrichment import fetch_public_site
from app.schemas.api import (
    DoNotContactIn,
    FollowUpIn,
    MarkEmailSentIn,
    ReceivedAnswerIn,
    SearchRunCreate,
    StatusUpdate,
)
from app.services.settings import get_provider_setting

ARCHIVE_STATUSES = {"won", "lost", "archived", "do_not_contact"}
DEFAULT_FRESH_LEAD_TARGET = 200
PROVIDER_FETCH_SAFETY_LIMIT = 500
WEB_DISCOVERY_FALLBACK_LIMIT = 25
B2C_CATEGORIES = {
    "bar",
    "cafe",
    "pub",
    "restaurant",
    "fast_food",
    "hotel",
    "guest_house",
    "bed_and_breakfast",
    "bakery",
    "pastry",
    "hairdresser",
    "beauty",
    "cosmetics",
    "fitness_centre",
    "sports",
    "dentist",
    "pharmacy",
    "optician",
    "clothes",
    "supermarket",
    "convenience",
}
B2B_CATEGORIES = {
    "lawyer",
    "architect",
    "car_repair",
    "mechanic",
}
BOTH_CATEGORIES = {
    "estate_agent",
    "real_estate",
    "clinic",
    "healthcare",
}


def classify_market(categories: list[str], business_name: str = "") -> tuple[str, str]:
    normalized = {normalize_name(category).replace(" ", "_") for category in categories if category}
    name = normalize_name(business_name)
    if normalized & B2C_CATEGORIES:
        return (
            "b2c",
            "Likely sells directly to local consumers or visitors.",
        )
    if normalized & BOTH_CATEGORIES:
        return (
            "both",
            "Likely serves both consumers and business/professional buyers.",
        )
    if normalized & B2B_CATEGORIES or any(
        token in name for token in ["studio", "agency", "agenzia"]
    ):
        return (
            "b2b",
            "Likely sells expertise or services to other businesses or high-intent clients.",
        )
    return (
        "unknown",
        "Audience needs manual validation.",
    )


def build_enrichment_search_query(business: Business) -> str:
    return (
        "Find the official website and relevant public sources for this Italian local business.\n"
        f"Business name: {business.name}\n"
        f"Category: {business.primary_category or 'unknown'}\n"
        f"Address/location: {business.formatted_address or 'unknown'}\n\n"
        "Return only valid JSON with this exact shape:\n"
        "{\n"
        '  "candidates": [\n'
        '    {"url": "...", "title": "...", "source_type": '
        '"official_website_candidate|social|external", "confidence": "high|medium|low", '
        '"reason": "..."}\n'
        "  ],\n"
        '  "best_website_url": "..." or null,\n'
        '  "conflict_warning": "..." or null\n'
        "}\n"
        "Prefer the business official domain. Use social/listing pages only as secondary sources. "
        "Only mark high confidence when name and location clearly match."
    )


def build_discovery_search_query(payload: SearchRunCreate, max_results: int) -> str:
    include = ", ".join(payload.categories) if payload.categories else "any public-facing type"
    exclude = ", ".join(payload.excluded_categories or DEFAULT_EXCLUDED_CATEGORIES)
    name_line = f"Business name filter: {payload.name_query}\n" if payload.name_query else ""
    return (
        "Find real local businesses, social enterprises, shops, studios, and service providers "
        "that are physically based in or very near this Italian search area.\n"
        f"Location: {payload.location_query}\n"
        f"Radius: {payload.radius_km} km\n"
        f"{name_line}"
        f"Include activity types: {include}\n"
        f"Exclude these types: {exclude}\n\n"
        f"Return up to {max_results} strong candidates. Prefer official websites and source-backed "
        "business pages. Do not return banks, public offices, post offices, churches, police, "
        "pharmacies, supermarkets, fuel stations, schools, hospitals, or irrelevant directories "
        "unless the business name filter clearly asks for one.\n\n"
        "Return only valid JSON with this exact shape:\n"
        "{\n"
        '  "businesses": [\n'
        '    {"name": "...", "website_url": "...", "phone": "...", "email": "...", '
        '"formatted_address": "...", "city": "...", "primary_category": "...", '
        '"categories": ["..."], "source_url": "...", "source_title": "...", '
        '"confidence": "high|medium|low", "reason": "..."}\n'
        "  ]\n"
        "}\n"
        "Only include candidates whose name and location are supported by the cited public source."
    )


def web_search_discovery(
    payload: SearchRunCreate, max_results: int
) -> tuple[list[DiscoveredBusiness], list[dict]]:
    try:
        result = web_search_json(
            build_discovery_search_query(payload, max_results),
            required_keys={"businesses"},
        )
    except HTTPException as exc:
        return [], [{"provider": "web_search_scraping", "error": str(exc.detail)}]

    discovered = []
    sources = result.get("_sources") or []
    source_by_url = {source.get("url"): source for source in sources if source.get("url")}
    for item in (result.get("businesses") or [])[:max_results]:
        name = as_text(item.get("name")).strip()
        if not name:
            continue
        categories = as_text_list(item.get("categories"))
        primary_category = as_text(item.get("primary_category")) or "web_search"
        candidate = DiscoveredBusiness(
            name=name,
            normalized_name=normalize_name(name),
            formatted_address=as_text(item.get("formatted_address")) or None,
            lat=None,
            lng=None,
            website_url=as_text(item.get("website_url")) or None,
            phone=as_text(item.get("phone")) or None,
            email=as_text(item.get("email")) or None,
            primary_category=primary_category,
            categories=categories or [primary_category],
            discovery_source="web_search",
        )
        excluded_categories = payload.excluded_categories or DEFAULT_EXCLUDED_CATEGORIES
        if not business_matches_activity_filters(
            candidate, payload.categories, excluded_categories
        ):
            continue
        normalized_name_query = normalize_name(payload.name_query or "")
        if normalized_name_query and normalized_name_query not in candidate.normalized_name:
            continue
        source_url = as_text(item.get("source_url")) or candidate.website_url
        source = source_by_url.get(source_url) or {}
        candidate.web_source_document = {
            "source_url": source_url,
            "title": as_text(item.get("source_title")) or source.get("title") or "Web discovery",
            "content_text": as_text(item.get("reason")) or "Found by WebSmith web discovery.",
            "extracted_json": {
                "candidate": item,
                "web_search_sources": sources,
                "confidence": item.get("confidence") or "low",
            },
            "confidence": item.get("confidence") or "low",
        }
        discovered.append(candidate)
    return discovered, []


def enrich_with_web_search(db: Session, business: Business) -> None:
    search_result = web_search_json(
        build_enrichment_search_query(business),
        required_keys={"candidates", "best_website_url", "conflict_warning"},
    )
    candidates = search_result.get("candidates") or []
    high_confidence_officials = [
        candidate
        for candidate in candidates
        if candidate.get("source_type") == "official_website_candidate"
        and candidate.get("confidence") == "high"
        and candidate.get("url")
    ]
    for candidate in candidates[:8]:
        db.add(
            SourceDocument(
                business_id=business.id,
                source_type=candidate.get("source_type") or "web_search",
                source_url=candidate.get("url"),
                title=candidate.get("title") or "Web search candidate",
                content_text=candidate.get("reason"),
                extracted_json={
                    "candidate": candidate,
                    "conflict_warning": search_result.get("conflict_warning"),
                    "web_search_sources": search_result.get("_sources") or [],
                },
                confidence=candidate.get("confidence") or "low",
            )
        )
    candidate_urls = {candidate.get("url") for candidate in candidates if candidate.get("url")}
    for source in (search_result.get("_sources") or [])[:12]:
        source_url = source.get("url")
        if not source_url or source_url in candidate_urls:
            continue
        db.add(
            SourceDocument(
                business_id=business.id,
                source_type="web_search",
                source_url=source_url,
                title=source.get("title") or "OpenAI web search source",
                content_text="Source consulted by OpenAI web search during enrichment.",
                extracted_json={
                    "web_search_source": source,
                    "conflict_warning": search_result.get("conflict_warning"),
                },
                confidence="medium",
            )
        )
    if not business.website_url and len(high_confidence_officials) == 1:
        business.website_url = high_confidence_officials[0]["url"]


def business_options():
    return (
        selectinload(Business.lead_profile),
        selectinload(Business.contacts),
        selectinload(Business.source_documents),
        selectinload(Business.website_projects),
    )


def get_business_or_404(db: Session, business_id: int) -> Business:
    business = db.scalar(
        select(Business).where(Business.id == business_id).options(*business_options())
    )
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


def ensure_profile(db: Session, business: Business) -> LeadProfile:
    if business.lead_profile:
        return business.lead_profile
    profile = LeadProfile(business_id=business.id)
    db.add(profile)
    db.flush()
    business.lead_profile = profile
    return profile


def upsert_contact(
    db: Session,
    business_id: int,
    *,
    email: str | None,
    phone: str | None,
    source_url: str | None,
    contact_type: str,
    confidence: str,
) -> None:
    """Add a contact, or enrich the existing one, respecting the (business_id, email) unique index.

    Re-running discovery/enrichment must never create duplicates or hit an IntegrityError.
    """
    if not email and not phone:
        return
    query = select(Contact).where(Contact.business_id == business_id)
    if email:
        existing = db.execute(query.where(Contact.email == email)).scalars().first()
    else:
        existing = (
            db.execute(query.where(Contact.email.is_(None), Contact.phone == phone))
            .scalars()
            .first()
        )
    if existing is not None:
        existing.phone = existing.phone or phone
        existing.source_url = existing.source_url or source_url
        if confidence == "medium":
            existing.confidence = "medium"
        return
    db.add(
        Contact(
            business_id=business_id,
            email=email,
            phone=phone,
            source_url=source_url,
            contact_type=contact_type,
            confidence=confidence,
        )
    )


def add_event(
    db: Session,
    business_id: int,
    event_type: str,
    note: str | None = None,
    contact_id: int | None = None,
) -> None:
    db.add(
        ComplianceEvent(
            business_id=business_id,
            contact_id=contact_id,
            event_type=event_type,
            data_source_note=note,
        )
    )


def as_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(item) for item in value if item is not None)
    if isinstance(value, dict):
        return "\n".join(f"{key}: {item}" for key, item in value.items())
    return str(value)


def as_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str):
        return [value]
    return [str(value)]


def normalize_market_type(value: Any, fallback: str) -> str:
    market_type = as_text(value)
    if market_type in {"b2c", "b2b", "both", "unknown"}:
        return market_type
    return fallback


async def create_search_run(
    db: Session, payload: SearchRunCreate
) -> tuple[SearchRun, list[Business]]:
    provider_setting = get_provider_setting(db)
    provider_order = provider_setting.provider_order_json or ["osm_overpass"]
    fresh_lead_target = payload.max_results or DEFAULT_FRESH_LEAD_TARGET
    run = SearchRun(
        location_query=payload.location_query,
        radius_km=payload.radius_km,
        categories_json=payload.categories,
        keywords=payload.name_query or payload.keywords,
        max_results=fresh_lead_target,
        search_depth=payload.search_depth,
        provider_order_json=provider_order,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    center = (None, None)
    discovered = []
    coverage: list[dict] = []
    provider_errors: list[dict] = []
    total_seen_count = 0
    excluded_count = 0
    excluded_categories = (
        payload.excluded_categories
        if payload.excluded_categories is not None
        else DEFAULT_EXCLUDED_CATEGORIES
    )
    provider_fetch_limit = min(
        max(fresh_lead_target * 3, fresh_lead_target + 80),
        PROVIDER_FETCH_SAFETY_LIMIT,
    )
    for provider in provider_order:
        remaining_discovery_slots = max(fresh_lead_target - len(discovered), 0)
        if provider == "osm_overpass":
            discovery_result = await discover_osm(
                payload.location_query,
                payload.radius_km,
                provider_fetch_limit,
                payload.categories,
                excluded_categories,
                payload.keywords,
                payload.name_query,
                payload.search_depth,
            )
            center = discovery_result.center
            discovered = discovery_result.businesses
            coverage = discovery_result.coverage
            provider_errors = discovery_result.provider_errors
            total_seen_count = discovery_result.total_seen_count
            excluded_count = discovery_result.excluded_count
        elif provider == "web_search_scraping" and remaining_discovery_slots > 0:
            web_limit = min(remaining_discovery_slots, WEB_DISCOVERY_FALLBACK_LIMIT)
            web_discovered, web_errors = web_search_discovery(payload, web_limit)
            discovered.extend(web_discovered)
            provider_errors.extend(web_errors)
            total_seen_count += len(web_discovered)
    run.center_lat, run.center_lng = center
    businesses = []
    duplicate_skipped_count = 0
    for item in discovered:
        if len(businesses) >= fresh_lead_target:
            break
        existing = None
        if item.osm_id:
            existing = db.scalar(select(Business).where(Business.osm_id == item.osm_id))
        if existing is None and item.website_url and item.discovery_source == "web_search":
            existing = db.scalar(select(Business).where(Business.website_url == item.website_url))
        if existing is None:
            existing = db.scalar(
                select(Business).where(
                    Business.normalized_name == item.normalized_name,
                    Business.formatted_address == item.formatted_address,
                )
            )
        if existing is not None:
            duplicate_skipped_count += 1
            continue
        category_values = [item.primary_category or "", *(item.categories or [])]
        market_type, audience_notes = classify_market(category_values, item.name)
        if payload.market_types and market_type not in payload.market_types:
            excluded_count += 1
            continue
        existing = Business(
            name=item.name,
            normalized_name=item.normalized_name,
            formatted_address=item.formatted_address,
            lat=item.lat,
            lng=item.lng,
            website_url=item.website_url,
            phone=item.phone,
            email=item.email,
            osm_id=item.osm_id,
            primary_category=item.primary_category,
            categories_json=item.categories or [],
            discovery_source=item.discovery_source,
        )
        db.add(existing)
        db.flush()
        profile = LeadProfile(
            business_id=existing.id,
            market_type=market_type,
            audience_notes=audience_notes,
        )
        db.add(profile)
        existing.lead_profile = profile
        upsert_contact(
            db,
            existing.id,
            email=existing.email,
            phone=existing.phone,
            source_url=item.website_url,
            contact_type="generic_business",
            confidence="medium" if item.discovery_source == "web_search" else "low",
        )
        add_event(db, existing.id, "data_collected", "Business discovered via provider search.")
        web_source_document = getattr(item, "web_source_document", None)
        if web_source_document:
            db.add(
                SourceDocument(
                    business_id=existing.id,
                    source_type="web_search",
                    source_url=web_source_document["source_url"],
                    title=web_source_document["title"],
                    content_text=web_source_document["content_text"],
                    extracted_json=web_source_document["extracted_json"],
                    confidence=web_source_document["confidence"],
                )
            )
        if profile.status in ARCHIVE_STATUSES:
            continue
        businesses.append(existing)
    run.coverage_json = coverage
    run.provider_errors_json = provider_errors
    run.total_seen_count = total_seen_count or len(discovered)
    run.new_added_count = len(businesses)
    run.duplicate_skipped_count = duplicate_skipped_count
    run.excluded_count = excluded_count
    run.status = "completed" if businesses else "completed_empty"
    run.error_message = "\n".join(error.get("error", "") for error in provider_errors) or None
    db.commit()
    return run, businesses


def list_businesses(db: Session) -> list[Business]:
    businesses = list(select_businesses(db).scalars())
    changed = False
    for business in businesses:
        profile = ensure_profile(db, business)
        if profile.market_type == "unknown" and not profile.audience_notes:
            category_values = [business.primary_category or "", *(business.categories_json or [])]
            market_type, audience_notes = classify_market(category_values, business.name)
            profile.market_type = market_type
            profile.audience_notes = audience_notes
            changed = True
    if changed:
        db.commit()
        businesses = list(select_businesses(db).scalars())
    return businesses


def select_businesses(db: Session):
    return db.execute(
        select(Business).options(*business_options()).order_by(Business.created_at.desc())
    )


def update_status(db: Session, business_id: int, payload: StatusUpdate) -> Business:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    profile.status = payload.status
    if payload.note:
        profile.notes = "\n\n".join(filter(None, [profile.notes, payload.note]))
    profile.next_follow_up_at = payload.next_follow_up_at
    add_event(
        db,
        business.id,
        "manual_send_marked" if payload.status == "contacted" else "data_collected",
        payload.note,
    )
    db.commit()
    return get_business_or_404(db, business_id)


def enrich_business(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    business = get_business_or_404(db, int(payload["business_id"]))
    profile = ensure_profile(db, business)
    if not business.website_url and ai_configured():
        enrich_with_web_search(db, business)
        db.flush()
    site = fetch_public_site(business.website_url)
    text = site["content_text"]
    extracted = site["extracted"]
    summary = complete_json(
        system="You enrich Italian local business leads for manual website outreach.",
        user=(
            f"Business: {business.name}\n"
            f"Category: {business.primary_category}\n"
            f"Address: {business.formatted_address}\n"
            f"Website text: {text[:5000]}"
            "\n\nReturn JSON with keys: opportunity_summary, mission_summary, "
            "review_sentiment_summary, pain_points, recommended_angle, market_type, "
            "audience_notes."
        ),
        required_keys={
            "opportunity_summary",
            "mission_summary",
            "review_sentiment_summary",
            "pain_points",
            "recommended_angle",
            "market_type",
            "audience_notes",
        },
    )
    sources = site.get("sources") or [
        {
            "source_url": site["source_url"],
            "title": site["title"],
            "content_text": text,
            "extracted": extracted,
            "confidence": site["confidence"],
        }
    ]
    for source in sources:
        db.add(
            SourceDocument(
                business_id=business.id,
                source_type="website" if business.website_url else "external",
                source_url=source["source_url"],
                title=source["title"],
                content_text=source["content_text"],
                extracted_json=source["extracted"],
                confidence=source["confidence"],
            )
        )
    emails = extracted.get("emails", [])
    phones = extracted.get("phones", [])
    if emails and not business.email:
        business.email = emails[0]
    if phones and not business.phone:
        business.phone = phones[0]
    upsert_contact(
        db,
        business.id,
        email=business.email,
        phone=business.phone,
        source_url=site["source_url"],
        contact_type="generic_business",
        confidence="medium",
    )
    profile.status = "enriched"
    profile.opportunity_summary = as_text(summary.get("opportunity_summary"))
    profile.mission_summary = as_text(summary.get("mission_summary"))
    profile.review_sentiment_summary = as_text(summary.get("review_sentiment_summary"))
    profile.pain_points_json = as_text_list(summary.get("pain_points"))
    profile.recommended_angle = as_text(summary.get("recommended_angle"))
    profile.market_type = normalize_market_type(summary.get("market_type"), profile.market_type)
    profile.audience_notes = as_text(summary.get("audience_notes"))
    add_event(db, business.id, "data_collected", "User-triggered enrichment completed.")
    db.commit()
    return {"business_id": business.id, "status": profile.status}


def draft_outreach(
    db: Session, business_id: int, language: str, contact_id: int | None
) -> OutreachMessage:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    if profile.status == "do_not_contact" or profile.do_not_contact_reason:
        raise HTTPException(status_code=409, detail="Lead is marked do not contact.")
    if contact_id is not None:
        contact = db.get(Contact, contact_id)
        if contact is None or contact.business_id != business.id:
            raise HTTPException(status_code=404, detail="Contact not found for this lead.")
    require_ai()
    subject = (
        f"Una presenza online piu chiara per {business.name}"
        if language == "it"
        else f"A clearer online presence for {business.name}"
    )
    body = complete_text(
        system="You write polite, specific, non-spammy manual outreach emails in Italian.",
        user=(
            f"Write a first email from Juri/WebSmith to {business.name}. "
            f"Observation: {business.website_url or business.formatted_address}. "
            "Never insult the current website. Include simple opt-out wording."
        ),
    )
    message = OutreachMessage(
        business_id=business.id,
        contact_id=contact_id,
        message_type="first_email",
        status="draft",
        subject=subject,
        body=body,
        language=language,
        source_context_json={"observation": business.website_url or business.formatted_address},
    )
    db.add(message)
    profile.status = "email_drafted"
    add_event(db, business.id, "draft_generated", "Manual outreach draft generated.", contact_id)
    db.commit()
    db.refresh(message)
    return message


def mark_email_sent(db: Session, business_id: int, payload: MarkEmailSentIn) -> Business:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    profile.status = "contacted"
    profile.last_contacted_at = datetime.now(UTC)
    profile.next_follow_up_at = payload.next_follow_up_at
    add_event(db, business.id, "manual_send_marked", payload.note, payload.contact_id)
    db.commit()
    return get_business_or_404(db, business_id)


def received_answer(db: Session, business_id: int, payload: ReceivedAnswerIn) -> dict[str, Any]:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    profile.status = payload.next_step
    conversation = db.scalar(select(Conversation).where(Conversation.business_id == business.id))
    if conversation is None:
        conversation = Conversation(
            business_id=business.id, title=f"Conversation with {business.name}"
        )
        db.add(conversation)
        db.flush()
    db.add(
        ConversationMessage(
            conversation_id=conversation.id,
            direction="client",
            body=payload.message,
            source="manual_paste",
        )
    )
    draft_id = None
    if payload.draft_reply:
        draft = ConversationMessage(
            conversation_id=conversation.id,
            direction="draft",
            body=complete_text(
                system="You draft short polite replies for manual business outreach in Italian.",
                user=f"Client replied:\n{payload.message}\n\nDraft a helpful next reply.",
            ),
            source="generated",
        )
        db.add(draft)
        db.flush()
        draft_id = draft.id
    add_event(db, business.id, "reply_pasted", "Client reply pasted manually.")
    db.commit()
    return {
        "conversation_id": conversation.id,
        "draft_message_id": draft_id,
        "status": profile.status,
    }


def set_follow_up(db: Session, business_id: int, payload: FollowUpIn) -> Business:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    profile.status = "follow_up_needed"
    profile.next_follow_up_at = payload.next_follow_up_at
    if payload.note:
        profile.notes = "\n\n".join(filter(None, [profile.notes, payload.note]))
    db.commit()
    return get_business_or_404(db, business_id)


def do_not_contact(db: Session, business_id: int, payload: DoNotContactIn) -> Business:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    profile.status = "do_not_contact"
    profile.do_not_contact_reason = payload.reason
    if payload.contact_id:
        contact = db.get(Contact, payload.contact_id)
        if contact:
            contact.do_not_contact = True
            contact.allowed_for_manual_contact = False
    add_event(db, business.id, "do_not_contact_set", payload.reason, payload.contact_id)
    db.commit()
    return get_business_or_404(db, business_id)
