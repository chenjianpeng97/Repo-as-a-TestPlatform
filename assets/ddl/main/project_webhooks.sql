-- auto-generated definition
create table project_webhooks
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    deleted_at    timestamptz null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    webhook_id    uuid        not null,
    workspace_id  uuid        not null
);

CREATE INDEX project_webhooks_created_by_id_c3e4bfa3 ON project_webhooks USING btree (created_by_id);

CREATE INDEX project_webhooks_project_id_bec3cf8c ON project_webhooks USING btree (project_id);

CREATE INDEX project_webhooks_updated_by_id_a0183aeb ON project_webhooks USING btree (updated_by_id);

CREATE INDEX project_webhooks_webhook_id_da27c6a7 ON project_webhooks USING btree (webhook_id);

CREATE INDEX project_webhooks_workspace_id_429ebf05 ON project_webhooks USING btree (workspace_id);

CREATE UNIQUE INDEX project_webhook_unique_project_webhook_when_deleted_at_null ON project_webhooks USING btree (project_id, webhook_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_webhooks_project_id_webhook_id_deleted_at_dcfdb35d_uniq ON project_webhooks USING btree (project_id, webhook_id, deleted_at);

