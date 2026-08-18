-- auto-generated definition
create table project_issue_types
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    deleted_at    timestamptz null,
    id            uuid        not null
        primary key,
    level         integer     not null,
    is_default    boolean     not null,
    created_by_id uuid        null,
    issue_type_id uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null
);

CREATE INDEX project_issue_types_created_by_id_049cecfd ON project_issue_types USING btree (created_by_id);

CREATE INDEX project_issue_types_issue_type_id_9494de9f ON project_issue_types USING btree (issue_type_id);

CREATE INDEX project_issue_types_project_id_ef6e52e4 ON project_issue_types USING btree (project_id);

CREATE INDEX project_issue_types_updated_by_id_b5998397 ON project_issue_types USING btree (updated_by_id);

CREATE INDEX project_issue_types_workspace_id_ace3c5b5 ON project_issue_types USING btree (workspace_id);

CREATE UNIQUE INDEX project_issue_type_unique_project_issue_type_when_deleted_at_nu ON project_issue_types USING btree (project_id, issue_type_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_issue_types_project_id_issue_type_id_2287e5dc_uniq ON project_issue_types USING btree (project_id, issue_type_id, deleted_at);

-- （project_issue_types 暂无数据，无示例 INSERT）
