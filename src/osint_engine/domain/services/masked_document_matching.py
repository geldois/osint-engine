from __future__ import annotations

_MIN_OVERLAPPING_DIGITS = 4


def masked_document_overlap(*, left: str, right: str) -> int | None:
    if len(left) != len(right):
        return None

    overlapping = 0

    for left_char, right_char in zip(left, right, strict=True):
        if left_char == "*" or right_char == "*":
            continue

        if left_char != right_char:
            return None

        overlapping += 1

    return overlapping if overlapping >= _MIN_OVERLAPPING_DIGITS else None
