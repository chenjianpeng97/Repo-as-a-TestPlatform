-- auto-generated definition
create table intakes
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(255) not null,
    description   text         not null,
    is_default    boolean      not null,
    view_props    jsonb        not null,
    created_by_id uuid         null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    logo_props    jsonb        not null,
    deleted_at    timestamptz  null
);

CREATE INDEX inboxes_created_by_id_9f1cf5ec ON intakes USING btree (created_by_id);

CREATE INDEX inboxes_project_id_a0135c66 ON intakes USING btree (project_id);

CREATE INDEX inboxes_updated_by_id_69b7b3ae ON intakes USING btree (updated_by_id);

CREATE INDEX inboxes_workspace_id_d6178865 ON intakes USING btree (workspace_id);

CREATE UNIQUE INDEX inboxes_name_project_id_deleted_at_95043f72_uniq ON intakes USING btree (name, project_id, deleted_at);

CREATE UNIQUE INDEX intake_unique_name_project_when_deleted_at_null ON intakes USING btree (name, project_id) WHERE (deleted_at IS NULL);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "intakes" ("created_at", "updated_at", "id", "name", "description", "is_default", "view_props", "created_by_id", "project_id", "updated_by_id", "workspace_id", "logo_props", "deleted_at") VALUES ('2026-07-14 09:38:34.350401+00:00', '2026-07-14 09:38:34.350417+00:00', 'b48da961-f440-4776-85da-25448b32002e', 'first project Intake', '', TRUE, '{}', '9d1f264d-7dee-48c5-ab98-087db907b8a1', 'ec840712-e7ae-41f7-bc45-ff324bee0248', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', '{}', NULL);
