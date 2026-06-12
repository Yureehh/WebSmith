from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Job
from app.schemas.api import (
    BusinessOut,
    DoNotContactIn,
    DraftReplyIn,
    FollowUpIn,
    JobOut,
    MarkEmailSentIn,
    OutreachDraftIn,
    OutreachMessageOut,
    ProviderSettingsOut,
    ProviderSettingsUpdate,
    ReceivedAnswerIn,
    SearchRunCreate,
    SearchRunOut,
    SearchRunResult,
    StatusUpdate,
    WebsiteImportIn,
    WebsiteProjectOut,
)
from app.services.businesses import (
    create_search_run,
    do_not_contact,
    draft_outreach,
    enrich_business,
    get_business_or_404,
    list_businesses,
    mark_email_sent,
    received_answer,
    set_follow_up,
    update_status,
)
from app.services.jobs import run_sync_job
from app.services.settings import get_provider_settings, update_provider_settings
from app.services.website_projects import generate_website, import_website

router = APIRouter(prefix="/api")


@router.post("/search-runs", response_model=SearchRunResult)
async def post_search_run(
    payload: SearchRunCreate, db: Session = Depends(get_db)
) -> SearchRunResult:
    search_run, businesses = await create_search_run(db, payload)
    return SearchRunResult(search_run=search_run, businesses=businesses)


@router.get("/search-runs/{search_run_id}", response_model=SearchRunOut)
def get_search_run(search_run_id: int, db: Session = Depends(get_db)) -> SearchRunOut:
    from app.models.entities import SearchRun

    search_run = db.get(SearchRun, search_run_id)
    if search_run is None:
        raise HTTPException(status_code=404, detail="Search run not found")
    return search_run


@router.get("/businesses", response_model=list[BusinessOut])
def get_businesses(db: Session = Depends(get_db)) -> list[BusinessOut]:
    return list_businesses(db)


@router.get("/businesses/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db)) -> BusinessOut:
    return get_business_or_404(db, business_id)


@router.post("/businesses/{business_id}/enrich", response_model=JobOut)
def post_enrich(business_id: int, db: Session = Depends(get_db)) -> JobOut:
    return run_sync_job(db, "enrich_business", {"business_id": business_id}, enrich_business)


@router.post("/businesses/{business_id}/status", response_model=BusinessOut)
def post_status(
    business_id: int, payload: StatusUpdate, db: Session = Depends(get_db)
) -> BusinessOut:
    return update_status(db, business_id, payload)


@router.post("/businesses/{business_id}/generate-website", response_model=JobOut)
def post_generate_website(business_id: int, db: Session = Depends(get_db)) -> JobOut:
    return run_sync_job(db, "generate_website", {"business_id": business_id}, generate_website)


@router.post("/businesses/{business_id}/import-website", response_model=WebsiteProjectOut)
def post_import_website(
    business_id: int, payload: WebsiteImportIn, db: Session = Depends(get_db)
) -> WebsiteProjectOut:
    return import_website(db, business_id, payload)


@router.post("/businesses/{business_id}/draft-outreach", response_model=OutreachMessageOut)
def post_draft_outreach(
    business_id: int, payload: OutreachDraftIn, db: Session = Depends(get_db)
) -> OutreachMessageOut:
    return draft_outreach(db, business_id, payload.language, payload.contact_id)


@router.post("/businesses/{business_id}/mark-email-sent", response_model=BusinessOut)
def post_mark_email_sent(
    business_id: int, payload: MarkEmailSentIn, db: Session = Depends(get_db)
) -> BusinessOut:
    return mark_email_sent(db, business_id, payload)


@router.post("/businesses/{business_id}/received-answer")
def post_received_answer(
    business_id: int, payload: ReceivedAnswerIn, db: Session = Depends(get_db)
) -> dict:
    return received_answer(db, business_id, payload)


@router.post("/businesses/{business_id}/follow-up", response_model=BusinessOut)
def post_follow_up(
    business_id: int, payload: FollowUpIn, db: Session = Depends(get_db)
) -> BusinessOut:
    return set_follow_up(db, business_id, payload)


@router.post("/businesses/{business_id}/do-not-contact", response_model=BusinessOut)
def post_do_not_contact(
    business_id: int, payload: DoNotContactIn, db: Session = Depends(get_db)
) -> BusinessOut:
    return do_not_contact(db, business_id, payload)


@router.post("/conversations/{conversation_id}/draft-reply")
def post_draft_reply(conversation_id: int, payload: DraftReplyIn) -> dict:
    body = (
        "Grazie per la risposta. Posso mandarvi una proposta sintetica con una bozza concreta?"
        if payload.language == "it"
        else "Thanks for replying. May I send a short proposal with a concrete draft?"
    )
    return {"conversation_id": conversation_id, "draft": body}


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/settings/providers", response_model=ProviderSettingsOut)
def get_settings(db: Session = Depends(get_db)) -> ProviderSettingsOut:
    return get_provider_settings(db)


@router.put("/settings/providers", response_model=ProviderSettingsOut)
def put_settings(
    payload: ProviderSettingsUpdate, db: Session = Depends(get_db)
) -> ProviderSettingsOut:
    return update_provider_settings(db, payload)
