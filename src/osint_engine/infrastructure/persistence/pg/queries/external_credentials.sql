-- name: FindByUsernameAndProvider :one
SELECT username, provider, api_key
FROM external_credentials
WHERE username = sqlc.arg('username') AND provider = sqlc.arg('provider');

-- name: Upsert :exec
INSERT INTO external_credentials (username, provider, api_key)
VALUES (sqlc.arg('username'), sqlc.arg('provider'), sqlc.arg('api_key'))
ON CONFLICT (username, provider)
DO UPDATE SET api_key = excluded.api_key;

-- name: ListProvidersByUsername :many
SELECT provider
FROM external_credentials
WHERE username = sqlc.arg('username');
