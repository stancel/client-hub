from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class PhoneOut(BaseModel):
    number: str
    type: str
    is_primary: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class EmailOut(BaseModel):
    address: str
    type: str
    is_primary: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class AddressOut(BaseModel):
    type: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool

    model_config = {"from_attributes": True}


class ChannelPrefOut(BaseModel):
    channel: str
    preferred: bool
    opt_in: str

    model_config = {"from_attributes": True}


class RecentOrderOut(BaseModel):
    order_number: str | None
    status: str
    total: Decimal
    order_date: str

    model_config = {"from_attributes": True}


class RecentCommOut(BaseModel):
    channel: str
    direction: str
    subject: str | None
    occurred_at: datetime

    model_config = {"from_attributes": True}


class LookupMatchPhone(BaseModel):
    number: str
    type: str
    is_primary: bool
    is_verified: bool


class LookupMatchResult(BaseModel):
    uuid: str
    first_name: str
    last_name: str
    display_name: str | None
    contact_type: str
    organization: str | None
    phone: LookupMatchPhone | None = None
    email: dict | None = None
    recent_orders: list[RecentOrderOut]
    recent_communications: list[RecentCommOut]
    tags: list[str]
    channel_preferences: dict[str, dict]


class LookupResponse(BaseModel):
    matches: list[LookupMatchResult]
    count: int


class ContactListItem(BaseModel):
    uuid: str
    first_name: str
    last_name: str
    display_name: str | None
    contact_type: str
    enrichment_status: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactListResponse(BaseModel):
    data: list[ContactListItem]
    pagination: dict


class ContactCreatePhone(BaseModel):
    number: str
    type: str = "mobile"
    is_primary: bool = False


class ContactCreateEmail(BaseModel):
    address: str
    type: str = "personal"
    is_primary: bool = False


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    contact_type: str = "prospect"
    organization_uuid: str | None = None
    display_name: str | None = None
    phones: list[ContactCreatePhone] = []
    emails: list[ContactCreateEmail] = []
    marketing_sources: list[str] = []
    data_source: str | None = None
    external_refs_json: dict[str, Any] | None = None


class ContactUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    contact_type: str | None = None
    organization_uuid: str | None = None
    enrichment_status: str | None = None
    notes_text: str | None = None
    external_refs_json: dict[str, Any] | None = None


class MarketingOptOuts(BaseModel):
    opt_out_sms: bool
    opt_out_email: bool
    opt_out_phone: bool


class PreferenceOut(BaseModel):
    key: str
    value: str
    data_source: str | None

    model_config = {"from_attributes": True}


class PreferenceSet(BaseModel):
    value: str
    data_source: str | None = None


class ContactSummaryOut(BaseModel):
    uuid: str
    first_name: str
    last_name: str
    display_name: str | None
    contact_type: str
    enrichment_status: str
    marketing_opt_out_sms: bool
    marketing_opt_out_email: bool
    marketing_opt_out_phone: bool
    organization: str | None
    primary_phone: str | None
    primary_email: str | None
    total_orders: int
    lifetime_value: Decimal
    last_order_date: str | None
    total_communications: int
    last_communication_at: datetime | None
    outstanding_balance: Decimal
    marketing_sources: list[str]
    tags: list[str]
