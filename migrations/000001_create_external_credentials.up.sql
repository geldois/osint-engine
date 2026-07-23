CREATE TABLE external_credentials (
    username text NOT NULL,
    provider text NOT NULL,
    api_key  text NOT NULL,
    PRIMARY KEY (username, provider)
);
