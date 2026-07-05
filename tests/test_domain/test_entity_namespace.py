from __future__ import annotations

from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE


class TestEntityNamespaceContract:
    def test_entity_namespace_assures_different_namespaces_for_members(self) -> None:
        assert len(set(EntityNAMESPACE)) == len(
            {member.namespace for member in EntityNAMESPACE}
        )

    def test_entity_namespace_members_have_matching_name_and_value(self) -> None:
        for member in EntityNAMESPACE:
            assert member._name_ == member._value_, (
                f"Member {member} has mismatched _name_ and _value_: "
                f"_name_={member._name_}, _value_={member._value_}"
            )
