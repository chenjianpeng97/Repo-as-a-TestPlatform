-- auto-generated definition
create table social_login_connections
(
    created_at       timestamptz not null,
    updated_at       timestamptz not null,
    id               uuid        not null
        primary key,
    medium           varchar(20) not null,
    last_login_at    timestamptz null,
    last_received_at timestamptz null,
    token_data       jsonb       null,
    extra_data       jsonb       null,
    created_by_id    uuid        null,
    updated_by_id    uuid        null,
    user_id          uuid        not null,
    deleted_at       timestamptz null
);

CREATE INDEX social_login_connection_created_by_id_7ca2ef50 ON social_login_connections USING btree (created_by_id);

CREATE INDEX social_login_connection_updated_by_id_c13deb42 ON social_login_connections USING btree (updated_by_id);

CREATE INDEX social_login_connection_user_id_0e26c0c5 ON social_login_connections USING btree (user_id);

-- （social_login_connections 暂无数据，无示例 INSERT）
