-- auto-generated definition
create table project_public_members
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    member_id     uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX project_public_members_created_by_id_c4c7c776 ON project_public_members USING btree (created_by_id);

CREATE INDEX project_public_members_member_id_52f257f9 ON project_public_members USING btree (member_id);

CREATE INDEX project_public_members_project_id_2dfd893d ON project_public_members USING btree (project_id);

CREATE INDEX project_public_members_updated_by_id_c3e4d675 ON project_public_members USING btree (updated_by_id);

CREATE INDEX project_public_members_workspace_id_ebfce110 ON project_public_members USING btree (workspace_id);

CREATE UNIQUE INDEX project_public_member_unique_project_member_when_deleted_at_nul ON project_public_members USING btree (project_id, member_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_public_members_project_id_member_id_del_9acd89b5_uniq ON project_public_members USING btree (project_id, member_id, deleted_at);

