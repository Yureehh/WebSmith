from datetime import UTC, datetime

from sqlalchemy import JSON as SAJSON
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class SearchRun(TimestampMixin, Base):
    __tablename__ = "search_runs"
    __table_args__ = (Index("ix_search_runs_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    location_query: Mapped[str] = mapped_column(String(255))
    center_lat: Mapped[float | None] = mapped_column(Float)
    center_lng: Mapped[float | None] = mapped_column(Float)
    radius_km: Mapped[float] = mapped_column(Float, default=3)
    country: Mapped[str] = mapped_column(String(2), default="IT")
    categories_json: Mapped[list[str]] = mapped_column(SAJSON, default=list)
    keywords: Mapped[str | None] = mapped_column(String(255))
    max_results: Mapped[int] = mapped_column(Integer, default=20)
    search_depth: Mapped[str] = mapped_column(String(20), default="balanced")
    provider_order_json: Mapped[list[str]] = mapped_column(SAJSON, default=list)
    coverage_json: Mapped[list[dict]] = mapped_column(SAJSON, default=list)
    provider_errors_json: Mapped[list[dict]] = mapped_column(SAJSON, default=list)
    total_seen_count: Mapped[int] = mapped_column(Integer, default=0)
    new_added_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    excluded_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)


class Business(TimestampMixin, Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True)
    formatted_address: Mapped[str | None] = mapped_column(String(500))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    website_url: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    osm_id: Mapped[str | None] = mapped_column(String(255), index=True)
    primary_category: Mapped[str | None] = mapped_column(String(120))
    categories_json: Mapped[list[str]] = mapped_column(SAJSON, default=list)
    discovery_source: Mapped[str] = mapped_column(String(80), default="osm")

    lead_profile: Mapped["LeadProfile"] = relationship(back_populates="business", uselist=False)
    source_documents: Mapped[list["SourceDocument"]] = relationship(back_populates="business")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="business")
    website_projects: Mapped[list["WebsiteProject"]] = relationship(back_populates="business")


class LeadProfile(Base):
    __tablename__ = "lead_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), unique=True)
    status: Mapped[str] = mapped_column(String(60), default="discovered")
    opportunity_summary: Mapped[str | None] = mapped_column(Text)
    mission_summary: Mapped[str | None] = mapped_column(Text)
    review_sentiment_summary: Mapped[str | None] = mapped_column(Text)
    pain_points_json: Mapped[list[str]] = mapped_column(SAJSON, default=list)
    recommended_angle: Mapped[str | None] = mapped_column(Text)
    market_type: Mapped[str] = mapped_column(String(20), default="unknown")
    audience_notes: Mapped[str | None] = mapped_column(Text)
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    do_not_contact_reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    business: Mapped[Business] = relationship(back_populates="lead_profile")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(60))
    source_url: Mapped[str | None] = mapped_column(String(800))
    title: Mapped[str | None] = mapped_column(String(255))
    content_text: Mapped[str | None] = mapped_column(Text)
    extracted_json: Mapped[dict] = mapped_column(SAJSON, default=dict)
    confidence: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped[Business] = relationship(back_populates="source_documents")


class Contact(Base):
    __tablename__ = "contacts"
    # Unique index (not a table constraint) so SQLite can add it without a table rebuild.
    # NULL emails are treated as distinct by SQLite, so phone-only contacts never collide.
    __table_args__ = (
        Index("uq_contacts_business_email", "business_id", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(100))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    profile_url: Mapped[str | None] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(800))
    contact_type: Mapped[str] = mapped_column(String(40), default="unknown")
    confidence: Mapped[str] = mapped_column(String(20), default="low")
    allowed_for_manual_contact: Mapped[bool] = mapped_column(Boolean, default=True)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped[Business] = relationship(back_populates="contacts")


class WebsiteProject(TimestampMixin, Base):
    __tablename__ = "website_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    status: Mapped[str] = mapped_column(String(60), default="draft_ready")
    generation_mode: Mapped[str] = mapped_column(String(40), default="internal")
    project_name: Mapped[str] = mapped_column(String(255))
    repo_path: Mapped[str | None] = mapped_column(String(500))
    preview_url: Mapped[str | None] = mapped_column(String(500))
    brief_markdown: Mapped[str | None] = mapped_column(Text)
    generated_copy_json: Mapped[dict] = mapped_column(SAJSON, default=dict)

    business: Mapped[Business] = relationship(back_populates="website_projects")


class OutreachMessage(TimestampMixin, Base):
    __tablename__ = "outreach_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), index=True)
    message_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="draft")
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10), default="it")
    source_context_json: Mapped[dict] = mapped_column(SAJSON, default=dict)


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40), default="active")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    direction: Mapped[str] = mapped_column(String(20))
    body: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(40), default="manual_paste")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ComplianceEvent(Base):
    __tablename__ = "compliance_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(60))
    data_source_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProviderSetting(TimestampMixin, Base):
    __tablename__ = "provider_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    provider_order_json: Mapped[list[str]] = mapped_column(SAJSON, default=list)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="queued", index=True)
    payload_json: Mapped[dict] = mapped_column(SAJSON, default=dict)
    result_json: Mapped[dict | None] = mapped_column(SAJSON)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
