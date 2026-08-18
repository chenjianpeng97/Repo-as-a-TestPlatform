-- auto-generated definition
create table descriptions
(
    created_at           timestamptz not null,
    updated_at           timestamptz not null,
    deleted_at           timestamptz null,
    id                   uuid        not null
        primary key,
    description_json     jsonb       not null,
    description_html     text        not null,
    description_binary   bytea       null,
    description_stripped text        null,
    created_by_id        uuid        null,
    project_id           uuid        null,
    updated_by_id        uuid        null,
    workspace_id         uuid        not null
);

CREATE INDEX descriptions_created_by_id_b88ab399 ON descriptions USING btree (created_by_id);

CREATE INDEX descriptions_project_id_8f46180b ON descriptions USING btree (project_id);

CREATE INDEX descriptions_updated_by_id_af519c4d ON descriptions USING btree (updated_by_id);

CREATE INDEX descriptions_workspace_id_767279bf ON descriptions USING btree (workspace_id);

-- （descriptions 暂无数据，无示例 INSERT）
