from osint_engine.domain.errors.entity_error import InvalidEntityHierarchyError


class InvalidEdgeHierarchyError(
    InvalidEntityHierarchyError, error_code="EDGE_INVALID_HIERARCHY"
):
    def __init__(self, *, subject: type, expected_base: type) -> None:
        super().__init__(subject=subject, expected_base=expected_base)

    def _build_message(self) -> str:
        return super()._build_message()
