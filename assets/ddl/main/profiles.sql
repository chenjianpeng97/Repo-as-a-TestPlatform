-- auto-generated definition
create table profiles
(
    created_at                   timestamptz  not null,
    updated_at                   timestamptz  not null,
    id                           uuid         not null
        primary key,
    theme                        jsonb        not null,
    is_tour_completed            boolean      not null,
    onboarding_step              jsonb        not null,
    use_case                     text         null,
    role                         varchar(300) null,
    is_onboarded                 boolean      not null,
    last_workspace_id            uuid         null,
    billing_address_country      varchar(255) not null,
    billing_address              jsonb        null,
    has_billing_address          boolean      not null,
    company_name                 varchar(255) not null,
    user_id                      uuid         not null,
    is_mobile_onboarded          boolean      not null,
    mobile_onboarding_step       jsonb        not null,
    mobile_timezone_auto_set     boolean      not null,
    language                     varchar(255) not null,
    is_smooth_cursor_enabled     boolean      not null,
    start_of_the_week            smallint     not null,
    is_app_rail_docked           boolean      not null,
    background_color             varchar(255) not null,
    goals                        jsonb        not null,
    has_marketing_email_consent  boolean      not null,
    is_navigation_tour_completed boolean      not null,
    is_subscribed_to_changelog   boolean      not null,
    notification_view_mode       varchar(255) not null,
    product_tour                 jsonb        not null
);

CREATE UNIQUE INDEX profiles_user_id_key ON profiles USING btree (user_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "profiles" ("created_at", "updated_at", "id", "theme", "is_tour_completed", "onboarding_step", "use_case", "role", "is_onboarded", "last_workspace_id", "billing_address_country", "billing_address", "has_billing_address", "company_name", "user_id", "is_mobile_onboarded", "mobile_onboarding_step", "mobile_timezone_auto_set", "language", "is_smooth_cursor_enabled", "start_of_the_week", "is_app_rail_docked", "background_color", "goals", "has_marketing_email_consent", "is_navigation_tour_completed", "is_subscribed_to_changelog", "notification_view_mode", "product_tour") VALUES ('2026-07-10 12:35:44.206489+00:00', '2026-07-10 13:40:13.638681+00:00', 'e7f99604-fa77-41d5-aec7-5111587537f0', '{''theme'': ''light''}', TRUE, '{''workspace_join'': True, ''profile_complete'': True, ''workspace_create'': True, ''workspace_invite'': True}', NULL, NULL, TRUE, '6f2f3ff8-62de-4127-978b-54991c166df3', 'INDIA', NULL, FALSE, 'Chen', '9d1f264d-7dee-48c5-ab98-087db907b8a1', FALSE, '{''workspace_join'': False, ''profile_complete'': False, ''workspace_create'': False}', FALSE, 'zh-CN', FALSE, 0, TRUE, '#AdF648', '{}', TRUE, FALSE, FALSE, 'full', '{''pages'': False, ''cycles'': False, ''intake'': False, ''modules'': False, ''work_items'': False}');
