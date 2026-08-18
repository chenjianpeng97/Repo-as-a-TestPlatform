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

