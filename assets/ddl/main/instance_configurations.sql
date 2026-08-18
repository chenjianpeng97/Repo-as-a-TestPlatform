-- auto-generated definition
create table instance_configurations
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    key           varchar(100) not null,
    value         text         null,
    category      text         not null,
    is_encrypted  boolean      not null,
    created_by_id uuid         null,
    updated_by_id uuid         null,
    deleted_at    timestamptz  null
);

CREATE INDEX instance_configurations_created_by_id_e683f3e5 ON instance_configurations USING btree (created_by_id);

CREATE INDEX instance_configurations_key_3eb64d36_like ON instance_configurations USING btree (key varchar_pattern_ops);

CREATE INDEX instance_configurations_updated_by_id_f0d7542e ON instance_configurations USING btree (updated_by_id);

CREATE UNIQUE INDEX instance_configurations_key_key ON instance_configurations USING btree (key);

