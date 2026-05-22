# 企业微信天气推送 · 部署指南

每天北京时间 **7:00** 自动将遵化市天气推送到普通微信。

---

## 一、企业微信配置

### 1. 开启微信消息互通（让消息到普通微信）

登录 [企业微信管理后台](https://work.weixin.qq.com) → 左侧菜单「我的企业」→「微信插件」→ 开启并保存。

生成二维码后，用普通微信扫码关注。之后消息会直接到达微信。

### 2. 配置应用可信 IP

「应用管理」→ 你的应用（AgentID: 1000002）→「企业可信IP」→ 清空或设为不限制。

> 因为 GitHub Actions 的出口 IP 不固定，建议不限制 IP。

### 3. 指定接收人（可选）

如果要发给特定成员而非全体：

- 在「通讯录」中查看成员的 **UserID**
- 在 GitHub Secrets 中添加 `WECOM_TO_USERS`，值用 `|` 分隔，如 `ZhangSan|LiSi`
- 如果不设，默认发给应用可见范围内所有人（`@all`）

### 4. ⚠️ 重置 Secret（安全）

因为 Secret 之前已在对话中暴露，请立即去后台重新生成：

「应用管理」→ 你的应用 → 点击 Secret 旁边的刷新 → 确认 → 拿到新 Secret。

---

## 二、部署到 GitHub

### 1. 创建仓库

在 GitHub 新建一个私有仓库，把本项目文件上传：

```
your-repo/
├── send_weather.py
└── .github/
    └── workflows/
        └── weather.yml
```

### 2. 设置 Secrets

仓库 → Settings → Secrets and variables → Actions → New repository secret：

| Name | 值 |
|------|-----|
| `WECOM_CORPID` | ww59c31db7973b6a37 |
| `WECOM_SECRET` | （重新生成后的新 Secret） |
| `WECOM_AGENTID` | 1000002 |

### 3. 手动触发测试

Actions → 天气推送 → Run workflow → 确认。首次运行后可检查微信是否收到消息。

---

## 三、完成

之后无需任何操作，每天 7:00 GitHub 会自动执行，你的微信里准时收到天气推送。