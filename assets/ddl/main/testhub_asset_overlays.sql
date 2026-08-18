-- auto-generated definition
create table testhub_asset_overlays
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    deleted_at    timestamptz  null,
    id            uuid         not null
        primary key,
    created_by_id uuid         null,
    updated_by_id uuid         null,
    asset_ref     varchar(512) not null,
    kind          varchar(64)  not null,
    payload       jsonb        not null,
    project_id    uuid         not null,
    workspace_id  uuid         not null
);

CREATE INDEX testhub_asset_overlays_created_by_id_c9e9641f ON testhub_asset_overlays USING btree (created_by_id);

CREATE INDEX testhub_asset_overlays_project_id_b83658d1 ON testhub_asset_overlays USING btree (project_id);

CREATE INDEX testhub_asset_overlays_updated_by_id_7d1793b7 ON testhub_asset_overlays USING btree (updated_by_id);

CREATE INDEX testhub_asset_overlays_workspace_id_e4cc5d1b ON testhub_asset_overlays USING btree (workspace_id);

CREATE INDEX testhub_ove_project_idx ON testhub_asset_overlays USING btree (project_id, kind);

CREATE UNIQUE INDEX testhub_overlay_project_asset_kind_uniq ON testhub_asset_overlays USING btree (project_id, asset_ref, kind);

-- （testhub_asset_overlays 暂无数据，无示例 INSERT）
