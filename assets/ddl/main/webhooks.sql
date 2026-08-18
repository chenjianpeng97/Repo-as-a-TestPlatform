-- auto-generated definition
create table webhooks
(
    created_at    timestamptz   not null,
    updated_at    timestamptz   not null,
    id            uuid          not null
        primary key,
    url           varchar(1024) not null,
    is_active     boolean       not null,
    secret_key    varchar(255)  not null,
    project       boolean       not null,
    issue         boolean       not null,
    module        boolean       not null,
    cycle         boolean       not null,
    issue_comment boolean       not null,
    created_by_id uuid          null,
    updated_by_id uuid          null,
    workspace_id  uuid          not null,
    deleted_at    timestamptz   null,
    is_internal   boolean       not null,
    version       varchar(50)   not null
);

CREATE INDEX webhooks_created_by_id_25aca1b0 ON webhooks USING btree (created_by_id);

CREATE INDEX webhooks_updated_by_id_ea35154e ON webhooks USING btree (updated_by_id);

CREATE INDEX webhooks_workspace_id_da5865d7 ON webhooks USING btree (workspace_id);

CREATE UNIQUE INDEX webhook_url_unique_url_when_deleted_at_null ON webhooks USING btree (workspace_id, url) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX webhooks_workspace_id_url_deleted_at_ea7a1429_uniq ON webhooks USING btree (workspace_id, url, deleted_at);

-- （webhooks 暂无数据，无示例 INSERT）
