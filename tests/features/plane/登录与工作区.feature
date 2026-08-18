@plane @regression
Feature: 登录与工作区
  为了进入 Plane 管理项目
  作为已开通账号的成员
  我希望能登录工作区并打开或创建项目

  @smoke @critical
  Scenario: 使用已配置账号登录后进入工作区
    Given 我打开 Plane
    When 我使用已配置的测试账号登录
    Then 我应进入工作区

  @smoke @critical
  Scenario: 打开已有项目
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    When 我打开项目 "Dogfood 核心"
    Then 我应看到项目 "Dogfood 核心" 的工作项入口

  @regression
  Scenario: 创建新项目后出现在项目列表
    Given 我已登录 Plane
    When 我创建项目 "Dogfood 新建项目"
    Then 项目列表应包含 "Dogfood 新建项目"

  @regression
  Scenario: 打开工作区分析能看到洞察区域
    Given 我已登录 Plane
    When 我打开工作区分析
    Then 分析页应展示可观测的项目洞察
