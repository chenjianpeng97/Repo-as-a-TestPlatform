-- auto-generated definition
create table workspaces
(
    created_at        timestamptz  not null,
    updated_at        timestamptz  not null,
    id                uuid         not null
        primary key,
    name              varchar(80)  not null,
    logo              text         null,
    slug              varchar(48)  not null,
    created_by_id     uuid         null,
    owner_id          uuid         not null,
    updated_by_id     uuid         null,
    organization_size varchar(20)  null,
    deleted_at        timestamptz  null,
    logo_asset_id     uuid         null,
    timezone          varchar(255) not null,
    background_color  varchar(255) not null
);

CREATE INDEX workspace_created_by_id_10ad894e ON workspaces USING btree (created_by_id);

CREATE INDEX workspace_owner_id_60a8bafc ON workspaces USING btree (owner_id);

CREATE INDEX workspace_slug_4d89d459_like ON workspaces USING btree (slug varchar_pattern_ops);

CREATE INDEX workspace_updated_by_id_09d249ed ON workspaces USING btree (updated_by_id);

CREATE INDEX workspaces_logo_asset_id_a784bb00 ON workspaces USING btree (logo_asset_id);

CREATE UNIQUE INDEX workspace_slug_key ON workspaces USING btree (slug);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "workspaces" ("created_at", "updated_at", "id", "name", "logo", "slug", "created_by_id", "owner_id", "updated_by_id", "organization_size", "deleted_at", "logo_asset_id", "timezone", "background_color") VALUES ('2026-08-03 12:45:41.453014+00:00', '2026-08-03 12:45:41.453024+00:00', '82345500-e469-419d-843d-92902ffac9db', 'tunerhome', NULL, 'tunerhome', 'bb96a7c2-ef4b-466f-a2af-92315b642787', 'bb96a7c2-ef4b-466f-a2af-92315b642787', NULL, 'Just myself', NULL, NULL, 'UTC', '#30Fe8D');
