@testcopilot @regression
Feature: Formulation
  为了只读浏览规格仓里的场景与可复用资产
  作为项目成员
  我希望在绑定数据源后看到场景、action words、API、Page 与 DDL

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 未绑定 Formulation 时引导去配置
    Given 项目 "Dogfood 核心" 尚未将 "Formulation" 绑定到数据源
    When 我打开项目模块 "Formulation"
    Then 应看到未绑定引导并提供进入配置的入口

  @critical
  Scenario: 绑定后能浏览场景及其 Scenario
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    And Formulation 场景目录中存在场景 "工作项"
    When 我打开 Formulation 的 "场景"
    Then Formulation 场景列表应包含 "工作项"
    And 场景 "工作项" 应展示其 Scenario 标题

  @smoke
  Scenario: 可从场景引用到 TestCopilot 新建测程
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    And 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    And Formulation 场景目录中存在场景 "工作项"
    When 我打开 Formulation 的 "场景"
    And 我从场景 "工作项" 引用到 TestCopilot
    Then 我应进入新建测程页且已预选场景 "工作项"

  Scenario: 绑定后能浏览 action words
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 Formulation 的 "Action words"
    Then Action words 列表应展示可检索的业务动作或产品空状态

  Scenario: TestCopilot 未绑定时不能执行 action word
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    And 项目 "Dogfood 核心" 尚未将 "TestCopilot" 绑定到数据源
    When 我打开 Formulation 的 "Action words"
    Then 页面应提示需要绑定 TestCopilot 才能执行 action word

  Scenario: 绑定后能浏览 API 文档入口
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 Formulation 的 "API"
    Then API 页应展示可浏览的接口资产或产品空状态

  Scenario: 绑定后能浏览 Page objects
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 Formulation 的 "Page"
    Then Page 页应展示 page objects 或产品空状态

  Scenario: 绑定后能浏览 DDL 索引
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 Formulation 的 "DDL"
    Then DDL 页应展示表结构索引或产品空状态
