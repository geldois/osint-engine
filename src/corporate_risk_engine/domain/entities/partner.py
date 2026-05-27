from pydantic import BaseModel


class Partner(BaseModel):
    cpf: str
    has_bad_reputation: bool
