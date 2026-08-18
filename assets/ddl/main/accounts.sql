-- auto-generated definition
create table accounts
(
    created_at               timestamptz  not null,
    updated_at               timestamptz  not null,
    id                       uuid         not null
        primary key,
    provider_account_id      varchar(255) not null,
    provider                 varchar      not null,
    access_token             text         not null,
    access_token_expired_at  timestamptz  null,
    refresh_token            text         null,
    refresh_token_expired_at timestamptz  null,
    last_connected_at        timestamptz  not null,
    metadata                 jsonb        not null,
    user_id                  uuid         not null,
    id_token                 text         not null
);

CREATE INDEX accounts_user_id_7f1e1f1e ON accounts USING btree (user_id);

CREATE UNIQUE INDEX accounts_provider_provider_account_id_daac1f10_uniq ON accounts USING btree (provider, provider_account_id);

