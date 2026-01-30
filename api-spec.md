# Todo List API 约定草案（v0.1）

> 目标：支持前端先行开发与 Mock，后端落地 FastAPI + MySQL。
> 范围：待办、分类、统计、用户/登录、回收站。

## 1. 通用约定

### 1.0 接口风格
- 采用 REST 风格：资源名使用名词复数、HTTP 方法表达动作、路径层级表达资源关系

### 1.1 基础
- Base URL：`/api/v1`
- 数据格式：`application/json; charset=utf-8`
- 时间格式：ISO 8601（UTC 推荐），示例：`2026-01-29T08:30:00Z`
- 分页：`page`（从 1 开始）、`page_size`（默认 20，最大 100）

### 1.2 统一响应
**成功响应**
```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

**分页响应**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [],
    "page": 1,
    "page_size": 20,
    "total": 0
  }
}
```

**错误响应**
```json
{
  "code": 40001,
  "message": "validation_error",
  "data": {
    "field": "title",
    "detail": "required"
  }
}
```

### 1.3 统一错误码（示例）
- `40001` 参数错误/校验失败
- `40101` 未登录/Token 失效
- `40301` 权限不足
- `40401` 资源不存在
- `40901` 状态冲突（如重复名称）
- `50000` 服务器错误

### 1.4 鉴权
- 登录后返回 `access_token`（JWT）
- 请求头：`Authorization: Bearer <token>`

---

## 2. 数据模型（核心字段）

### 2.1 User
- `id` (string)
- `username` (string)
- `email` (string, optional)
- `avatar_url` (string, optional)
- `created_at` (string)
- `updated_at` (string)

### 2.2 Category（分类）
- `id` (string)
- `name` (string)
- `color` (string, hex)
- `order` (number)
- `is_system` (boolean)  // 快捷分类可标记
- `created_at` (string)
- `updated_at` (string)

### 2.3 TodoItem（待办）
- `id` (string)
- `title` (string)
- `description` (string, optional)
- `priority` (enum: `high` | `medium` | `low`)
- `status` (enum: `todo` | `done`)
- `due_date` (string, optional)  // 截止日期
- `remind_at` (string, optional) // 提醒时间
- `category_id` (string, optional)
- `tags` (string[], optional)
- `is_deleted` (boolean) // 回收站
- `deleted_at` (string, optional)
- `created_at` (string)
- `updated_at` (string)
- `completed_at` (string, optional)

---

## 3. 用户与登录

### 3.1 注册
`POST /auth/register`

**Body**
```json
{
  "username": "tom",
  "password": "123456",
  "email": "tom@example.com"
}
```

**Response**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "u_001",
    "username": "tom"
  }
}
```

### 3.2 登录
`POST /auth/login`

**Body**
```json
{
  "username": "tom",
  "password": "123456"
}
```

**Response**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "xxx.yyy.zzz",
    "expires_in": 86400,
    "user": {
      "id": "u_001",
      "username": "tom",
      "avatar_url": ""
    }
  }
}
```

### 3.3 当前用户信息
`GET /users/me`

---

## 4. 分类（Category）

### 4.1 获取分类列表
`GET /categories`

### 4.2 新增分类
`POST /categories`

**Body**
```json
{
  "name": "我的工作",
  "color": "#4A90E2",
  "order": 1
}
```

### 4.3 更新分类
`PUT /categories/{id}`

**Body**
```json
{
  "name": "生活琐事",
  "color": "#7ED321",
  "order": 2
}
```

### 4.4 删除分类
`DELETE /categories/{id}`

> 删除策略：可设置为“强制删除”或“转移至未分类”，由后端策略决定。

---

## 5. 待办（Todo）

### 5.1 获取待办列表
`GET /todos`

**Query Params**
- `status`：`todo` | `done`
- `category_id`
- `priority`：`high` | `medium` | `low`
- `keyword`：标题/标签模糊搜索
- `due`：`today` | `week` | `overdue` | `none`
- `sort_by`：`created_at` | `due_date` | `priority`
- `sort_order`：`asc` | `desc`
- `include_deleted`：`true` | `false`（默认 `false`）
- `page` / `page_size`

### 5.2 新增待办
`POST /todos`

**Body**
```json
{
  "title": "完成设计稿",
  "description": "完成 Todo 列表页面",
  "priority": "high",
  "status": "todo",
  "due_date": "2026-01-31",
  "remind_at": "2026-01-30T09:00:00Z",
  "category_id": "c_001",
  "tags": ["设计", "UI"]
}
```

### 5.3 更新待办
`PUT /todos/{id}`

**Body**
```json
{
  "title": "完成交互稿",
  "priority": "medium",
  "status": "done",
  "completed_at": "2026-01-29T12:00:00Z"
}
```

### 5.4 删除待办（软删除）
`DELETE /todos/{id}`

> 默认软删除，进入回收站（`is_deleted = true`）。

### 5.5 批量更新状态
`PATCH /todos/batch/status`

**Body**
```json
{
  "ids": ["t_001", "t_002"],
  "status": "done"
}
```

### 5.6 清空已完成
`DELETE /todos/clear-done`

> 可只清空“已完成且未删除”的记录。

---

## 6. 回收站（Trash）

### 6.1 获取回收站列表
`GET /trash`

**Query Params**
- `page` / `page_size`

### 6.2 还原待办
`POST /trash/{id}/restore`

### 6.3 永久删除
`DELETE /trash/{id}/purge`

### 6.4 清空回收站
`DELETE /trash/clear`

---

## 7. 统计

### 7.1 基础统计
`GET /stats/summary`

**Response**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "total_todos": 120,
    "today_completed": 5,
    "week_completion_rate": 0.78
  }
}
```

### 7.2 分类统计（可选）
`GET /stats/categories`

---

## 8. 备注与建议
- 前端 Mock 可优先实现：`/todos` 列表 + 过滤/排序 + 新增/编辑 + 回收站
- 后端落地建议加唯一性约束：同用户分类名称不可重复
- `priority` 可映射 UI 的颜色：
  - `high`：橙红
  - `medium`：橙
  - `low`：绿
