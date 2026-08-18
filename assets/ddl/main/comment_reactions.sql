-- auto-generated definition
create table comment_reactions
(
    created_at    timestamptz not null,
    updated_at    timestamptz not null,
    id            uuid        not null
        primary key,
    reaction      text        not null,
    actor_id      uuid        not null,
    comment_id    uuid        not null,
    created_by_id uuid        null,
    project_id    uuid        not null,
    updated_by_id uuid        null,
    workspace_id  uuid        not null,
    deleted_at    timestamptz null
);

CREATE INDEX comment_reactions_actor_id_21219e9c ON comment_reactions USING btree (actor_id);

CREATE INDEX comment_reactions_comment_id_87c59446 ON comment_reactions USING btree (comment_id);

CREATE INDEX comment_reactions_created_by_id_9aeb43c4 ON comment_reactions USING btree (created_by_id);

CREATE INDEX comment_reactions_project_id_ab9114b4 ON comment_reactions USING btree (project_id);

CREATE INDEX comment_reactions_updated_by_id_c74c9bbd ON comment_reactions USING btree (updated_by_id);

CREATE INDEX comment_reactions_workspace_id_b614ca4f ON comment_reactions USING btree (workspace_id);

CREATE UNIQUE INDEX comment_reaction_unique_comment_actor_reaction_when_deleted_at_ ON comment_reactions USING btree (comment_id, actor_id, reaction) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX comment_reactions_comment_id_actor_id_reac_24dc2de6_uniq ON comment_reactions USING btree (comment_id, actor_id, reaction, deleted_at);

-- （comment_reactions 暂无数据，无示例 INSERT）
