# hoshino_shadowverse
Hoshinobot 影之诗模块

[TOC]

## 使用

克隆项目到 `HoshinoBot/hoshino/modules/` ，在 `HoshinoBot/hoshino/config/__bot__.py` 的 `MODULES_ON` 中加入 `hoshino_shadowverse` 。

安装依赖

``` python
pip install -r requirements.txt
```

## 功能

### 查询

查看帮助： `帮助sv查询`

#### 查卡器

群聊中输入 `sv查卡 关键词1 [关键词2] [关键词3] ...` 即可查询相关卡牌。

### 娱乐

查看帮助： `帮助sv娱乐`

#### 猜卡牌

群聊中输入 `sv猜卡牌 [关键词1] [关键词2] [关键词3] ...` 进行猜卡牌游戏，可选关键词进行筛选，名称中标点符号作通配处理。

#### 猜语音

可能需要安装 `ffmpeg` 。

群聊中输入 `sv猜语音 [关键词1] [关键词2] [关键词3] ...` 进行猜语音游戏，可选关键词进行筛选，名称中标点符号作通配处理。（目前只支持英文与日文数据库源）
