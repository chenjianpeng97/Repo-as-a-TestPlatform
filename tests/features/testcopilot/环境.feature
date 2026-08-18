@testcopilot @regression
Feature: 环境
  为了知道被测系统连到哪里
  作为项目成员
  我希望浏览脱敏后的连接与数据源模板，且看不到密钥

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 未绑定环境时引导去配置
    Given 项目 "Dogfood 核心" 尚未将 "环境" 绑定到数据源
    When 我打开项目模块 "环境"
    Then 应看到未绑定引导并提供进入配置的入口

  @critical
  Scenario: 绑定后展示连接目标且不泄露密钥
    Given 项目 "Dogfood 核心" 已将 "环境" 绑定到数据源 "Dogfood 测试仓"
    When 我打开项目模块 "环境"
    Then 环境页应列出连接目标或产品空状态
    And 环境页应提示密码和 token 已脱敏
    And 环境页应仅展示密钥键名而非密钥内容
