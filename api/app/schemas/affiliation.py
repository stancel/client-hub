from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class AffiliationOrgStub(BaseModel):
    uuid: str
    name: str

    model_config = {"from_attributes": True}


class AffiliationOut(BaseModel):
    uuid: str
    organization: AffiliationOrgStub | None = None
    organization_uuid: str | None = None
    role_title: str | None = None
    department: str | None = None
    seniority: str | None = None
    is_decision_maker: bool
    is_primary: bool
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool
    notes: str | None = None
    created_at: datetime | None = None


class AffiliationListResponse(BaseModel):
    data: list[AffiliationOut]
    count: int


class AffiliationCreate(BaseModel):
    organization_uuid: str
    role_title: str | None = None
    department: str | None = None
    seniority: str | None = None
    is_decision_maker: bool = False
    is_primary: bool = False
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None
    external_refs_json: dict[str, Any] | None = None


class AffiliationUpdate(BaseModel):
    role_title: str | None = None
    department: str | None = None
    seniority: str | None = None
    is_decision_maker: bool | None = None
    is_primary: bool | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    notes: str | None = None
    external_refs_json: dict[str, Any] | None = None


class InlineAffiliationCreate(BaseModel):
    """Embedded in ContactCreate for one-shot contact + affiliation."""
    organization_uuid: str
    role_title: str | None = None
    department: str | None = None
    seniority: str | None = None
    is_decision_maker: bool = False
    is_primary: bool = False
    start_date: date | None = None
    end_date: date | None = None
