@plane @regression
Feature: 视图
  为了反复查看同一组筛选后的工作项
  作为项目成员
  我希望把当前过滤器保存为视图并再次打开

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中
    And 项目 "Dogfood 核心" 中存在工作项 "Dogfood 高优缺陷"

  @smoke @critical
  Scenario: 按优先级筛选后保存为视图
    Given 工作项 "Dogfood 高优缺陷" 的优先级为 "高"
    When 我按以下条件筛选工作项:
      | 优先级 |
      | 高    |
    And 我将当前筛选保存为视图 "Dogfood 仅高优"
    Then 视图列表应包含 "Dogfood 仅高优"

  Scenario: 打开已保存视图仍能看到符合条件的工作项
    Given 项目 "Dogfood 核心" 中存在视图 "Dogfood 仅高优"
    When 我打开视图 "Dogfood 仅高优"
    Then 视图 "Dogfood 仅高优" 中应能看到工作项 "Dogfood 高优缺陷"
