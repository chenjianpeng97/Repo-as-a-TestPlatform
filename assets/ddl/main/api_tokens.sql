-- auto-generated definition
create table api_tokens
(
    created_at         timestamptz  not null,
    updated_at         timestamptz  not null,
    id                 uuid         not null
        primary key,
    token              varchar(255) not null,
    label              varchar(255) not null,
    user_type          smallint     not null,
    created_by_id      uuid         null,
    updated_by_id      uuid         null,
    user_id            uuid         not null,
    workspace_id       uuid         null,
    description        text         not null,
    expired_at         timestamptz  null,
    is_active          boolean      not null,
    last_used          timestamptz  null,
    is_service         boolean      not null,
    deleted_at         timestamptz  null,
    allowed_rate_limit varchar(255) not null
);

CREATE INDEX api_tokens_created_by_id_441e3d24 ON api_tokens USING btree (created_by_id);

CREATE INDEX api_tokens_token_6211101f_like ON api_tokens USING btree (token varchar_pattern_ops);

CREATE INDEX api_tokens_updated_by_id_bcd544cf ON api_tokens USING btree (updated_by_id);

CREATE INDEX api_tokens_user_id_2db24e1c ON api_tokens USING btree (user_id);

CREATE INDEX api_tokens_workspace_id_6791c7bd ON api_tokens USING btree (workspace_id);

CREATE UNIQUE INDEX api_tokens_token_key ON api_tokens USING btree (token);

