-- auto-generated definition
create table module_members
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    member_id     uuid        not null,
    module_id     uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX module_member_created_by_id_2ed84a65 ON module_members USING btree (created_by_id);

CREATE INDEX module_member_member_id_928f473e ON module_members USING btree (member_id);

CREATE INDEX module_member_module_id_f00be7ef ON module_members USING btree (module_id);

CREATE INDEX module_member_project_id_ec8d2376 ON module_members USING btree (project_id);

CREATE INDEX module_member_updated_by_id_a9046438 ON module_members USING btree (updated_by_id);

CREATE INDEX module_member_workspace_id_f2f23c73 ON module_members USING btree (workspace_id);

CREATE UNIQUE INDEX module_member_unique_module_member_when_deleted_at_null ON module_members USING btree (module_id, member_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX module_members_module_id_member_id_deleted_at_bb7a6f00_uniq ON module_members USING btree (module_id, member_id, deleted_at);

