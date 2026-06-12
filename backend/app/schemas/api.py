from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

LeadStatus = Literal[
    "discovered",
    "enriched",
    "qualified",
    "creating_website",
    "draft_ready",
    "externally_imported",
    "email_drafted",
    "contacted",
    "replied",
    "follow_up_needed",
    "proposal_sent",
    "won",
    "lost",
    "do_not_contact",
    "archived",
]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SearchRunCreate(BaseModel):
    location_query: str
    name_query: str | None = None
    radius_km: float = Field(default=3, ge=0, le=50)
    categories: list[str] = Field(default_factory=list)
    excluded_categories: list[str] | None = None
    market_types: list[Literal["b2c", "b2b", "both", "unknown"]] = Field(default_factory=list)
    keywords: str | None = None
    max_results: int | None = Field(default=None, gt=0, le=200)
    search_depth: Literal["fast", "balanced", "deep"] = "balanced"


class LeadProfileOut(ORMModel):
    status: str
    opportunity_summary: str | None = None
    mission_summary: str | None = None
    review_sentiment_summary: str | None = None
    pain_points_json: list[str] = []
    recommended_angle: str | None = None
    market_type: str = "unknown"
    audience_notes: str | None = None
    last_contacted_at: datetime | None = None
    next_follow_up_at: datetime | None = None
    do_not_contact_reason: str | None = None
    notes: str | None = None


class SourceDocumentOut(ORMModel):
    id: int
    source_type: str
    source_url: str | None = None
    title: str | None = None
    content_text: str | None = None
    extracted_json: dict[str, Any] = {}
    confidence: str | None = None
    created_at: datetime


class ContactOut(ORMModel):
    id: int
    name: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    profile_url: str | None = None
    source_url: str | None = None
    contact_type: str
    confidence: str
    allowed_for_manual_contact: bool
    do_not_contact: bool
    created_at: datetime


class WebsiteProjectSummaryOut(ORMModel):
    id: int
    business_id: int
    status: str
    generation_mode: str
    project_name: str
    repo_path: str | None = None
    preview_url: str | None = None
    brief_markdown: str | None = None
    generated_copy_json: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class BusinessOut(ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    formatted_address: str | None = None
    lat: float | None = None
    lng: float | None = None
    website_url: str | None = None
    phone: str | None = None
    email: str | None = None
    osm_id: str | None = None
    primary_category: str | None = None
    categories_json: list[str] = []
    discovery_source: str
    lead_profile: LeadProfileOut | None = None
    contacts: list[ContactOut] = []
    source_documents: list[SourceDocumentOut] = []
    website_projects: list[WebsiteProjectSummaryOut] = []


class SearchRunOut(ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
    location_query: str
    center_lat: float | None = None
    center_lng: float | None = None
    radius_km: float
    country: str
    categories_json: list[str]
    keywords: str | None = None
    max_results: int
    search_depth: str
    provider_order_json: list[str]
    coverage_json: list[dict[str, Any]] = []
    provider_errors_json: list[dict[str, Any]] = []
    total_seen_count: int = 0
    new_added_count: int = 0
    duplicate_skipped_count: int = 0
    excluded_count: int = 0
    status: str
    error_message: str | None = None


class SearchRunResult(ORMModel):
    search_run: SearchRunOut
    businesses: list[BusinessOut]


class StatusUpdate(BaseModel):
    status: LeadStatus
    note: str | None = None
    next_follow_up_at: datetime | None = None


class JobOut(ORMModel):
    id: int
    type: str
    status: str
    payload_json: dict[str, Any]
    result_json: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class WebsiteProjectOut(WebsiteProjectSummaryOut):
    pass


class OutreachMessageOut(ORMModel):
    id: int
    business_id: int
    contact_id: int | None = None
    message_type: str
    status: str
    subject: str | None = None
    body: str
    language: str
    source_context_json: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class WebsiteImportIn(BaseModel):
    project_name: str
    repo_path: str | None = None
    preview_url: str | None = None
    notes: str | None = None


class OutreachDraftIn(BaseModel):
    language: Literal["it", "en"] = "it"
    contact_id: int | None = None


class MarkEmailSentIn(BaseModel):
    contact_id: int | None = None
    note: str | None = None
    next_follow_up_at: datetime | None = None


class ReceivedAnswerIn(BaseModel):
    message: str
    draft_reply: bool = True
    next_step: LeadStatus = "follow_up_needed"


class FollowUpIn(BaseModel):
    next_follow_up_at: datetime
    note: str | None = None


class DoNotContactIn(BaseModel):
    reason: str
    contact_id: int | None = None


class DraftReplyIn(BaseModel):
    language: Literal["it", "en"] = "it"


class ProviderSettingsOut(BaseModel):
    discovery_provider: str
    overpass_configured: bool
    web_search_backup_enabled: bool
    enrich_web_search_enabled: bool
    ai_key_configured: bool


class ProviderSettingsUpdate(BaseModel):
    web_search_backup_enabled: bool = False
