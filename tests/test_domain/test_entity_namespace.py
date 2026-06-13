from __future__ import annotations

from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

# VALID CASES


def test_entity_namespace_assures_different_namespaces_for_members() -> None:
    assert len(set(EntityNAMESPACE)) == len(
        {member.namespace for member in EntityNAMESPACE}
    )
