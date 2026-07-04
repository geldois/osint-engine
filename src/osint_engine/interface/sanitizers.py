def sanitize_cnpj(cnpj: str, /) -> str:
    return "".join(char for char in cnpj if char.isdecimal())
