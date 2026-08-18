-- auto-generated definition
create table api_activity_logs
(
    created_at       timestamptz  not null,
    updated_at       timestamptz  not null,
    id               uuid         not null
        primary key,
    token_identifier varchar(255) not null,
    path             varchar(255) not null,
    method           varchar(10)  not null,
    query_params     text         null,
    headers          text         null,
    body             text         null,
    response_code    integer      not null,
    response_body    text         null,
    ip_address       inet         null,
    user_agent       varchar(512) null,
    created_by_id    uuid         null,
    updated_by_id    uuid         null,
    deleted_at       timestamptz  null
);

CREATE INDEX api_activity_logs_created_by_id_7f5c4ca8 ON api_activity_logs USING btree (created_by_id);

CREATE INDEX api_activity_logs_updated_by_id_9ba0d417 ON api_activity_logs USING btree (updated_by_id);

