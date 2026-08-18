-- auto-generated definition
create table webhook_logs
(
    created_at       timestamptz  not null,
    updated_at       timestamptz  not null,
    id               uuid         not null
        primary key,
    event_type       varchar(255) null,
    request_method   varchar(10)  null,
    request_headers  text         null,
    request_body     text         null,
    response_status  text         null,
    response_headers text         null,
    response_body    text         null,
    retry_count      smallint     not null,
    created_by_id    uuid         null,
    updated_by_id    uuid         null,
    webhook          uuid         not null,
    workspace_id     uuid         not null,
    deleted_at       timestamptz  null
);

CREATE INDEX webhook_logs_created_by_id_71e7bc38 ON webhook_logs USING btree (created_by_id);

CREATE INDEX webhook_logs_updated_by_id_3d9bad04 ON webhook_logs USING btree (updated_by_id);

CREATE INDEX webhook_logs_workspace_id_ffcd0e31 ON webhook_logs USING btree (workspace_id);

