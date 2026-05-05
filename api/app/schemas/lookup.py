from pydantic import BaseModel


class LookupMatchPhone(BaseModel):
    number: str
    type: str
    is_primary: bool
    is_verified: bool


class LookupMatchEmail(BaseModel):
    address: str
    type: str
    is_primary: bool
    is_verified: bool


class LookupMatchOrder(BaseModel):
    order_number: str | None = None
    status: str
    total: str
    order_date: str


class LookupMatchCommunication(BaseModel):
    channel: str
    direction: str
    subject: str | None = None
    occurred_at: str | None = None


class LookupMatchChannelPref(BaseModel):
    preferred: bool
    opt_in: str | None = None


class LookupMatch(BaseModel):
    uuid: str
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    contact_type: str
    organization: str | None = None
    phone: LookupMatchPhone | None = None
    email: LookupMatchEmail | None = None
    phones: list[LookupMatchPhone] = []
    emails: list[LookupMatchEmail] = []
    recent_orders: list[LookupMatchOrder] = []
    recent_communications: list[LookupMatchCommunication] = []
    tags: list[str] = []
    channel_preferences: dict[str, LookupMatchChannelPref] = {}


class LookupResponse(BaseModel):
    matches: list[LookupMatch]
    count: int
