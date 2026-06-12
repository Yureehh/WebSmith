from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import ProviderSetting
from app.providers.ai import ai_configured
from app.schemas.api import ProviderSettingsOut, ProviderSettingsUpdate


def get_provider_setting(db: Session) -> ProviderSetting:
    setting = db.scalar(select(ProviderSetting).where(ProviderSetting.provider == "discovery"))
    if setting is None:
        setting = ProviderSetting(
            provider="discovery",
            enabled=False,
            provider_order_json=["osm_overpass"],
        )
        db.add(setting)
        db.flush()
    return setting


def get_provider_settings(db: Session) -> ProviderSettingsOut:
    setting = get_provider_setting(db)
    return ProviderSettingsOut(
        discovery_provider="osm_overpass",
        overpass_configured=bool(settings.overpass_url),
        web_search_backup_enabled=setting.enabled,
        enrich_web_search_enabled=ai_configured(),
        ai_key_configured=bool(settings.openai_api_key),
    )


def update_provider_settings(db: Session, payload: ProviderSettingsUpdate) -> ProviderSettingsOut:
    setting = get_provider_setting(db)
    setting.enabled = payload.web_search_backup_enabled
    setting.provider_order_json = (
        ["osm_overpass", "web_search_scraping"]
        if payload.web_search_backup_enabled
        else ["osm_overpass"]
    )
    db.commit()
    return get_provider_settings(db)
