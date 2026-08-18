-- auto-generated definition
create table teams
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(255) not null,
    description   text         not null,
    created_by_id uuid         null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    logo_props    jsonb        not null,
    deleted_at    timestamptz  null
);

CREATE INDEX team_created_by_id_725a9101 ON teams USING btree (created_by_id);

CREATE INDEX team_updated_by_id_79bb36f2 ON teams USING btree (updated_by_id);

CREATE INDEX team_workspace_id_1d56407f ON teams USING btree (workspace_id);

CREATE UNIQUE INDEX team_unique_name_workspace_when_deleted_at_null ON teams USING btree (name, workspace_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX teams_name_workspace_id_deleted_at_4b131aa2_uniq ON teams USING btree (name, workspace_id, deleted_at);

