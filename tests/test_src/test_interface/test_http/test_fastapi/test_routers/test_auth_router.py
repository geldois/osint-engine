from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx2 import ASGITransport, AsyncClient
from jwt import decode as jwt_decode  # pyright: ignore[reportUnknownVariableType]

from osint_engine.config.croot import build_container
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app

if TYPE_CHECKING:
    import asyncpg

    from osint_engine.config.container import Policies
    from osint_engine.config.settings import Settings
    from tests.fakes.persistence import FakePgPool
    from tests.fixtures.persistence import MakeMemStorage

_USER = {"username": "alice", "password": "correct horse"}


async def _register(client: AsyncClient, body: dict[str, str] | None = None) -> None:
    await client.post("/auth/register", json=body if body is not None else _USER)


class TestPostRegister:
    @pytest.mark.asyncio
    async def test_returns_201_with_a_bearer_token(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post("/auth/register", json=_USER)
        body: dict[str, object] = response.json()

        assert response.status_code == 201
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str)
        assert len(body["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_token_carries_only_the_new_username_and_an_expiry(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.post("/auth/register", json=_USER)

        claims = jwt_decode(
            jwt=response.json()["access_token"],
            key=settings.secret_key,
            algorithms=["HS256"],
        )

        assert set(claims) == {"sub", "exp"}
        assert claims["sub"] == "alice"

    @pytest.mark.asyncio
    async def test_token_is_accepted_by_a_protected_route(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        registered = await fastapi_app_client.post("/auth/register", json=_USER)
        token = registered.json()["access_token"]

        response = await fastapi_app_client.get(
            "/credentials", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_stores_an_argon2_hash_never_the_password(
        self, fastapi_app_client: AsyncClient, fake_pg_pool: FakePgPool
    ) -> None:
        await _register(fastapi_app_client)

        stored = fake_pg_pool.users["alice"]

        assert stored.startswith("$argon2id$")
        assert _USER["password"] not in stored

    @pytest.mark.asyncio
    async def test_existing_username_returns_409_and_keeps_the_first_password(
        self, fastapi_app_client: AsyncClient, fake_pg_pool: FakePgPool
    ) -> None:
        await _register(fastapi_app_client)
        first_hash = fake_pg_pool.users["alice"]

        response = await fastapi_app_client.post(
            "/auth/register", json={"username": "alice", "password": "another pass"}
        )

        assert response.status_code == 409
        assert response.json()["type"] == "AUTH_USERNAME_TAKEN"
        assert fake_pg_pool.users["alice"] == first_hash

    @pytest.mark.asyncio
    async def test_the_old_seeded_admin_name_is_an_ordinary_free_username(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/register", json={"username": "admin", "password": "correct horse"}
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "username",
        ["ab", "a" * 33, "Alice", "al ice", "al.ice", "al/ice", "", "ålice"],
    )
    async def test_invalid_username_returns_422(
        self, fastapi_app_client: AsyncClient, username: str
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/register", json={"username": username, "password": "correct horse"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.parametrize("username", ["abc", "a" * 32, "a_b-c9"])
    async def test_username_at_the_accepted_boundaries_returns_201(
        self, fastapi_app_client: AsyncClient, username: str
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/register", json={"username": username, "password": "correct horse"}
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    @pytest.mark.parametrize("password", ["", "1234567", "p" * 129])
    async def test_invalid_password_returns_422(
        self, fastapi_app_client: AsyncClient, password: str
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/register", json={"username": "alice", "password": password}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.parametrize("password", ["12345678", "p" * 128])
    async def test_password_at_the_accepted_boundaries_returns_201(
        self, fastapi_app_client: AsyncClient, password: str
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/register", json={"username": "alice", "password": password}
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "body", [{}, {"username": "alice"}, {"password": "correct horse"}]
    )
    async def test_missing_field_returns_422(
        self, fastapi_app_client: AsyncClient, body: dict[str, str]
    ) -> None:
        response = await fastapi_app_client.post("/auth/register", json=body)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_input_creates_no_account(
        self, fastapi_app_client: AsyncClient, fake_pg_pool: FakePgPool
    ) -> None:
        await fastapi_app_client.post(
            "/auth/register", json={"username": "ab", "password": "correct horse"}
        )

        assert fake_pg_pool.users == {}


class TestPostRegisterRateLimit:
    @pytest.mark.asyncio
    async def test_the_eleventh_registration_in_the_window_returns_429(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        for index in range(10):
            response = await fastapi_app_client.post(
                "/auth/register",
                json={"username": f"user{index}", "password": "correct horse"},
            )

            assert response.status_code == 201

        blocked = await fastapi_app_client.post(
            "/auth/register",
            json={"username": "user10", "password": "correct horse"},
        )

        assert blocked.status_code == 429
        assert int(blocked.headers["retry-after"]) > 0

    @pytest.mark.asyncio
    async def test_rejected_attempts_also_count_toward_the_limit(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        for _ in range(10):
            await fastapi_app_client.post(
                "/auth/register", json={"username": "ab", "password": "short"}
            )

        blocked = await fastapi_app_client.post("/auth/register", json=_USER)

        assert blocked.status_code == 429


class TestPostToken:
    @pytest.mark.asyncio
    async def test_a_registered_user_can_log_in(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        await _register(fastapi_app_client)

        response = await fastapi_app_client.post(
            "/auth/token", data={"username": "alice", "password": "correct horse"}
        )
        body: dict[str, object] = response.json()

        assert response.status_code == 200
        assert isinstance(body["access_token"], str)
        assert len(body["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_access_token_carries_only_the_username_and_an_expiry(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        await _register(fastapi_app_client)

        response = await fastapi_app_client.post(
            "/auth/token", data={"username": "alice", "password": "correct horse"}
        )

        claims = jwt_decode(
            jwt=response.json()["access_token"],
            key=settings.secret_key,
            algorithms=["HS256"],
        )

        assert set(claims) == {"sub", "exp"}
        assert claims["sub"] == "alice"

    @pytest.mark.asyncio
    async def test_invalid_password_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        await _register(fastapi_app_client)

        response = await fastapi_app_client.post(
            "/auth/token", data={"username": "alice", "password": "wrong_password"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_unknown_username_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token", data={"username": "nobody", "password": "any_password"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.parametrize("username", ["admin", "visitor"])
    async def test_no_account_exists_before_someone_registers_it(
        self, fastapi_app_client: AsyncClient, username: str
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token", data={"username": username, "password": "change-me"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_failed_auth_includes_www_authenticate_bearer(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token", data={"username": "alice", "password": "wrong_password"}
        )

        assert response.headers.get("WWW-Authenticate") == "Bearer"

    @pytest.mark.asyncio
    async def test_failed_auth_response_carries_correlation_id(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token", data={"username": "alice", "password": "wrong_password"}
        )

        assert "x-correlation-id" in response.headers


class TestPostTokenRateLimit:
    @pytest.mark.asyncio
    async def test_exceeding_attempt_limit_returns_429(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        attempt = {"username": "alice", "password": "wrong_password"}

        for _ in range(5):
            await fastapi_app_client.post("/auth/token", data=attempt)

        response = await fastapi_app_client.post("/auth/token", data=attempt)

        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_within_attempt_limit_is_not_blocked(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        attempt = {"username": "alice", "password": "wrong_password"}

        for _ in range(4):
            response = await fastapi_app_client.post("/auth/token", data=attempt)

            assert response.status_code == 401


class TestViewerTokenRemoved:
    @pytest.mark.asyncio
    async def test_the_credential_free_token_route_no_longer_exists(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post("/auth/viewer-token")

        assert response.status_code == 404


class TestEveryProtectedRouteRequiresAToken:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", "/cnpj/11222333000181"),
            ("get", "/cpf/11144477735"),
            ("get", "/legal-process/11144477735"),
            ("get", "/cnep/11144477735"),
            ("get", "/ceis/11144477735"),
            ("get", "/cepim/11222333000181"),
            ("get", "/ceaf/11144477735"),
            ("get", "/peps/11144477735"),
            ("get", "/graphs"),
            ("get", "/consumption"),
            ("get", "/consumption/11144477735"),
            ("get", "/credentials"),
            ("get", "/text-ingestion/patterns"),
            ("post", "/text-ingestion"),
            ("post", "/cpf/batch"),
        ],
    )
    async def test_missing_token_returns_401(
        self, fastapi_app_client: AsyncClient, method: str, path: str
    ) -> None:
        response = await getattr(fastapi_app_client, method)(path)

        assert response.status_code == 401


@pytest.mark.usefixtures("clean_tables")
class TestRegisterAgainstPostgres:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_registering_persists_the_account_and_allows_login(
        self,
        settings: Settings,
        policies: Policies,
        make_mem_storage: MakeMemStorage,
        postgres_pool: asyncpg.Pool,
    ) -> None:
        async with AsyncClient() as http_client:
            container = build_container(
                settings=settings,
                http_client=http_client,
                pg_pool=postgres_pool,
                external_credential_encryption_key=(
                    settings.external_credential_encryption_key
                ),
                mem_storage=make_mem_storage(),
                policies=policies,
            )

            async with AsyncClient(
                transport=ASGITransport(app=build_fastapi_app(container=container)),
                base_url="http://test",
            ) as client:
                registered = await client.post("/auth/register", json=_USER)
                logged_in = await client.post("/auth/token", data=_USER)

        stored_hash = await postgres_pool.fetchval(  # pyright: ignore[reportUnknownMemberType]
            "SELECT hashed_password FROM users WHERE username = $1",
            _USER["username"],
        )

        assert registered.status_code == 201
        assert logged_in.status_code == 200
        assert stored_hash is not None
        assert stored_hash != _USER["password"]
