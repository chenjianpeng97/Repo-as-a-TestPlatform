-- auto-generated definition
create table project_member_invites
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    email         varchar(255) not null,
    accepted      boolean      not null,
    token         varchar(255) not null,
    message       text         null,
    responded_at  timestamptz  null,
    role          smallint     not null,
    created_by_id uuid         null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX project_member_invite_created_by_id_a87df45c ON project_member_invites USING btree (created_by_id);

CREATE INDEX project_member_invite_project_id_8fb7750e ON project_member_invites USING btree (project_id);

CREATE INDEX project_member_invite_updated_by_id_5aa55c96 ON project_member_invites USING btree (updated_by_id);

CREATE INDEX project_member_invite_workspace_id_64e2dc4c ON project_member_invites USING btree (workspace_id);

-- （project_member_invites 暂无数据，无示例 INSERT）
