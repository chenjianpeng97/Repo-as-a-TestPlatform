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

