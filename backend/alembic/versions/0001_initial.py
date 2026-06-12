"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "search_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        *timestamps(),
        sa.Column("location_query", sa.String(255), nullable=False),
        sa.Column("center_lat", sa.Float()),
        sa.Column("center_lng", sa.Float()),
        sa.Column("radius_km", sa.Float(), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("categories_json", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.String(255)),
        sa.Column("max_results", sa.Integer(), nullable=False),
        sa.Column("search_depth", sa.String(20), nullable=False),
        sa.Column("provider_order_json", sa.JSON(), nullable=False),
        sa.Column("coverage_json", sa.JSON(), nullable=False),
        sa.Column("provider_errors_json", sa.JSON(), nullable=False),
        sa.Column("total_seen_count", sa.Integer(), nullable=False),
        sa.Column("new_added_count", sa.Integer(), nullable=False),
        sa.Column("duplicate_skipped_count", sa.Integer(), nullable=False),
        sa.Column("excluded_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer(), primary_key=True),
        *timestamps(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.Column("formatted_address", sa.String(500)),
        sa.Column("lat", sa.Float()),
        sa.Column("lng", sa.Float()),
        sa.Column("website_url", sa.String(500)),
        sa.Column("phone", sa.String(100)),
        sa.Column("email", sa.String(255)),
        sa.Column("osm_id", sa.String(255)),
        sa.Column("primary_category", sa.String(120)),
        sa.Column("categories_json", sa.JSON(), nullable=False),
        sa.Column("discovery_source", sa.String(80), nullable=False),
    )
    op.create_index("ix_businesses_name", "businesses", ["name"])
    op.create_index("ix_businesses_normalized_name", "businesses", ["normalized_name"])
    op.create_index("ix_businesses_osm_id", "businesses", ["osm_id"])
    op.create_table(
        "lead_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id"), unique=True),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("opportunity_summary", sa.Text()),
        sa.Column("mission_summary", sa.Text()),
        sa.Column("review_sentiment_summary", sa.Text()),
        sa.Column("pain_points_json", sa.JSON(), nullable=False),
        sa.Column("recommended_angle", sa.Text()),
        sa.Column("market_type", sa.String(20), nullable=False),
        sa.Column("audience_notes", sa.Text()),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True)),
        sa.Column("next_follow_up_at", sa.DateTime(timezone=True)),
        sa.Column("do_not_contact_reason", sa.Text()),
        sa.Column("notes", sa.Text()),
    )
    op.create_table(
        "source_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id")),
        sa.Column("source_type", sa.String(60), nullable=False),
        sa.Column("source_url", sa.String(800)),
        sa.Column("title", sa.String(255)),
        sa.Column("content_text", sa.Text()),
        sa.Column("extracted_json", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.String(30)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id")),
        sa.Column("name", sa.String(255)),
        sa.Column("role", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(100)),
        sa.Column("linkedin_url", sa.String(500)),
        sa.Column("profile_url", sa.String(500)),
        sa.Column("source_url", sa.String(800)),
        sa.Column("contact_type", sa.String(40), nullable=False),
        sa.Column("confidence", sa.String(20), nullable=False),
        sa.Column("allowed_for_manual_contact", sa.Boolean(), nullable=False),
        sa.Column("do_not_contact", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "website_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        *timestamps(),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id")),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("generation_mode", sa.String(40), nullable=False),
        sa.Column("project_name", sa.String(255), nullable=False),
        sa.Column("repo_path", sa.String(500)),
        sa.Column("preview_url", sa.String(500)),
        sa.Column("brief_markdown", sa.Text()),
        sa.Column("generated_copy_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "outreach_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        *timestamps(),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id")),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("contacts.id")),
        sa.Column("message_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("subject", sa.String(255)),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("language", sa.String(10), nullable=False),
        sa.Column("source_context_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        *timestamps(),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
    )
    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id")),
        sa.Column("direction", sa.String(20), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "compliance_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("business_id", sa.Integer(), sa.ForeignKey("businesses.id")),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("contacts.id")),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("data_source_note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "provider_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        *timestamps(),
        sa.Column("provider", sa.String(80), unique=True, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("provider_order_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(80), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON()),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    for table in [
        "jobs",
        "provider_settings",
        "compliance_events",
        "conversation_messages",
        "conversations",
        "outreach_messages",
        "website_projects",
        "contacts",
        "source_documents",
        "lead_profiles",
        "businesses",
        "search_runs",
    ]:
        op.drop_table(table)
