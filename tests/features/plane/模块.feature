@plane @regression
Feature: 模块
  为了把复杂项目拆成可跟踪的阶段
  作为项目成员
  我希望创建模块并把相关工作项归入其中

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 创建模块后出现在模块列表
    When 我创建模块:
      | 名称          |
      | Dogfood 发布阶段 |
    Then 模块列表应包含 "Dogfood 发布阶段"

  @critical
  Scenario: 将工作项加入模块后模块内可见
    Given 项目 "Dogfood 核心" 中存在工作项 "Dogfood 模块候选"
    And 项目 "Dogfood 核心" 中存在模块 "Dogfood 发布阶段"
    When 我将工作项 "Dogfood 模块候选" 加入模块 "Dogfood 发布阶段"
    Then 模块 "Dogfood 发布阶段" 应包含工作项 "Dogfood 模块候选"
