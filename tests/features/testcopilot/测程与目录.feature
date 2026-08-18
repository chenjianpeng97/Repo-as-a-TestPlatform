@testcopilot @regression
Feature: TestCopilot 测程与目录
  为了引用 Formulation 场景并只读浏览测试仓目录
  作为项目成员
  我希望在绑定后看到总览、常用 SQL、pytest 节点，并能创建待执行测程

  Background:
    Given 我已登录 Plane
    And 当前工作区存在项目 "Dogfood 核心"
    And 我在项目 "Dogfood 核心" 中

  @smoke @critical
  Scenario: 未绑定 TestCopilot 时引导去配置
    Given 项目 "Dogfood 核心" 尚未将 "TestCopilot" 绑定到数据源
    When 我打开项目模块 "TestCopilot"
    Then 应看到未绑定引导并提供进入配置的入口

  @critical
  Scenario: 绑定后总览展示仓库与资产入口
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    When 我打开项目模块 "TestCopilot"
    Then TestCopilot 总览应展示绑定仓库与同步状态
    And TestCopilot 总览应提供测程、工具、常用 SQL、pytest 与作业入口

  Scenario: 可浏览常用 SQL 索引
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 TestCopilot 的 "常用 SQL"
    Then 常用 SQL 页应展示 SQL 文件列表或产品空状态

  Scenario: 可浏览 pytest 节点
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    When 我打开 TestCopilot 的 "pytest"
    Then pytest 页应展示已收集的节点或产品空状态

  @smoke @critical
  Scenario: 引用场景创建测程后报告保持待执行
    Given 项目 "Dogfood 核心" 已将 "TestCopilot" 绑定到数据源 "Dogfood 测试仓"
    And 项目 "Dogfood 核心" 已将 "Formulation" 绑定到数据源 "Dogfood 测试仓"
    And Formulation 场景目录中存在场景 "工作项"
    When 我打开 TestCopilot 的 "测程"
    And 我创建测程:
      | 名称              | 场景  |
      | Dogfood 工作项回归 | 工作项 |
    Then 测程列表应包含 "Dogfood 工作项回归"
    And 测程 "Dogfood 工作项回归" 应引用所选场景且报告处于待执行

  @skip
  Scenario: 测程关联跑测后报告不再为空（P3 尚未把运行挂到测程）
    Given 项目 "Dogfood 核心" 中存在测程 "Dogfood 工作项回归"
    When 系统将跑测结果回填到测程 "Dogfood 工作项回归"
    Then 测程 "Dogfood 工作项回归" 的报告应包含可观测的通过或失败结果
