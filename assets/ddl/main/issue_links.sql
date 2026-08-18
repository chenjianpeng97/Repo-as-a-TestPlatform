-- auto-generated definition
create table issue_links
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    title         varchar(255) null,
    url           text         not null,
    created_by_id uuid         null,
    issue_id      uuid         not null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    metadata      jsonb        not null,
    deleted_at    timestamptz  null
);

CREATE INDEX issue_links_created_by_id_5e4aa092 ON issue_links USING btree (created_by_id);

CREATE INDEX issue_links_issue_id_7032881f ON issue_links USING btree (issue_id);

CREATE INDEX issue_links_project_id_63d6e9ce ON issue_links USING btree (project_id);

CREATE INDEX issue_links_updated_by_id_a771cce4 ON issue_links USING btree (updated_by_id);

CREATE INDEX issue_links_workspace_id_ff9038e7 ON issue_links USING btree (workspace_id);

-- （issue_links 暂无数据，无示例 INSERT）
