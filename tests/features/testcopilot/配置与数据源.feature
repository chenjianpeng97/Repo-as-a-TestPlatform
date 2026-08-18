@testcopilot @regression
Feature: 配置与数据源
  为了让项目成分读到测试仓
  作为项目管理员
  我希望登记本地挂载数据源并把各模块绑上去

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 未登记数据源时配置页给出本地挂载说明
    Given 项目 "Dogfood 核心" 尚未绑定任何数据源
    When 我打开项目模块 "配置"
    Then 配置页应提示可以添加本地挂载数据源

  @critical
  Scenario: 添加本地挂载数据源后出现在列表
    Given 项目 "Dogfood 核心" 尚未绑定任何数据源
    When 我打开项目模块 "配置"
    And 我添加本地挂载数据源:
      | 名称           | 类型     |
      | Dogfood 测试仓 | 本地挂载 |
    Then 数据源列表应包含 "Dogfood 测试仓"
    And 页面应提示数据源已保存

  @critical
  Scenario: 将三个产品模块绑到同一数据源
    Given 项目 "Dogfood 核心" 已登记本地挂载数据源 "Dogfood 测试仓"
    When 我打开项目模块 "配置"
    And 我将以下产品模块绑定到数据源 "Dogfood 测试仓":
      | 产品模块      |
      | Formulation |
      | 环境          |
      | TestCopilot |
    And 我保存模块绑定
    Then 产品模块 "Formulation" 应绑定到数据源 "Dogfood 测试仓"
    And 产品模块 "环境" 应绑定到数据源 "Dogfood 测试仓"
    And 产品模块 "TestCopilot" 应绑定到数据源 "Dogfood 测试仓"
    And 页面应提示模块绑定已保存

  @smoke
  Scenario: 同步本地挂载数据源后能看到完成提示
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    When 我打开项目模块 "配置"
    And 我同步数据源 "Dogfood 测试仓"
    Then 页面应提示同步完成

  @skip
  Scenario: 选择 Git URL 类型时同步应提示尚未提供（clone/fetch 未实现）
    Given 项目 "Dogfood 核心" 已登记 Git URL 数据源 "Dogfood 远程仓"
    When 我打开项目模块 "配置"
    And 我同步数据源 "Dogfood 远程仓"
    Then 页面应提示 Git URL 同步尚未提供
