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

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "workspace_members" ("created_at", "updated_at", "id", "role", "created_by_id", "member_id", "updated_by_id", "workspace_id", "company_role", "view_props", "default_props", "issue_props", "is_active", "deleted_at", "explored_features", "getting_started_checklist", "tips") VALUES ('2026-07-10 12:37:56.150898+00:00', '2026-07-10 12:37:56.150911+00:00', 'a22c74fa-9e88-45fa-93e1-f5eb39398445', 20, NULL, '7f979bbb-cc06-4739-a6bb-0348e80efda7', NULL, '6f2f3ff8-62de-4127-978b-54991c166df3', '', '{''filters'': {''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}, ''display_filters'': {''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}, ''display_properties'': {''key'': True, ''link'': True, ''state'': True, ''labels'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''start_date'': True, ''updated_on'': True, ''sub_issue_count'': True, ''attachment_count'': True}}', '{''filters'': {''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}, ''display_filters'': {''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}, ''display_properties'': {''key'': True, ''link'': True, ''state'': True, ''labels'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''start_date'': True, ''updated_on'': True, ''sub_issue_count'': True, ''attachment_count'': True}}', '{''created'': True, ''assigned'': True, ''all_issues'': True, ''subscribed'': True}', TRUE, NULL, '{}', '{}', '{}');
