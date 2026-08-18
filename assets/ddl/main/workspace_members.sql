-- auto-generated definition
create table workspace_members
(
    created_at                timestamptz not null,
    updated_at                timestamptz not null,
    id                        uuid        not null
        primary key,
    role                      smallint    not null,
    created_by_id             uuid        null,
    member_id                 uuid        not null,
    updated_by_id             uuid        null,
    workspace_id              uuid        not null,
    company_role              text        null,
    view_props                jsonb       not null,
    default_props             jsonb       not null,
    issue_props               jsonb       not null,
    is_active                 boolean     not null,
    deleted_at                timestamptz null,
    explored_features         jsonb       not null,
    getting_started_checklist jsonb       not null,
    tips                      jsonb       not null
);

CREATE INDEX workspace_member_created_by_id_8dc8b040 ON workspace_members USING btree (created_by_id);

CREATE INDEX workspace_member_member_id_824f5497 ON workspace_members USING btree (member_id);

CREATE INDEX workspace_member_updated_by_id_1cec0062 ON workspace_members USING btree (updated_by_id);

CREATE INDEX workspace_member_workspace_id_33f66d4b ON workspace_members USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_member_unique_workspace_member_when_deleted_at_null ON workspace_members USING btree (workspace_id, member_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX workspace_members_workspace_id_member_id_d_d7bfa872_uniq ON workspace_members USING btree (workspace_id, member_id, deleted_at);

