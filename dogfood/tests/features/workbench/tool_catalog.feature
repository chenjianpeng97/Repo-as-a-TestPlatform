@workbench @dogfood
Feature: 在工作台中发现可用工具
  为了让不擅长编码的成员也能使用团队沉淀的工具
  作为一名测试团队成员
  我希望拉取 workspace 后能在工作台里找到工具并看懂参数

  Background:
    Given 工作台已在本机启动

  @api @wip
  Scenario: 工具目录同时列出私有工具与造数动作词
    When 我查看工具目录
    Then 目录应包含工具 "sample_tool"
    And 目录应包含动作词 "db_seed.sample_seed"
    And 每个条目应带有名称、分组与参数结构

  @ui @wip
  Scenario: 按关键字搜索工具
    When 我在工具目录搜索 "sample"
    Then 结果应只包含名称含 "sample" 的条目

  @ui @wip
  Scenario: 工具详情展示交接说明与参数表单
    When 我打开工具 "sample_tool" 的详情
    Then 应看到该工具的交接说明
    And 表单字段应与参数结构一一对应
