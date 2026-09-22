@workbench @dogfood
Feature: 回看工作台的运行历史
  为了追溯谁在什么时候用什么参数跑过哪个工具
  作为一名测试团队成员
  我希望在工作台里按时间回看运行记录并打开日志与产物

  Background:
    Given 工作台已在本机启动

  @api @wip
  Scenario: 历史列表按时间倒序展示最近运行
    Given 我已运行过工具 "sample_tool" 两次
    When 我查看运行历史
    Then 最近一次运行应排在最前
    And 每条记录应包含工具、状态、开始时间与日志链接

  @ui @wip
  Scenario: 打开一次运行可以查看完整日志与产物
    Given 我已运行过工具 "sample_tool" 一次
    When 我打开最近一次运行的详情
    Then 应看到完整日志
    And 应看到该次运行的清单与产物列表
