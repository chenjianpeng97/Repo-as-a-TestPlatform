-- auto-generated definition
create table page_labels
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    created_by_id uuid        null,
    label_id      uuid        not null,
    page_id       uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX page_labels_created_by_id_fbd942c0 ON page_labels USING btree (created_by_id);

CREATE INDEX page_labels_label_id_05958e53 ON page_labels USING btree (label_id);

CREATE INDEX page_labels_page_id_0e6cdb3d ON page_labels USING btree (page_id);

CREATE INDEX page_labels_updated_by_id_d9fddbff ON page_labels USING btree (updated_by_id);

CREATE INDEX page_labels_workspace_id_078bb01c ON page_labels USING btree (workspace_id);

-- （page_labels 暂无数据，无示例 INSERT）
