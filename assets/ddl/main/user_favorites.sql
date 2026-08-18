-- auto-generated definition
create table user_favorites
(
    created_at        timestamptz      not null,
    updated_at        timestamptz      not null,
    id                uuid             not null
        primary key,
    entity_type       varchar(100)     not null,
    entity_identifier uuid             null,
    name              varchar(255)     null,
    is_folder         boolean          not null,
    sequence          double precision not null,
    created_by_id     uuid             null,
    parent_id         uuid             null,
    project_id        uuid             null,
    updated_by_id     uuid             null,
    user_id           uuid             not null,
    workspace_id      uuid             not null,
    deleted_at        timestamptz      null
);

CREATE INDEX fav_entity_identifier_idx ON user_favorites USING btree (entity_identifier);

CREATE INDEX fav_entity_idx ON user_favorites USING btree (entity_type, entity_identifier);

CREATE INDEX fav_entity_type_idx ON user_favorites USING btree (entity_type);

CREATE INDEX user_favorites_created_by_id_dc025309 ON user_favorites USING btree (created_by_id);

CREATE INDEX user_favorites_parent_id_550512e4 ON user_favorites USING btree (parent_id);

CREATE INDEX user_favorites_project_id_359b527f ON user_favorites USING btree (project_id);

CREATE INDEX user_favorites_updated_by_id_a1a5ac4a ON user_favorites USING btree (updated_by_id);

CREATE INDEX user_favorites_user_id_cea7e2d2 ON user_favorites USING btree (user_id);

CREATE INDEX user_favorites_workspace_id_aa90f680 ON user_favorites USING btree (workspace_id);

CREATE UNIQUE INDEX user_favorite_unique_entity_type_entity_identifier_user_when_de ON user_favorites USING btree (entity_type, entity_identifier, user_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX user_favorites_entity_type_user_id_enti_22b103ff_uniq ON user_favorites USING btree (entity_type, user_id, entity_identifier, deleted_at);

-- （user_favorites 暂无数据，无示例 INSERT）
