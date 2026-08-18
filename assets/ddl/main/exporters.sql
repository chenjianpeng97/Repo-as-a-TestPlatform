-- auto-generated definition
create table exporters
(
    created_at      timestamptz  not null,
    updated_at      timestamptz  not null,
    id              uuid         not null
        primary key,
    project         uuid[]       null,
    provider        varchar(50)  not null,
    status          varchar(50)  not null,
    reason          text         not null,
    key             text         not null,
    url             varchar(800) null,
    token           varchar(255) not null,
    created_by_id   uuid         null,
    initiated_by_id uuid         not null,
    updated_by_id   uuid         null,
    workspace_id    uuid         not null,
    filters         jsonb        null,
    name            varchar(255) null,
    type            varchar(50)  not null,
    deleted_at      timestamptz  null,
    rich_filters    jsonb        null
);

CREATE INDEX exporters_created_by_id_44e1d9b3 ON exporters USING btree (created_by_id);

CREATE INDEX exporters_initiated_by_id_d51f7552 ON exporters USING btree (initiated_by_id);

CREATE INDEX exporters_token_c774aeeb_like ON exporters USING btree (token varchar_pattern_ops);

CREATE INDEX exporters_updated_by_id_d2572861 ON exporters USING btree (updated_by_id);

CREATE INDEX exporters_workspace_id_11a04317 ON exporters USING btree (workspace_id);

CREATE UNIQUE INDEX exporters_token_key ON exporters USING btree (token);

