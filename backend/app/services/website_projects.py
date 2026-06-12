from pathlib import Path

from sqlalchemy.orm import Session

from app.models.entities import Business, LeadProfile, WebsiteProject
from app.providers.discovery import normalize_name
from app.schemas.api import WebsiteImportIn
from app.services.businesses import add_event, ensure_profile, get_business_or_404

REPO_ROOT = Path(__file__).resolve().parents[3]
WEBSITE_PROJECTS_DIR = REPO_ROOT / "website-projects"
BUILD_BRIEF_TEMPLATE = REPO_ROOT / "docs" / "website-factory" / "BUILD_BRIEF_TEMPLATE.md"


def project_slug(business: Business) -> str:
    base = normalize_name(business.name).replace(" ", "-")
    return "".join(char for char in base if char.isalnum() or char == "-").strip("-") or "website"


def source_document_filename(index: int, source_type: str) -> str:
    safe_type = "".join(
        char
        for char in normalize_name(source_type).replace(" ", "-")
        if char.isalnum() or char == "-"
    )
    return f"{index:02d}-{safe_type or 'source'}.md"


def build_source_documents(project_dir: Path, business: Business) -> str:
    lines = [
        "# Source Index\n\n",
        "These files are the factual base for the website. "
        "Do not invent facts that are not present here.\n\n",
    ]
    for index, source in enumerate(business.source_documents, start=1):
        filename = source_document_filename(index, source.source_type)
        lines.append(f"- `source_documents/{filename}`: {source.title or source.source_type}\n")
        (project_dir / "source_documents" / filename).write_text(
            "# Source Document\n\n"
            f"- Type: {source.source_type}\n"
            f"- URL: {source.source_url or 'unknown'}\n"
            f"- Title: {source.title or 'unknown'}\n"
            f"- Confidence: {source.confidence or 'unknown'}\n\n"
            "## Extracted Data\n\n"
            f"```json\n{source.extracted_json or {}}\n```\n\n"
            "## Text\n\n"
            f"{source.content_text or 'No text captured.'}\n",
            encoding="utf-8",
        )
    return "".join(lines)


def build_business_context(business: Business, profile: LeadProfile) -> str:
    contact = business.phone or business.email or "unknown"
    return (
        f"# {business.name}\n\n"
        "## Business Snapshot\n\n"
        f"- Business ID: {business.id}\n"
        f"- Category: {business.primary_category or 'unknown'}\n"
        f"- Address: {business.formatted_address or 'unknown'}\n"
        f"- Website: {business.website_url or 'unknown'}\n"
        f"- Phone: {business.phone or 'unknown'}\n"
        f"- Email: {business.email or 'unknown'}\n"
        f"- Contact: {contact}\n"
        f"- Market type: {profile.market_type}\n"
        f"- Lead status: {profile.status}\n\n"
        "## Qualitative Context\n\n"
        "### Opportunity Summary\n\n"
        f"{profile.opportunity_summary or 'Run enrichment before final copy.'}\n\n"
        "### Mission Summary\n\n"
        f"{profile.mission_summary or 'Unknown. Do not invent mission claims.'}\n\n"
        "### Recommended Angle\n\n"
        f"{profile.recommended_angle or 'Create a clear, trustworthy local-business presence.'}\n\n"
        "### Audience Notes\n\n"
        f"{profile.audience_notes or 'Unknown. Validate before making strong claims.'}\n\n"
        "## Client Confirmation Needed\n\n"
        "- Opening hours\n"
        "- Final services/offers\n"
        "- Exact prices, if any\n"
        "- Legal business details for footer/privacy pages\n"
        "- Whether to use analytics, booking, WhatsApp, forms, or only direct contact links\n\n"
    )


def build_brief(project_dir: Path, business: Business, profile: LeadProfile) -> str:
    template = BUILD_BRIEF_TEMPLATE.read_text(encoding="utf-8")
    return template.format(
        business_name=business.name,
        business_context=build_business_context(business, profile),
        source_index_path="SOURCE_INDEX.md",
        source_documents_path="source_documents/",
        site_path="site/",
        exports_path="exports/",
    )


def build_readme(business: Business) -> str:
    return (
        f"# {business.name} Website Workspace\n\n"
        "This folder is a WebSmith handoff for Claude Code, Codex, Codex Sites, or another "
        "external website builder.\n\n"
        "Use one file first: `BUILD_BRIEF.md`.\n\n"
        "Recommended flow:\n\n"
        "1. Open this exact folder in VS Code or your builder tool.\n"
        "2. Ask the builder to read `BUILD_BRIEF.md` and plan before editing.\n"
        "3. Approve the visual direction.\n"
        "4. Build only inside `site/`.\n"
        "5. Keep final exports in `exports/`.\n"
        "6. Import `site/`, a zip, or a preview URL back into WebSmith.\n\n"
        "Core files:\n\n"
        "- `BUILD_BRIEF.md`: all builder instructions, business context, copy rules, "
        "asset rules, and QA.\n"
        "- `SOURCE_INDEX.md`: list of source documents.\n"
        "- `source_documents/`: source-backed evidence from enrichment.\n"
        "- `CLIENT_CHECKLIST.md`: client approval, import, and hosting handoff checklist.\n"
        "- `site/`: final static website implementation.\n"
        "- `exports/`: optional zip exports.\n"
    )


