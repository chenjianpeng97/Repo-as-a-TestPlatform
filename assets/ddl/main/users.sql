-- auto-generated definition
create table users
(
    password                   varchar(128) not null,
    last_login                 timestamptz  null,
    id                         uuid         not null
        primary key,
    username                   varchar(128) not null,
    mobile_number              varchar(255) null,
    email                      varchar(255) null,
    first_name                 varchar(255) not null,
    last_name                  varchar(255) not null,
    avatar                     text         not null,
    date_joined                timestamptz  not null,
    created_at                 timestamptz  not null,
    updated_at                 timestamptz  not null,
    last_location              varchar(255) not null,
    created_location           varchar(255) not null,
    is_superuser               boolean      not null,
    is_managed                 boolean      not null,
    is_password_expired        boolean      not null,
    is_active                  boolean      not null,
    is_staff                   boolean      not null,
    is_email_verified          boolean      not null,
    is_password_autoset        boolean      not null,
    token                      varchar(64)  not null,
    user_timezone              varchar(255) not null,
    last_active                timestamptz  null,
    last_login_time            timestamptz  null,
    last_logout_time           timestamptz  null,
    last_login_ip              varchar(255) not null,
    last_logout_ip             varchar(255) not null,
    last_login_medium          varchar(20)  not null,
    last_login_uagent          text         not null,
    token_updated_at           timestamptz  null,
    is_bot                     boolean      not null,
    cover_image                varchar(800) null,
    display_name               varchar(255) not null,
    avatar_asset_id            uuid         null,
    cover_image_asset_id       uuid         null,
    bot_type                   varchar(30)  null,
    is_email_valid             boolean      not null,
    masked_at                  timestamptz  null,
    is_password_reset_required boolean      not null
);

CREATE INDEX user_email_54dc62b2_like ON users USING btree (email varchar_pattern_ops);

CREATE INDEX user_username_cf016618_like ON users USING btree (username varchar_pattern_ops);

CREATE INDEX users_avatar_asset_id_50fa2043 ON users USING btree (avatar_asset_id);

CREATE INDEX users_cover_image_asset_id_b9679cbc ON users USING btree (cover_image_asset_id);

CREATE UNIQUE INDEX user_email_key ON users USING btree (email);

CREATE UNIQUE INDEX user_username_key ON users USING btree (username);

-- 最新一条数据示例（latest id），已排除生成列，已排除密钥列 password, token，仅供数据构造参考
-- INSERT INTO "users" ("last_login", "id", "username", "mobile_number", "email", "first_name", "last_name", "avatar", "date_joined", "created_at", "updated_at", "last_location", "created_location", "is_superuser", "is_managed", "is_password_expired", "is_active", "is_staff", "is_email_verified", "is_password_autoset", "user_timezone", "last_active", "last_login_time", "last_logout_time", "last_login_ip", "last_logout_ip", "last_login_medium", "last_login_uagent", "token_updated_at", "is_bot", "cover_image", "display_name", "avatar_asset_id", "cover_image_asset_id", "bot_type", "is_email_valid", "masked_at", "is_password_reset_required") VALUES ('2026-08-16 02:23:46.403396+00:00', 'bb96a7c2-ef4b-466f-a2af-92315b642787', 'e62ba479f592487492e93ee546392f22', NULL, 'chenjianpeng97@outlook.com', 'tuner', '', '', '2026-08-03 12:44:48.568808+00:00', '2026-08-03 12:44:48.568821+00:00', '2026-08-16 02:23:46.358078+00:00', '', '', FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, 'UTC', '2026-08-16 02:23:46.357416+00:00', '2026-08-16 02:23:46.357420+00:00', NULL, '172.19.0.1', '', 'email', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36', '2026-08-16 02:23:46.357480+00:00', FALSE, NULL, 'chenjianpeng97', NULL, NULL, NULL, FALSE, NULL, FALSE);
