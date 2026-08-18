-- auto-generated definition
create table integrations
(
    created_at     timestamptz  not null,
    updated_at     timestamptz  not null,
    id             uuid         not null
        primary key,
    title          varchar(400) not null,
    provider       varchar(400) not null,
    network        integer      not null,
    description    jsonb        not null,
    author         varchar(400) not null,
    webhook_url    text         not null,
    webhook_secret text         not null,
    redirect_url   text         not null,
    metadata       jsonb        not null,
    verified       boolean      not null,
    avatar_url     text         null,
    created_by_id  uuid         null,
    updated_by_id  uuid         null,
    deleted_at     timestamptz  null
);

CREATE INDEX integrations_created_by_id_0b6edd52 ON integrations USING btree (created_by_id);

CREATE INDEX integrations_provider_6537a106_like ON integrations USING btree (provider varchar_pattern_ops);

CREATE INDEX integrations_updated_by_id_d6d00d15 ON integrations USING btree (updated_by_id);

CREATE UNIQUE INDEX integrations_provider_key ON integrations USING btree (provider);

-- （integrations 暂无数据，无示例 INSERT）
