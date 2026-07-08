from __future__ import annotations

ADDRESS_DATA: dict[str, object] = {
    "cep": "70040912",
    "municipio": "BRASILIA",
    "logradouro": "SAUN QUADRA 5 BLOCO B",
    "complemento": "ANDAR T I",
    "bairro": "ASA NORTE",
    "numero": "SN",
    "uf": "DF",
}

COMPANY_DATA: dict[str, object] = {
    "data_inicio_atividade": "1966-08-01",
    "cnpj": "00000000000191",
    "identificador_matriz_filial": 1,
    "razao_social": "BANCO DO BRASIL SA",
    "natureza_juridica": "Sociedade de Economia Mista",
    "descricao_situacao_cadastral": "ATIVA",
    "data_situacao_cadastral": "2005-11-03",
    "descricao_motivo_situacao_cadastral": "SEM MOTIVO",
    "capital_social": 120000000000,
    "porte": "DEMAIS",
    "nome_fantasia": "DIRECAO GERAL",
}

CNAE_DATA: dict[str, object] = {
    "cnae_fiscal": 6422100,
    "cnae_fiscal_descricao": "Bancos múltiplos, com carteira comercial",
    "cnaes_secundarios": [
        {"codigo": 6499999, "descricao": "Outras atividades financeiras"},
    ],
}

CNPJ = "00000000000191"

PARTNER_PERSON: dict[str, object] = {
    "identificador_de_socio": 2,
    "nome_socio": "TARCIANA PAULA GOMES MEDEIROS",
    "cnpj_cpf_do_socio": "***128734**",
    "faixa_etaria": "Entre 41 a 50 anos",
    "qualificacao_socio": "Presidente",
    "data_entrada_sociedade": "2023-01-26",
}

COMPLETE_PAYLOAD_DATA: dict[str, object] = {
    **ADDRESS_DATA,
    **COMPANY_DATA,
    **CNAE_DATA,
    "ddd_telefone_1": "6134939002",
    "ddd_telefone_2": "6134931040",
    "email": "contato@bb.com.br",
    "qsa": [PARTNER_PERSON],
}
