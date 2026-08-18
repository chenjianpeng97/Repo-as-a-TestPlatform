-- auto-generated definition
create table changelogs
(
    created_at           timestamptz  not null,
    updated_at           timestamptz  not null,
    id                   uuid         not null
        primary key,
    title                varchar(255) not null,
    description          text         not null,
    version              varchar(255) not null,
    tags                 jsonb        not null,
    release_date         timestamptz  null,
    is_release_candidate boolean      not null,
    created_by_id        uuid         null,
    updated_by_id        uuid         null,
    deleted_at           timestamptz  null
);

CREATE INDEX changelogs_created_by_id_16dd944a ON changelogs USING btree (created_by_id);

CREATE INDEX changelogs_updated_by_id_e0989861 ON changelogs USING btree (updated_by_id);

