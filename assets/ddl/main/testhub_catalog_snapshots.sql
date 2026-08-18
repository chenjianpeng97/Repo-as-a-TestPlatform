-- auto-generated definition
create table testhub_catalog_snapshots
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    deleted_at    timestamptz null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    updated_by_id uuid        null,
    sha           varchar(64) not null,
    payload       jsonb       not null,
    project_id    uuid        not null,
    workspace_id  uuid        not null
);

CREATE INDEX testhub_cat_project_idx ON testhub_catalog_snapshots USING btree (project_id, created_at DESC);

CREATE INDEX testhub_catalog_snapshots_created_by_id_6e5bc7cb ON testhub_catalog_snapshots USING btree (created_by_id);

CREATE INDEX testhub_catalog_snapshots_project_id_89ddb687 ON testhub_catalog_snapshots USING btree (project_id);

CREATE INDEX testhub_catalog_snapshots_updated_by_id_12bfaf8d ON testhub_catalog_snapshots USING btree (updated_by_id);

CREATE INDEX testhub_catalog_snapshots_workspace_id_be1e5cba ON testhub_catalog_snapshots USING btree (workspace_id);

-- （testhub_catalog_snapshots 最新一行过长，已省略示例 INSERT；常见于 stdout / jsonb。需要样例时对该表单独查询）
