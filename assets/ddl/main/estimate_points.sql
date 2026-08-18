-- auto-generated definition
create table estimate_points
(
    created_at    timestamptz  not null,
    updated_at    timestamptz  not null,
    id            uuid         not null
        primary key,
    key           integer      not null,
    description   text         not null,
    value         varchar(255) not null,
    created_by_id uuid         null,
    estimate_id   uuid         not null,
    project_id    uuid         not null,
    updated_by_id uuid         null,
    workspace_id  uuid         not null,
    deleted_at    timestamptz  null
);

CREATE INDEX estimate_points_created_by_id_d1b04bd9 ON estimate_points USING btree (created_by_id);

CREATE INDEX estimate_points_estimate_id_4b4cb706 ON estimate_points USING btree (estimate_id);

CREATE INDEX estimate_points_project_id_ba9bcb2c ON estimate_points USING btree (project_id);

CREATE INDEX estimate_points_updated_by_id_a1da94e1 ON estimate_points USING btree (updated_by_id);

CREATE INDEX estimate_points_workspace_id_96fc4f92 ON estimate_points USING btree (workspace_id);

