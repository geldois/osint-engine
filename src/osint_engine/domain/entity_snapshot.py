import json
import uuid
from dataclasses import asdict, dataclass, field


@dataclass(order=True, frozen=True, kw_only=True, slots=True)
class EntitySnapshot:
    id: uuid.UUID = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", self._calculate_id())

    def _calculate_id(self) -> uuid.UUID:
        return uuid.uuid5(
            namespace=uuid.NAMESPACE_DNS, name=json.dumps(asdict(self), sort_keys=True)
        )
