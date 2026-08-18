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

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "file_assets" ("created_at", "updated_at", "id", "attributes", "asset", "created_by_id", "updated_by_id", "workspace_id", "is_deleted", "deleted_at", "is_archived", "comment_id", "entity_type", "external_id", "external_source", "is_uploaded", "issue_id", "page_id", "project_id", "size", "storage_metadata", "user_id", "draft_issue_id", "entity_identifier") VALUES ('2026-08-18 06:25:14.279558+00:00', '2026-08-18 06:25:14.279586+00:00', 'f12e2f02-868d-4443-979b-849629e0c655', '{''name'': ''image_14.jpg'', ''size'': 186911, ''type'': ''image/jpeg''}', '82345500-e469-419d-843d-92902ffac9db/be0738a5a5514f229ff387bc746eafb0-image_14.jpg', 'bb96a7c2-ef4b-466f-a2af-92315b642787', NULL, '82345500-e469-419d-843d-92902ffac9db', FALSE, NULL, FALSE, NULL, 'PROJECT_COVER', NULL, NULL, TRUE, NULL, NULL, NULL, 186911.0, '{}', NULL, NULL, NULL);
