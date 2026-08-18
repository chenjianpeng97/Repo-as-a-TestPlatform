-- auto-generated definition
create table modules
(
    created_at       timestamptz      not null,
    updated_at       timestamptz      not null,
    id               uuid             not null
        primary key,
    name             varchar(255)     not null,
    description      text             not null,
    description_text jsonb            null,
    description_html jsonb            null,
    start_date       date             null,
    target_date      date             null,
    status           varchar(20)      not null,
    created_by_id    uuid             null,
    lead_id          uuid             null,
    project_id       uuid             not null,
    updated_by_id    uuid             null,
    workspace_id     uuid             not null,
    view_props       jsonb            not null,
    sort_order       double precision not null,
    external_id      varchar(255)     null,
    external_source  varchar(255)     null,
    archived_at      timestamptz      null,
    logo_props       jsonb            not null,
    deleted_at       timestamptz      null
);

CREATE INDEX module_created_by_id_ff7a5866 ON modules USING btree (created_by_id);

CREATE INDEX module_lead_id_04966630 ON modules USING btree (lead_id);

CREATE INDEX module_project_id_da84b04f ON modules USING btree (project_id);

CREATE INDEX module_updated_by_id_72ab6d5c ON modules USING btree (updated_by_id);

CREATE INDEX module_workspace_id_0a826fef ON modules USING btree (workspace_id);

CREATE UNIQUE INDEX module_unique_name_project_when_deleted_at_null ON modules USING btree (name, project_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX modules_name_project_id_deleted_at_328e2346_uniq ON modules USING btree (name, project_id, deleted_at);

