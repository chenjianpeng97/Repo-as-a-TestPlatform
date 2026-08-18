-- auto-generated definition
create table cycles
(
    created_at        timestamptz      not null,
    updated_at        timestamptz      not null,
    id                uuid             not null
        primary key,
    name              varchar(255)     not null,
    description       text             not null,
    start_date        timestamptz      null,
    end_date          timestamptz      null,
    created_by_id     uuid             null,
    owned_by_id       uuid             not null,
    project_id        uuid             not null,
    updated_by_id     uuid             null,
    workspace_id      uuid             not null,
    view_props        jsonb            not null,
    sort_order        double precision not null,
    external_id       varchar(255)     null,
    external_source   varchar(255)     null,
    progress_snapshot jsonb            not null,
    archived_at       timestamptz      null,
    logo_props        jsonb            not null,
    deleted_at        timestamptz      null,
    timezone          varchar(255)     not null,
    version           integer          not null
);

CREATE INDEX cycle_created_by_id_78e43b79 ON cycles USING btree (created_by_id);

CREATE INDEX cycle_owned_by_id_5456a4d1 ON cycles USING btree (owned_by_id);

CREATE INDEX cycle_project_id_0b590349 ON cycles USING btree (project_id);

CREATE INDEX cycle_updated_by_id_93baee43 ON cycles USING btree (updated_by_id);

CREATE INDEX cycle_workspace_id_a199e8e1 ON cycles USING btree (workspace_id);

