-- auto-generated definition
create table project_pages
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    page_id       uuid        not null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX project_pages_created_by_id_b9d02062 ON project_pages USING btree (created_by_id);

CREATE INDEX project_pages_page_id_a0f54439 ON project_pages USING btree (page_id);

CREATE INDEX project_pages_project_id_376ba35a ON project_pages USING btree (project_id);

CREATE INDEX project_pages_updated_by_id_b80bf0f4 ON project_pages USING btree (updated_by_id);

CREATE INDEX project_pages_workspace_id_13ed9e73 ON project_pages USING btree (workspace_id);

CREATE UNIQUE INDEX project_page_unique_project_page_when_deleted_at_null ON project_pages USING btree (project_id, page_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_pages_project_id_page_id_deleted_at_7c80a40c_uniq ON project_pages USING btree (project_id, page_id, deleted_at);

