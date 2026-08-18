-- auto-generated definition
create table project_members
(
    created_at    timestamptz      not null,
    updated_at    timestamptz      not null,
    id            uuid             not null
        primary key,
    comment       text             null,
    role          smallint         not null,
    created_by_id uuid             null,
    member_id     uuid             null,
    project_id    uuid             not null,
    updated_by_id uuid             null,
    workspace_id  uuid             not null,
    view_props    jsonb            not null,
    default_props jsonb            not null,
    sort_order    double precision not null,
    preferences   jsonb            not null,
    is_active     boolean          not null,
    deleted_at    timestamptz      null
);

CREATE INDEX project_member_created_by_id_8b363306 ON project_members USING btree (created_by_id);

CREATE INDEX project_member_member_id_9d6b126b ON project_members USING btree (member_id);

CREATE INDEX project_member_project_id_11ea1a9e ON project_members USING btree (project_id);

CREATE INDEX project_member_updated_by_id_cf6aaac4 ON project_members USING btree (updated_by_id);

CREATE INDEX project_member_workspace_id_88bb9a97 ON project_members USING btree (workspace_id);

CREATE UNIQUE INDEX project_member_unique_project_member_when_deleted_at_null ON project_members USING btree (project_id, member_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_members_project_id_member_id_deleted_at_0299122d_uniq ON project_members USING btree (project_id, member_id, deleted_at);

