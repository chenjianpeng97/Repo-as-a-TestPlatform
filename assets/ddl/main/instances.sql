-- auto-generated definition
create table instances
(
    created_at                    timestamptz  not null,
    updated_at                    timestamptz  not null,
    id                            uuid         not null
        primary key,
    instance_name                 varchar(255) not null,
    whitelist_emails              text         null,
    instance_id                   varchar(255) not null,
    current_version               varchar(255) not null,
    last_checked_at               timestamptz  not null,
    namespace                     varchar(255) null,
    is_telemetry_enabled          boolean      not null,
    is_support_required           boolean      not null,
    is_setup_done                 boolean      not null,
    is_signup_screen_visited      boolean      not null,
    is_verified                   boolean      not null,
    created_by_id                 uuid         null,
    updated_by_id                 uuid         null,
    domain                        text         not null,
    latest_version                varchar(255) null,
    edition                       varchar(255) not null,
    deleted_at                    timestamptz  null,
    is_test                       boolean      not null,
    is_current_version_deprecated boolean      not null
);

CREATE INDEX instances_created_by_id_c76e92ef ON instances USING btree (created_by_id);

CREATE INDEX instances_instance_id_cf688621_like ON instances USING btree (instance_id varchar_pattern_ops);

CREATE INDEX instances_updated_by_id_cce8fcdf ON instances USING btree (updated_by_id);

CREATE UNIQUE INDEX instances_instance_id_key ON instances USING btree (instance_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "instances" ("created_at", "updated_at", "id", "instance_name", "whitelist_emails", "instance_id", "current_version", "last_checked_at", "namespace", "is_telemetry_enabled", "is_support_required", "is_setup_done", "is_signup_screen_visited", "is_verified", "created_by_id", "updated_by_id", "domain", "latest_version", "edition", "deleted_at", "is_test", "is_current_version_deprecated") VALUES ('2026-07-10 12:26:12.456300+00:00', '2026-08-18 07:42:27.424724+00:00', 'c46dfded-9d14-4abe-9cf5-79ebe07f8149', 'Chen', NULL, 'bcfc4268f6116a8120184ad9', '1.4.1', '2026-08-18 07:42:27.424140+00:00', NULL, TRUE, TRUE, TRUE, FALSE, FALSE, NULL, NULL, '', '1.4.1', 'PLANE_COMMUNITY', NULL, FALSE, FALSE);
