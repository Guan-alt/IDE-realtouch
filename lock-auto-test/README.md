# 智能门锁插件自动化测试框架

基于 Appium + 串口通信的端到端自动化测试框架，覆盖 UI 界面验证与指令下发验证两大核心场景，支持自研 App 与米家 App 双端测试。

## 项目结构

```
lock-auto-test/
├── tests/                      # 测试用例
│   ├── self_app/               # 自研App测试用例
│   ├── mijia_app/              # 米家App测试用例
│   ├── test_serial_smoke.py    # 串口冒烟测试
│   └── conftest.py             # pytest fixture 配置
├── pages/                      # 页面对象 (PO)
│   ├── base/                   # 接口抽象
│   │   └── lock_app_interface.py   # 门锁操作统一接口
│   ├── self_app/               # 自研App页面
│   │   ├── base_page.py
│   │   ├── home_page.py
│   │   └── lock_detail_page.py
│   └── mijia_app/              # 米家App页面
│       ├── base_page.py
│       ├── home_page.py
│       └── lock_plugin_page.py
├── drivers/                    # 驱动封装
│   ├── appium_driver.py        # Appium Driver
│   └── serial_driver.py        # 串口 Driver
├── lock_controller/            # 门锁控制器
│   ├── lock_serial.py          # 串口控制器（核心）
│   └── log_parser.py           # 日志解析器
├── common/                     # 公共工具
│   ├── config.py               # 配置管理
│   ├── logger.py               # 日志工具
│   └── utils.py                # 通用函数
├── config/                     # 配置文件
│   ├── config.yaml             # 主配置
│   └── devices.yaml            # 设备配置
├── reports/                    # 测试报告输出目录
├── pytest.ini                  # pytest 配置
├── requirements.txt            # 依赖清单
└── README.md                   # 项目说明
```

## 环境准备

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Appium

```bash
# 需要先安装 Node.js
npm install -g appium
npm install -g appium-uiautomator2-driver
```

### 3. 安装 Android SDK

配置 `ANDROID_HOME` 环境变量，确保 `adb` 命令可用。

### 4. 串口驱动

安装 USB 转串口驱动（如 CH340、PL2303 等），确保设备管理器中能看到 COM 口。

## 快速开始

### 第一步：配置修改

编辑 `config/config.yaml`：

- 修改 `android.device_name` 为你的测试手机序列号（`adb devices` 查看）
- 修改 `self_app` 的 `app_package` 和 `app_activity`
- 修改 `serial.port` 为实际的串口号
- 修改 `test_lock_name` 为你的测试门锁名称

编辑 `config/devices.yaml` 配置测试设备信息。

### 第二步：验证串口通信

```bash
# 先跑串口冒烟测试，确认串口能正常读取日志
pytest tests/test_serial_smoke.py --serial-only -v
```

### 第三步：启动 Appium 服务

```bash
appium
```

### 第四步：运行测试

```bash
# 运行自研App全部测试
pytest tests/self_app/ -v

# 运行米家App全部测试
pytest tests/mijia_app/ --app=mijia_app -v

# 只跑冒烟用例
pytest -m smoke -v

# 生成 HTML 报告
pytest tests/self_app/ --html=reports/report.html --self-contained-html
```

## 核心能力

### 1. UI 界面验证

- 页面元素存在性校验
- 状态文案正确性校验
- 按钮/入口可见性校验

### 2. 指令下发验证（端到端）

- App 操作后通过串口日志验证指令到达
- 验证门锁执行结果
- 验证 App UI 状态同步更新

### 3. 门锁串口控制器

- 日志捕获与关键字匹配
- 状态查询
- 环境准备（确保门锁处于预期状态）
- 调试指令发送

## 测试用例列表（一期）

| 编号 | 用例名称 | 场景 | 优先级 |
|------|---------|------|--------|
| TC-001 | 门锁详情页UI元素校验 | UI验证 | P0 |
| TC-002 | 远程开锁端到端验证 | UI + 指令下发 | P0 |
| TC-003 | 远程关锁端到端验证 | UI + 指令下发 | P0 |
| TC-004 | 添加临时密码 | UI + 指令下发 | P1 |
| TC-005 | 删除临时密码 | UI + 指令下发 | P1 |
| TC-006 | 门锁状态查询与展示 | UI + 指令下发 | P1 |

## 扩展自定义

### 添加新的页面

1. 在 `pages/self_app/` 下新建页面类，继承 `BasePage`
2. 定义元素定位器和操作方法
3. 在测试用例中引用

### 添加新的测试用例

1. 在 `tests/self_app/` 下新建测试文件
2. 使用 pytest 风格编写测试函数
3. 使用 `app_driver` 和 `lock_serial` fixture

### 适配自定义日志格式

修改 `lock_controller/log_parser.py` 中的正则表达式，匹配你们的日志格式。

修改 `lock_controller/lock_serial.py` 中的 `LOG_KEY_*` 常量，匹配你们固件的日志关键字。

## 注意事项

1. **元素定位**：代码中的元素 ID 都是占位符，请用 Appium Inspector 实际探查后替换
2. **日志关键字**：串口日志的关键字需要根据你们固件的实际日志格式调整
3. **米家App**：米家相关页面为骨架代码，需要实际探查后完善元素定位
4. **串口指令**：通过串口发送调试指令的功能需要固件支持相应的 AT 指令或调试接口

## 后续计划

- [ ] 场景三：门锁事件上报验证
- [ ] 集成 MitmProxy 抓包能力
- [ ] iOS 端支持
- [ ] CI/CD 集成
- [ ] 性能测试扩展