def build_client_checklist() -> str:
    return (
        "# Client Checklist\n\n"
        "## Approval\n\n"
        "- Business name, address, and contact details are correct.\n"
        "- Services/offers are accurate.\n"
        "- No unsupported claims are present.\n"
        "- Tone and visual direction are approved.\n"
        "- Mobile layout is approved.\n"
        "- Domain/hosting path is confirmed.\n"
        "- Privacy/cookie choices are confirmed.\n\n"
        "## Import Back To WebSmith\n\n"
        "When the external website is ready:\n\n"
        "1. Keep final code inside `site/`.\n"
        "2. Add or update `site/README.md` and `site/DECISIONS.md`.\n"
        "3. If exporting a zip, place it in `exports/`.\n"
        "4. In WebSmith, select the lead and click `Import website`.\n"
        "5. Paste either the `site/` folder path, zip path, or preview URL.\n\n"
        "## Hosting Handoff\n\n"
        "Default: client-owned hosting and domain.\n\n"
        "Needed from client:\n\n"
        "- Domain registrar access or DNS access.\n"
        "- Hosting provider account, if already chosen.\n"
        "- Legal business details for footer and privacy policy.\n"
        "- Decision on analytics, cookies, forms, booking, WhatsApp, or direct links only.\n\n"
        "If WebSmith manages hosting, define monthly price, support limits, renewal/payment terms, "
        "backup expectations, and what happens if payment stops.\n"
    )


def scaffold_website_workspace(business: Business, profile: LeadProfile) -> tuple[Path, str]:
    project_dir = WEBSITE_PROJECTS_DIR / f"{business.id}-{project_slug(business)}"
    for relative in [
        "source_documents",
        "assets/generated",
        "assets/source",
        "exports",
        "site/assets",
        "site/src",
    ]:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)

    source_index = build_source_documents(project_dir, business)
    brief = build_brief(project_dir, business, profile)
    (project_dir / "SOURCE_INDEX.md").write_text(source_index, encoding="utf-8")
    (project_dir / "BUILD_BRIEF.md").write_text(brief, encoding="utf-8")
    (project_dir / "CLIENT_CHECKLIST.md").write_text(build_client_checklist(), encoding="utf-8")
    (project_dir / "README.md").write_text(build_readme(business), encoding="utf-8")
    (project_dir / "site" / "README.md").write_text(
        "# Site Output\n\n"
        "Build the static website here. Keep implementation files inside this folder.\n",
        encoding="utf-8",
    )
    return project_dir, brief


def generate_website(db: Session, payload: dict[str, object]) -> dict[str, object]:
    business = get_business_or_404(db, int(payload["business_id"]))
    profile = ensure_profile(db, business)
    profile.status = "draft_ready"
    project_dir, brief = scaffold_website_workspace(business, profile)
    project = WebsiteProject(
        business_id=business.id,
        status="draft_ready",
        generation_mode="internal",
        project_name=f"{project_slug(business)}-website",
        repo_path=str(project_dir),
        preview_url=None,
        brief_markdown=brief,
        generated_copy_json={
            "mode": "external_agent_handoff",
            "build_brief": str(project_dir / "BUILD_BRIEF.md"),
            "source_index": str(project_dir / "SOURCE_INDEX.md"),
            "source_documents_dir": str(project_dir / "source_documents"),
            "client_checklist": str(project_dir / "CLIENT_CHECKLIST.md"),
            "site_output_dir": str(project_dir / "site"),
            "exports_dir": str(project_dir / "exports"),
            "asset_dirs": [
                str(project_dir / "assets/generated"),
                str(project_dir / "assets/source"),
            ],
        },
    )
    db.add(project)
    add_event(db, business.id, "draft_generated", "Website handoff workspace generated.")
    db.commit()
    return {
        "business_id": business.id,
        "website_project_id": project.id,
        "status": "draft_ready",
        "repo_path": str(project_dir),
    }


def import_website(db: Session, business_id: int, payload: WebsiteImportIn) -> WebsiteProject:
    business = get_business_or_404(db, business_id)
    profile = ensure_profile(db, business)
    profile.status = "externally_imported"
    project = WebsiteProject(
        business_id=business.id,
        status="externally_imported",
        generation_mode="external_import",
        project_name=payload.project_name,
        repo_path=payload.repo_path,
        preview_url=payload.preview_url,
        brief_markdown=payload.notes,
        generated_copy_json={"imported": True},
    )
    db.add(project)
    add_event(db, business.id, "draft_generated", "External website imported.")
    db.commit()
    db.refresh(project)
    return project
