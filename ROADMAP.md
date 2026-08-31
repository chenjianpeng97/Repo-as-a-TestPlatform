# ROADMAP


- [ ] packages/包，apps/公共工具包，工程化，独立打包上传pip
- [x] page_test运行库设计,模拟apitest设计思路，定义pageobject基类，独立运行的page等
      （`packages/page_test`：PageModel 元素表 + 声明式 flow、多定位器备用、locator_policy
      确定性拦截、doctor 体检、BasePage 逃生舱、CLI 与单文件回放。
      `apps/page_recorder` 手点冻结已落地。后续：`Pages` 容器接入 behave `context.pages`）
- [ ] api_mocker运行库扩展，mockserver
- [ ] fake_data packages/公共包开发
- [ ] pytest联动pageobject和apiobjects进行 health check
- [ ] 日志分析skill
- [ ] 