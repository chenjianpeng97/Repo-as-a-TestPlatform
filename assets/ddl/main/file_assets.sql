-- auto-generated definition
create table file_assets
(
    created_at        timestamptz      not null,
    updated_at        timestamptz      not null,
    id                uuid             not null
        primary key,
    attributes        jsonb            not null,
    asset             varchar(800)     not null,
    created_by_id     uuid             null,
    updated_by_id     uuid             null,
    workspace_id      uuid             null,
    is_deleted        boolean          not null,
    deleted_at        timestamptz      null,
    is_archived       boolean          not null,
    comment_id        uuid             null,
    entity_type       varchar(255)     null,
    external_id       varchar(255)     null,
    external_source   varchar(255)     null,
    is_uploaded       boolean          not null,
    issue_id          uuid             null,
    page_id           uuid             null,
    project_id        uuid             null,
    size              double precision not null,
    storage_metadata  jsonb            null,
    user_id           uuid             null,
    draft_issue_id    uuid             null,
    entity_identifier varchar(255)     null
);

CREATE INDEX asset_asset_idx ON file_assets USING btree (asset);

CREATE INDEX asset_entity_identifier_idx ON file_assets USING btree (entity_identifier);

CREATE INDEX asset_entity_idx ON file_assets USING btree (entity_type, entity_identifier);

CREATE INDEX asset_entity_type_idx ON file_assets USING btree (entity_type);

CREATE INDEX file_asset_created_by_id_966942a0 ON file_assets USING btree (created_by_id);

CREATE INDEX file_asset_updated_by_id_d6aaf4f0 ON file_assets USING btree (updated_by_id);

CREATE INDEX file_assets_comment_id_35d4ecaf ON file_assets USING btree (comment_id);

CREATE INDEX file_assets_draft_issue_id_52633145 ON file_assets USING btree (draft_issue_id);

CREATE INDEX file_assets_issue_id_cfe87d6c ON file_assets USING btree (issue_id);

CREATE INDEX file_assets_page_id_64c753d1 ON file_assets USING btree (page_id);

CREATE INDEX file_assets_project_id_ebd5c0d8 ON file_assets USING btree (project_id);

CREATE INDEX file_assets_user_id_ce1818dc ON file_assets USING btree (user_id);

CREATE INDEX file_assets_workspace_id_fa50b9c5 ON file_assets USING btree (workspace_id);

