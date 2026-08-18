-- auto-generated definition
create table instance_admins
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    role          integer     not null,
    is_verified   boolean     not null,
    created_by_id uuid        null,
    instance_id   uuid        not null,
    updated_by_id uuid        null,
    user_id       uuid        null,
    deleted_at    timestamptz null
);

CREATE INDEX instance_admins_created_by_id_7f4e03b4 ON instance_admins USING btree (created_by_id);

CREATE INDEX instance_admins_instance_id_66d1ba73 ON instance_admins USING btree (instance_id);

CREATE INDEX instance_admins_updated_by_id_b7800403 ON instance_admins USING btree (updated_by_id);

CREATE INDEX instance_admins_user_id_cc6e9b62 ON instance_admins USING btree (user_id);

CREATE UNIQUE INDEX instance_admins_instance_id_user_id_2e80a466_uniq ON instance_admins USING btree (instance_id, user_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "instance_admins" ("created_at", "updated_at", "id", "role", "is_verified", "created_by_id", "instance_id", "updated_by_id", "user_id", "deleted_at") VALUES ('2026-07-10 12:35:44.231826+00:00', '2026-07-10 12:35:44.231838+00:00', '1a5a63ef-2aa3-47e6-9266-e58f0af21432', 20, FALSE, NULL, 'c46dfded-9d14-4abe-9cf5-79ebe07f8149', NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL);
