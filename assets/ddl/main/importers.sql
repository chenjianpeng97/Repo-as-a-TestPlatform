-- auto-generated definition
create table importers
(
    created_at      timestamptz not null,
    updated_at      timestamptz not null,
    id              uuid        not null
        primary key,
    service         varchar(50) not null,
    status          varchar(50) not null,
    metadata        jsonb       not null,
    config          jsonb       not null,
    data            jsonb       not null,
    created_by_id   uuid        null,
    initiated_by_id uuid        not null,
    project_id      uuid        not null,
    token_id        uuid        not null,
    updated_by_id   uuid        null,
    workspace_id    uuid        not null,
    imported_data   jsonb       null,
    deleted_at      timestamptz null
);

CREATE INDEX importers_created_by_id_7dd06433 ON importers USING btree (created_by_id);

CREATE INDEX importers_initiated_by_id_3cddbd23 ON importers USING btree (initiated_by_id);

CREATE INDEX importers_project_id_1f8b43ef ON importers USING btree (project_id);

CREATE INDEX importers_token_id_c951e89f ON importers USING btree (token_id);

CREATE INDEX importers_updated_by_id_3915139e ON importers USING btree (updated_by_id);

CREATE INDEX importers_workspace_id_795b8985 ON importers USING btree (workspace_id);

-- （importers 暂无数据，无示例 INSERT）
