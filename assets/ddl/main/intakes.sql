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

