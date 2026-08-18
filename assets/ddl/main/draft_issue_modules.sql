-- auto-generated definition
create table draft_issue_modules
(
    created_at     timestamptz not null,
    updated_at     timestamptz not null,
    deleted_at     timestamptz null,
    id             uuid        not null
        primary key,
    created_by_id  uuid        null,
    draft_issue_id uuid        not null,
    module_id      uuid        not null,
    project_id     uuid        null,
    updated_by_id  uuid        null,
    workspace_id   uuid        not null
);

CREATE INDEX draft_issue_modules_created_by_id_95ec4247 ON draft_issue_modules USING btree (created_by_id);

CREATE INDEX draft_issue_modules_draft_issue_id_eb470383 ON draft_issue_modules USING btree (draft_issue_id);

CREATE INDEX draft_issue_modules_module_id_4d3f477a ON draft_issue_modules USING btree (module_id);

CREATE INDEX draft_issue_modules_project_id_c32eadab ON draft_issue_modules USING btree (project_id);

CREATE INDEX draft_issue_modules_updated_by_id_18548965 ON draft_issue_modules USING btree (updated_by_id);

CREATE INDEX draft_issue_modules_workspace_id_536c335a ON draft_issue_modules USING btree (workspace_id);

CREATE UNIQUE INDEX draft_issue_modules_draft_issue_id_module_id_634e1f1a_uniq ON draft_issue_modules USING btree (draft_issue_id, module_id, deleted_at);

CREATE UNIQUE INDEX module_draft_issue_unique_issue_module_when_deleted_at_null ON draft_issue_modules USING btree (draft_issue_id, module_id) WHERE (deleted_at IS NULL);

-- （draft_issue_modules 暂无数据，无示例 INSERT）
