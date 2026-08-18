-- auto-generated definition
create table estimates
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(255) not null,
    description   text         not null,
    created_by_id uuid         null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    type          varchar(255) not null,
    last_used     boolean      not null,
    deleted_at    timestamptz  null
);

CREATE INDEX estimates_created_by_id_7e401493 ON estimates USING btree (created_by_id);

CREATE INDEX estimates_project_id_7f195a41 ON estimates USING btree (project_id);

CREATE INDEX estimates_updated_by_id_b3fcfb1d ON estimates USING btree (updated_by_id);

CREATE INDEX estimates_workspace_id_718811eb ON estimates USING btree (workspace_id);

CREATE UNIQUE INDEX estimate_unique_name_project_when_deleted_at_null ON estimates USING btree (name, project_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX estimates_name_project_id_deleted_at_41d66639_uniq ON estimates USING btree (name, project_id, deleted_at);

