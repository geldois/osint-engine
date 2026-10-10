from __future__ import annotations

from osint_engine.domain.services.normalization import normalize_masked_document


def masked_overlapping_cpf(*, real_cpf: str) -> str:
    normalized = normalize_masked_document(value=real_cpf)
    kept = 0
    masked: list[str] = []

    for char in normalized:
        if char != "*" and kept < 4:
            masked.append(char)
            kept += 1
        else:
            masked.append("*")

    return "".join(masked)
