-- auto-generated definition
create table workspace_member_invites
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
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX workspace_member_invite_created_by_id_082f21d3 ON workspace_member_invites USING btree (created_by_id);

CREATE INDEX workspace_member_invite_updated_by_id_d31a9c7f ON workspace_member_invites USING btree (updated_by_id);

CREATE INDEX workspace_member_invite_workspace_id_d935b364 ON workspace_member_invites USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_member_invite_unique_email_workspace_when_deleted_at_ ON workspace_member_invites USING btree (email, workspace_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX workspace_member_invites_email_workspace_id_delet_2f03573e_uniq ON workspace_member_invites USING btree (email, workspace_id, deleted_at);

-- （workspace_member_invites 暂无数据，无示例 INSERT）
