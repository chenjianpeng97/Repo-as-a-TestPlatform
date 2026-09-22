@workbench @dogfood
Feature: 在工作台中填写参数并运行工具
  为了不写命令行也能使用团队工具
  作为一名测试团队成员
  我希望在表单里填参数、点运行，并看到结果与产物

  Background:
    Given 工作台已在本机启动

  @api @wip
  Scenario: 用表单参数运行工具并看到成功结果
    When 我以下列参数运行工具 "sample_tool":
      | name  | value |
      | count | 3     |
      | label | demo  |
    Then 运行状态应为 "succeeded"
    And 运行日志应包含 "label=demo"
    And 交付物目录应出现该次运行的清单文件

  @api @wip
  Scenario: 破坏性动作词未确认时拒绝运行
    When 我未勾选确认就运行动作词 "db_seed.sample_seed"
    Then 运行应被拒绝并提示需要确认

  @api @wip
  Scenario: 破坏性动作词确认后以 dry-run 运行
    When 我勾选确认并以 dry-run 运行动作词 "db_seed.sample_seed"
    Then 运行状态应为 "succeeded"
    And 运行日志应包含 "dry-run"

  @api @wip
  Scenario: 缺少必填参数时表单校验失败
    When 我不填必填参数直接运行工具 "sample_tool"
    Then 运行应被拒绝并指出缺少的参数
