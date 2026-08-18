@plane @regression
Feature: 工作项
  为了跟踪任务
  作为项目成员
  我希望在项目中创建工作项并维护优先级与子工作项

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 创建工作项后出现在列表
    When 我创建工作项:
      | 标题           | 优先级 |
      | Dogfood 起草需求 | 中    |
    Then 工作项列表应包含 "Dogfood 起草需求"

  @regression
  Scenario: 为工作项设置优先级后详情可见
    Given 项目 "Dogfood 核心" 中存在工作项 "Dogfood 待排期"
    When 我将工作项 "Dogfood 待排期" 的优先级设为 "高"
    Then 工作项 "Dogfood 待排期" 应显示优先级 "高"

  @regression
  Scenario: 为工作项添加子工作项
    Given 项目 "Dogfood 核心" 中存在工作项 "Dogfood 父任务"
    When 我为工作项 "Dogfood 父任务" 添加子工作项 "Dogfood 子任务"
    Then 工作项 "Dogfood 父任务" 应包含子工作项 "Dogfood 子任务"
