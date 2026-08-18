-- auto-generated definition
create table issue_types
(
    created_at      timestamptz      not null,
    updated_at      timestamptz      not null,
    id              uuid             not null
        primary key,
    name            varchar(255)     not null,
    description     text             not null,
    logo_props      jsonb            not null,
    created_by_id   uuid             null,
    updated_by_id   uuid             null,
    workspace_id    uuid             not null,
    is_active       boolean          not null,
    deleted_at      timestamptz      null,
    is_default      boolean          not null,
    level           double precision not null,
    external_id     varchar(255)     null,
    external_source varchar(255)     null,
    is_epic         boolean          not null
);

CREATE INDEX issue_types_created_by_id_48764f53 ON issue_types USING btree (created_by_id);

CREATE INDEX issue_types_updated_by_id_4919203b ON issue_types USING btree (updated_by_id);

CREATE INDEX issue_types_workspace_id_591c6f3b ON issue_types USING btree (workspace_id);

