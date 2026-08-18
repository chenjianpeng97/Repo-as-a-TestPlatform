@plane @regression
Feature: 周期
  为了在限时块中推进工作
  作为项目成员
  我希望创建周期并把工作项放进去，以便查看进度

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 创建周期后出现在周期列表
    When 我创建周期:
      | 名称            | 开始日期     | 结束日期     |
      | Dogfood 本周冲刺 | 2026-08-17 | 2026-08-23 |
    Then 周期列表应包含 "Dogfood 本周冲刺"

  @critical
  Scenario: 将工作项加入周期后周期内可见
    Given 项目 "Dogfood 核心" 中存在工作项 "Dogfood 周期候选"
    And 项目 "Dogfood 核心" 中存在周期 "Dogfood 本周冲刺"
    When 我将工作项 "Dogfood 周期候选" 加入周期 "Dogfood 本周冲刺"
    Then 周期 "Dogfood 本周冲刺" 应包含工作项 "Dogfood 周期候选"

  Scenario: 周期内有工作项后展示进度或燃尽区域
    Given 项目 "Dogfood 核心" 中存在周期 "Dogfood 本周冲刺"
    And 周期 "Dogfood 本周冲刺" 中包含工作项 "Dogfood 周期候选"
    When 我打开周期 "Dogfood 本周冲刺"
    Then 周期 "Dogfood 本周冲刺" 应展示进度或燃尽信息
