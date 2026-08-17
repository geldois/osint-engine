import dataclasses


@dataclasses.dataclass()
class ExternalCredential:
    username: str
    provider: str
    api_key: str
