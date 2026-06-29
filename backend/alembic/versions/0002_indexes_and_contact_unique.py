"""indexes on foreign keys + contact email uniqueness

Revision ID: 0002_indexes_and_contact_unique
Revises: 0001_initial
Create Date: 2026-06-29
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_indexes_and_contact_unique"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (index_name, table, column) — names match SQLAlchemy's index=True convention so the ORM
# and the database agree.
_INDEXES: list[tuple[str, str, str]] = [
    ("ix_source_documents_business_id", "source_documents", "business_id"),
    ("ix_contacts_business_id", "contacts", "business_id"),
    ("ix_website_projects_business_id", "website_projects", "business_id"),
    ("ix_outreach_messages_business_id", "outreach_messages", "business_id"),
    ("ix_outreach_messages_contact_id", "outreach_messages", "contact_id"),
    ("ix_conversations_business_id", "conversations", "business_id"),
    ("ix_conversation_messages_conversation_id", "conversation_messages", "conversation_id"),
    ("ix_compliance_events_business_id", "compliance_events", "business_id"),
    ("ix_compliance_events_contact_id", "compliance_events", "contact_id"),
    ("ix_search_runs_created_at", "search_runs", "created_at"),
    ("ix_jobs_status", "jobs", "status"),
]


def upgrade() -> None:
    # Collapse any pre-existing duplicate (business_id, email) contacts, keeping the lowest id,
    # so the unique index can be created. NULL emails are left untouched (distinct in SQLite).
    op.execute(
        """
        DELETE FROM contacts
        WHERE email IS NOT NULL
          AND id NOT IN (
            SELECT MIN(id) FROM contacts WHERE email IS NOT NULL GROUP BY business_id, email
          )
        """
    )
    op.create_index(
        "uq_contacts_business_email", "contacts", ["business_id", "email"], unique=True
    )
    for name, table, column in _INDEXES:
        op.create_index(name, table, [column])


def downgrade() -> None:
    for name, table, _column in _INDEXES:
        op.drop_index(name, table_name=table)
    op.drop_index("uq_contacts_business_email", table_name="contacts")
