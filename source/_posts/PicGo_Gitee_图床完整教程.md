---
title: PicGo + Gitee 图床完整教程
date: 2025-08-25
tags: [PicGo, Gitee, 图床, 教程]
---

# PicGo + Gitee 图床完整教程

## 含 Typora 一键联动（Windows / macOS / Linux 通用）


<!-- more -->
> **目标**：截图 → 自动上传到 Gitee → Markdown 中直接粘贴外链

---

## 🛠️ 1. 软件准备

| 工具         | 下载地址                                        | 备注                    |
| ------------ | ----------------------------------------------- | ----------------------- |
| Node.js ≥ 14 | <https://nodejs.org>                            | PicGo 运行依赖          |
| PicGo ≥ 2.3  | <https://github.com/Molunerfinn/PicGo/releases> | 图床客户端              |
| Typora ≥ 1.0 | <https://typora.io>                             | Markdown 编辑器（可选） |

**安装顺序**：

1.  先安装 Node.js（一路 Next 即可）

2.  再安装 PicGo（Windows 选 `.exe`，macOS 选 `.dmg`，Linux 选 `.AppImage`）

---

## 📦 2. Gitee 配置（一次性设置）

### 2.1 创建图片仓库

1.  登录 Gitee → 右上角 **「+ 新建仓库」**

2.  填写仓库信息：

    - **仓库名称**：`imgbed`（可自定义）

    - **路径**：`imgbed`（与仓库名一致）

    - **可见性**：公开或私有均可（私有仓库外链需登录查看，建议公开）

    - **初始化**：勾选 **使用 README 初始化仓库**（避免空仓库错误）

3.  创建成功后记住 **仓库完整路径**：

        https://gitee.com/你的用户名/imgbed

### 2.2 生成私人令牌

1.  点击头像 → **设置 → 安全设置 → 私人令牌**

2.  **生成新令牌** → 仅勾选 `projects` 权限

3.  **复制生成的令牌**（只显示一次，请妥善保存）

---

## 🔧 3. PicGo 安装与配置

### 3.1 安装 Gitee 插件

1.  打开 PicGo → 左侧菜单选择 **插件设置**

2.  搜索 `gitee-uploader` → 点击 **安装**

3.  安装完成后 **重启 PicGo**

### 3.2 配置 Gitee 图床

进入 **图床设置 → Gitee**，填写以下信息：

| 字段        | 示例值              | 说明                  |
| ----------- | ------------------- | --------------------- |
| `repo`      | `用户名/imgbed`     | 格式：`用户名/仓库名` |
| `branch`    | `master` 或 `main`  | 查看仓库的默认分支    |
| `token`     | 刚才复制的令牌      | Gitee 私人令牌        |
| `path`      | `img/`              | 上传子目录（可选）    |
| `customUrl` | 留空                | 自建 CDN 时使用       |
| `message`   | `upload from picgo` | 提交信息（随意）      |

点击 **确定** → **设为默认图床**

---

## 🧪 4. 测试上传功能

### 上传方式：

- **拖拽上传**：直接拖拽图片到 PicGo 主界面

- **快捷键上传**：截图后按 `Ctrl+Shift+P`（可在设置中修改）

### 验证成功：

上传成功后日志显示绿色 `success`，外链自动复制到剪贴板：

```markdown
![image](https://gitee.com/用户名/imgbed/raw/master/img/20240625120001.png)
```

---

## 🖋️ 5. Typora 一键联动配置

### 5.1 Typora 设置

1.  打开 Typora → **偏好设置 → 图像**

2.  按以下配置：

| 选项       | 设置值                    |
| ---------- | ------------------------- |
| 插入图片时 | 上传图片                  |
| 上传服务   | PicGo (app)               |
| PicGo 路径 | 浏览选择 PicGo 可执行文件 |

1.  点击 **验证图片上传选项** → 出现绿色 √ 表示成功

### 5.2 使用流程

- **截图** → 在 Typora 中 `Ctrl+V` 粘贴

- → 图片自动上传到 Gitee

- → 自动替换为外链 Markdown 格式

---

## ❓ 6. 常见问题解决

| 问题现象          | 解决方案                                               |
| ----------------- | ------------------------------------------------------ |
| 上传提示 403 错误 | 重新生成令牌，确保勾选 `projects` 权限                 |
| 外链显示 404      | 检查仓库是否为公开，分支名称是否正确                   |
| macOS 权限问题    | 系统设置 → 隐私与安全 → 允许 PicGo 运行                |
| Linux 无法启动    | 安装 AppImageLauncher 或执行 `chmod +x PicGo.AppImage` |
| 上传速度慢        | 检查网络连接，或考虑使用国内 CDN 加速                  |

---

## 🚀 7. 进阶功能

### 7.1 图片压缩插件

在 PicGo 插件商店搜索安装：

- **compress**：本地压缩

- **tinypng**：使用 TinyPNG API 压缩（需要 API key）

---

## ⌨️ 8. 命令行使用（可选）

喜欢终端操作的用户可以安装 PicGo CLI：

```bash
# 全局安装 PicGo CLI
npm install picgo -g

# 配置 Gitee 上传器
picgo set uploader gitee

# 设置为默认上传器
picgo use uploader gitee

# 上传图片
picgo upload example.png
```

---

## ✅ 9. 完整工作流验证

1.  **截图**或选择本地图片

2.  **粘贴**到 Typora 或拖拽到 PicGo

3.  **自动上传**到 Gitee 仓库

4.  **自动生成** Markdown 外链

5.  **确认图片**在网页中正常显示

---
