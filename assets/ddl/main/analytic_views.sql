-- auto-generated definition
create table analytic_views
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    name          varchar(255) not null,
    description   text         not null,
    query         jsonb        not null,
    query_dict    jsonb        not null,
    created_by_id uuid         null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX analytic_views_created_by_id_1b3ca0a9 ON analytic_views USING btree (created_by_id);

CREATE INDEX analytic_views_updated_by_id_b6d827e1 ON analytic_views USING btree (updated_by_id);

CREATE INDEX analytic_views_workspace_id_ca6e5c0b ON analytic_views USING btree (workspace_id);

-- （analytic_views 暂无数据，无示例 INSERT）
