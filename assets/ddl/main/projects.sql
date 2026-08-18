-- auto-generated definition
create table projects
(
    created_at               timestamptz  not null,
    updated_at               timestamptz  not null,
    id                       uuid         not null
        primary key,
    name                     varchar(255) not null,
    description              text         not null,
    description_text         jsonb        null,
    description_html         jsonb        null,
    network                  smallint     not null,
    identifier               varchar(12)  not null,
    created_by_id            uuid         null,
    default_assignee_id      uuid         null,
    project_lead_id          uuid         null,
    updated_by_id            uuid         null,
    workspace_id             uuid         not null,
    emoji                    varchar(255) null,
    cycle_view               boolean      not null,
    module_view              boolean      not null,
    cover_image              text         null,
    issue_views_view         boolean      not null,
    page_view                boolean      not null,
    estimate_id              uuid         null,
    icon_prop                jsonb        null,
    intake_view              boolean      not null,
    archive_in               integer      not null,
    close_in                 integer      not null,
    default_state_id         uuid         null,
    logo_props               jsonb        not null,
    archived_at              timestamptz  null,
    is_time_tracking_enabled boolean      not null,
    is_issue_type_enabled    boolean      not null,
    deleted_at               timestamptz  null,
    guest_view_all_features  boolean      not null,
    timezone                 varchar(255) not null,
    cover_image_asset_id     uuid         null,
    external_id              varchar(255) null,
    external_source          varchar(255) null
);

CREATE INDEX project_created_by_id_6cc13408 ON projects USING btree (created_by_id);

CREATE INDEX project_default_assignee_id_6ba45f90 ON projects USING btree (default_assignee_id);

CREATE INDEX project_project_lead_id_caf8e353 ON projects USING btree (project_lead_id);

CREATE INDEX project_updated_by_id_fe290525 ON projects USING btree (updated_by_id);

CREATE INDEX project_workspace_id_01764ff9 ON projects USING btree (workspace_id);

CREATE INDEX projects_cover_image_asset_id_e6636b92 ON projects USING btree (cover_image_asset_id);

CREATE INDEX projects_default_state_id_f13e8b95 ON projects USING btree (default_state_id);

CREATE INDEX projects_estimate_id_85c7b2ac ON projects USING btree (estimate_id);

CREATE INDEX projects_identifier_3267ade8 ON projects USING btree (identifier);

CREATE INDEX projects_identifier_3267ade8_like ON projects USING btree (identifier varchar_pattern_ops);

CREATE UNIQUE INDEX project_unique_identifier_workspace_when_deleted_at_null ON projects USING btree (identifier, workspace_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_unique_name_workspace_when_deleted_at_null ON projects USING btree (name, workspace_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX projects_identifier_workspace_id_deleted_at_7d2fa8c1_uniq ON projects USING btree (identifier, workspace_id, deleted_at);

CREATE UNIQUE INDEX projects_name_workspace_id_deleted_at_c7aa56f7_uniq ON projects USING btree (name, workspace_id, deleted_at);

