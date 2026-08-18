@plane @regression
Feature: 页面
  为了把想法沉淀为可检索的文档
  作为项目成员
  我希望创建页面并写下正文

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 创建页面后出现在页面列表
    When 我创建页面 "Dogfood 发布说明"
    Then 页面列表应包含 "Dogfood 发布说明"

  Scenario: 在页面中写入正文后再打开仍能看到
    Given 项目 "Dogfood 核心" 中存在页面 "Dogfood 发布说明"
    When 我在页面 "Dogfood 发布说明" 中写入正文 "本周只回归社区版核心路径"
    Then 页面 "Dogfood 发布说明" 应展示正文 "本周只回归社区版核心路径"
