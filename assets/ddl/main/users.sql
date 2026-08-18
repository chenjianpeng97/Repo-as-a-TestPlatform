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

