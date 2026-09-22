@workbench @dogfood
Feature: 在工作台中浏览工作区知识
  为了不打开 IDE 也能了解工作区里有什么
  作为一名测试团队成员
  我希望在工作台首页看到统计，并能浏览知识文件与当前环境

  Background:
    Given 工作台已在本机启动

  @api @wip
  Scenario: 首页展示工作区统计
    When 我打开工作台首页
    Then 应看到工具、动作词、知识文件与 feature 的数量
    And 应看到当前分支与最近的任务记录

  @ui @wip
  Scenario: 浏览知识层文件的元数据
    When 我打开知识浏览页
    Then 应看到 "roadmap" 条目及其 domain 与 confidence

  @api @wip
  Scenario: 切换命名环境只显示环境名
    Given 本机配置了环境 "dev" 与 "uat"
    When 我把当前环境切换为 "uat"
    Then 当前环境应显示为 "uat"
    And 页面不应出现任何密码或令牌
