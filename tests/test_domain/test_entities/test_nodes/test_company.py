from __future__ import annotations

from decimal import Decimal

from osint_engine.domain.entities.nodes.company import Company

# TEST DOUBLES


def _make_company(*, cnpj: str, trade_name: str = "DIRECAO GERAL") -> Company:
    return Company(
        activity_start_date="1966-08-01",
        cnpj=cnpj,
        is_headquarters=True,
        legal_name="BANCO DO BRASIL SA",
        legal_nature="Sociedade de Economia Mista",
        registration_status="ATIVA",
        registration_status_date="2005-11-03",
        registration_status_reason="SEM MOTIVO",
        share_capital=Decimal("120000000000"),
        size_category="DEMAIS",
        trade_name=trade_name,
    )


# TESTS


class TestCompanyIdentityNormalization:
    def test_id_is_same_for_formatted_and_raw_cnpj(self) -> None:
        formatted = _make_company(cnpj="00.000.000/0001-91")
        raw = _make_company(cnpj="00000000000191")

        assert formatted.id == raw.id

    def test_id_differs_for_genuinely_different_cnpj(self) -> None:
        company_a = _make_company(cnpj="00000000000191")
        company_b = _make_company(cnpj="00000000000272")

        assert company_a.id != company_b.id

    def test_content_id_is_same_for_formatted_and_raw_cnpj(self) -> None:
        formatted = _make_company(cnpj="00.000.000/0001-91")
        raw = _make_company(cnpj="00000000000191")

        assert formatted.content_id == raw.content_id

    def test_stored_cnpj_preserves_original_formatting(self) -> None:
        company = _make_company(cnpj="00.000.000/0001-91")

        assert company.cnpj == "00.000.000/0001-91"
