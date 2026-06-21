# 红宝书词典 - 单词搜索

一个支持模糊搜索和拼写纠错的单词查询工具，可快速定位任意单词在红宝书中的页码。

## 功能特性

- **精确匹配** — 输入完整单词直接定位页码
- **前缀匹配** — 输入 `aberr` 可找到所有以 `aberr` 开头的单词
- **包含匹配** — 输入 `ment` 可找到所有包含 `ment` 的单词
- **拼写纠错** — 使用编辑距离算法智能修正输入错误
- **网络释义** — 词库中未收录的单词自动调用有道词典查询释义
- **关键词高亮** — 搜索结果中突出显示匹配部分
- **卡片式展示** — 搜索结果按匹配类型分组，清晰明了

## 目录结构

```
红宝书词典/
├── run.bat          ← 一键启动 (Windows)
├── app.py           ← Flask 后端服务
├── index.html       ← 前端页面
├── data.txt         ← 单词数据源 (5,266 条)
├── words.db         ← SQLite 数据库 (已填充，首次运行可自动生成)
├── import_data.py   ← 数据导入脚本
├── requirements.txt ← 依赖声明
└── README.md        ← 本说明文档
```

## 快速开始（Windows）

### 方式一：一键启动（推荐）

双击 `run.bat` 即可。脚本会自动：
1. 检查 Python 是否安装
2. 检查并安装 Flask 依赖
3. 检查数据库是否存在，若不存在则自动导入 data.txt
4. 启动服务并自动打开浏览器访问 http://localhost:5000

### 方式二：命令行启动

```bash
pip install -r requirements.txt
python app.py
```

然后手动打开浏览器访问 http://localhost:5000

## 使用方法

1. 在搜索框中输入单词（例如 `abandon`）
2. 输入时自动搜索，结果分为四组：
   - **✓ 精确匹配** — 与输入完全一致的单词
   - **→ 前缀匹配** — 以输入内容开头的单词
   - **≋ 包含匹配** — 包含输入内容的单词
   - **~ 拼写相近** — 可能输入有误的相近单词
3. 每张卡片右侧显示该单词在红宝书中的页码
4. 词库未收录的单词会显示有道词典的网络释义

## 搜索示例

| 输入 | 效果 |
|------|------|
| `abandon` | 精确匹配，显示该单词及页码 |
| `aberr` | 前缀匹配，显示所有以 aberr 开头的单词 |
| `ment` | 包含匹配，显示含 ment 的所有单词 |
| `abendon` | 拼写纠错，推荐 abandon 等相近词 |
| `serendipity` | 词库未收录，显示有道词典释义 |

## 自定义词库

如需修改或扩展词库：

1. 编辑 `data.txt`，格式为每行一个单词：`单词,页码`
   - 以 `#` 开头的行为注释
   - 示例：`abandon,24`
2. 删除旧的 `words.db`
3. 重新运行 `run.bat`，会自动导入新数据

或者手动导入：

```bash
python import_data.py import data.txt
```

## 环境要求

- **Python 3.8 或更高版本**（Win10/11 自带 Python 安装器）
- 无需额外安装数据库，使用 SQLite 内置数据库
- 浏览器支持：Chrome / Edge / Firefox 现代版本

## 常见问题

**Q: 运行 run.bat 提示找不到 Python？**
A: 请先安装 Python，下载地址 https://www.python.org/downloads/
   安装时请勾选「Add Python to PATH」选项。

**Q: 首次启动较慢？**
A: 首次运行时需要下载 Flask 依赖包，大约 1-2 分钟，后续启动瞬间启动。

**Q: 端口 5000 被占用怎么办？**
A: 关闭其他占用 5000 端口的程序，或修改 `app.py` 最后一行中的端口号。

**Q: 想更新数据库？**
A: 删除 `words.db` 文件后重新运行 `run.bat` 即可。

**Q: 如何停止服务？**
A: 在运行窗口按 `Ctrl+C`，或直接关闭窗口。

## 手机端 App（Android）

如需在手机上使用，请查看 `android_app/` 文件夹：

```
android_app/
├── app/src/main/java/com/redbook/dictionary/
│   ├── MainActivity.java       ← 启动画面，检测服务器
│   └── LocalServerActivity.java ← WebView 加载词典网页
├── app/src/main/res/layout/
│   ├── activity_main.xml       ← 启动画面布局
│   └── activity_local_server.xml ← WebView 页面布局
├── build.gradle
├── settings.gradle
└── 构建说明.md
```

### 构建 APK 步骤

1. 在 Android Studio 中打开 `android_app` 文件夹
2. 等待 Gradle 同步完成
3. Build → Build APK(s)
4. APK 生成后安装到手机

### 手机连接电脑

1. 电脑和手机连接同一 WiFi
2. 电脑端运行 `run.bat`，记下显示的局域网 IP（如 `192.168.1.100`）
3. 修改 `LocalServerActivity.java` 中的 `LOCAL_URL` 为 `http://192.168.1.100:5000`
4. 重新构建 APK 安装到手机

详细说明请参阅 `android_app/构建说明.md`

## 技术栈

- **后端**: Python + Flask
- **数据库**: SQLite
- **前端**: HTML + CSS + 原生 JavaScript
- **拼写纠错**: Levenshtein 编辑距离算法
- **网络释义**: 有道词典开放 API
- **Android**: Java + WebView + Material Design
