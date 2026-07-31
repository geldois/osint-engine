-- name: find_by_username_and_provider^
SELECT username, provider, api_key
FROM external_credentials
WHERE username = :username AND provider = :provider;

-- name: upsert!
INSERT INTO external_credentials (username, provider, api_key)
VALUES (:username, :provider, :api_key)
ON CONFLICT (username, provider)
DO UPDATE SET api_key = excluded.api_key;

-- name: list_providers_by_username
SELECT provider
FROM external_credentials
WHERE username = :username;
