@testcopilot @regression
Feature: 作业
  为了在白名单内触发测试仓命令并查看结果
  作为项目成员
  我希望未绑定时展示引导，绑定后能运行允许的工具并在作业页看到记录

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 未绑定 TestCopilot 时作业页引导去配置
    Given 项目 "Dogfood 核心" 尚未将 "TestCopilot" 绑定到数据源
    When 我打开项目模块 "作业"
    Then 应看到未绑定引导并提供进入配置的入口

  Scenario: 绑定后尚无作业时展示空状态
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    And 项目 "Dogfood 核心" 尚无作业记录
    When 我打开项目模块 "作业"
    Then 作业页应展示尚无作业的空状态

  @smoke
  Scenario: 运行 dump_ddl 前未填表名应看到提示
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 TestCopilot 的 "工具"
    And 我在未填写表名时运行工具 "dump_ddl"
    Then 页面应提示 dump_ddl 至少需要一张表

  @critical
  Scenario: 运行白名单工具后作业中出现对应记录
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 TestCopilot 的 "工具"
    And 我使用已登记的业务表运行工具 "dump_ddl"
    Then 我应进入作业详情
    And 作业详情的类型应为 "dump_ddl"

  Scenario: 非白名单工具显示不可运行
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    And TestCopilot 目录中存在未在白名单的工具
    When 我打开 TestCopilot 的 "工具"
    Then 非白名单工具应显示不可运行

  Scenario: 未确认写入时破坏性 action word 不应入队
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    And 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    And Formulation 中存在可写入被测系统的 action word
    When 我打开 Formulation 的 "Action words"
    And 我在未确认写入的情况下运行该 action word
    Then 该 action word 不应入队作业

  Scenario: 确认写入后破坏性 action word 进入作业
    Given 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    And 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    And Formulation 中存在可写入被测系统的 action word
    When 我打开 Formulation 的 "Action words"
    And 我确认该操作会写入被测系统并运行该 action word
    Then 我应进入作业详情
