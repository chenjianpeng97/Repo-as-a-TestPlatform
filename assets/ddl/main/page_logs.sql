-- auto-generated definition
create table page_logs
(
    created_at        timestamptz not null,
    updated_at        timestamptz not null,
    id                uuid        not null
        primary key,
    transaction       uuid        not null,
    entity_identifier uuid        null,
    entity_name       varchar(30) not null,
    created_by_id     uuid        null,
    page_id           uuid        not null,
    updated_by_id     uuid        null,
    workspace_id      uuid        not null,
    deleted_at        timestamptz null,
    entity_type       varchar(30) null
);

CREATE INDEX page_logs_created_by_id_4a295aec ON page_logs USING btree (created_by_id);

CREATE INDEX page_logs_page_id_0e0d747d ON page_logs USING btree (page_id);

CREATE INDEX page_logs_updated_by_id_1995190b ON page_logs USING btree (updated_by_id);

CREATE INDEX page_logs_workspace_id_be7bde64 ON page_logs USING btree (workspace_id);

CREATE INDEX pagelog_entity_id_idx ON page_logs USING btree (entity_identifier);

CREATE INDEX pagelog_entity_name_idx ON page_logs USING btree (entity_name);

CREATE INDEX pagelog_entity_type_idx ON page_logs USING btree (entity_type);

CREATE INDEX pagelog_name_id_idx ON page_logs USING btree (entity_name, entity_identifier);

CREATE INDEX pagelog_type_id_idx ON page_logs USING btree (entity_type, entity_identifier);

CREATE UNIQUE INDEX page_logs_page_id_transaction_9ab05334_uniq ON page_logs USING btree (page_id, transaction);

-- （page_logs 暂无数据，无示例 INSERT）
