import { useEffect, useMemo, useState } from 'react'
import {
  App as AntdApp,
  Badge,
  Button,
  DatePicker,
  Dropdown,
  Form,
  Input,
  Modal,
  Select,
  Tooltip,
} from 'antd'
import {
  CheckOutlined,
  DeleteOutlined,
  EditOutlined,
  FilterOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PlusOutlined,
  SearchOutlined,
  SortAscendingOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { ensureAuth } from './api/auth'
import { del, get, post, put } from './api/client'
import './App.css'

const priorityMeta = {
  high: { label: '高', color: '#F29D4B' },
  medium: { label: '中', color: '#F5A623' },
  low: { label: '低', color: '#26B36A' },
}

const dueMeta = {
  soon: { label: '快到期', color: '#F29D4B' },
  overdue: { label: '已过期', color: '#F25D5D' },
}

const filterItems = [
  { key: 'all', label: '全部' },
  { key: 'done', label: '已完成' },
  { key: 'todo', label: '未完成' },
  { key: 'today', label: '今日待办' },
  { key: 'soon', label: '快到期' },
  { key: 'high', label: '高优先级' },
  { key: 'medium', label: '中优先级' },
  { key: 'low', label: '低优先级' },
]

const sortItems = [
  { key: 'created_at', label: '按创建时间' },
  { key: 'due_date', label: '按截止日期' },
  { key: 'priority', label: '按优先级' },
]

function App() {
  const { message: messageApi } = AntdApp.useApp()
  const [collapsed, setCollapsed] = useState(false)
  const [searchValue, setSearchValue] = useState('')
  const [todos, setTodos] = useState([])
  const [overviewTodos, setOverviewTodos] = useState([])
  const [categories, setCategories] = useState([])
  const [stats, setStats] = useState({ total_todos: 0, today_completed: 0, week_completion_rate: 0 })
  const [filterKey, setFilterKey] = useState('all')
  const [sortKey, setSortKey] = useState('created_at')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [ready, setReady] = useState(false)
  const [form] = Form.useForm()

  const categoryMap = useMemo(() => {
    const map = new Map()
    categories.forEach((item) => map.set(item.id, item))
    return map
  }, [categories])

  const allDone = todos.length > 0 && todos.every((item) => item.status === 'done')
  const showList = todos.length > 0

  const quickCategories = useMemo(() => {
    const todayStr = dayjs().format('YYYY-MM-DD')
    const soonCutoff = dayjs().add(2, 'day')
    const todayCount = overviewTodos.filter((t) => t.status === 'todo' && t.due_date === todayStr).length
    const soonCount = overviewTodos.filter(
      (t) =>
        t.status === 'todo' &&
        t.due_date &&
        dayjs(t.due_date).isAfter(dayjs().subtract(1, 'day')) &&
        dayjs(t.due_date).isBefore(soonCutoff.add(1, 'day')),
    ).length
    return [
      { key: 'all', label: '全部待办', count: overviewTodos.length },
      { key: 'todo', label: '待完成', count: overviewTodos.filter((t) => t.status === 'todo').length },
      { key: 'done', label: '已完成', count: overviewTodos.filter((t) => t.status === 'done').length },
      { key: 'today', label: '今日待办', count: todayCount },
      { key: 'soon', label: '快到期', count: soonCount },
    ]
  }, [overviewTodos])

  const loadTodos = async () => {
    const params = {
      page: 1,
      page_size: 50,
      sort_by: sortKey,
      sort_order: 'desc',
    }
    const keyword = searchValue.trim()
    if (keyword) params.keyword = keyword
    if (filterKey === 'done' || filterKey === 'todo') params.status = filterKey
    if (filterKey === 'high' || filterKey === 'medium' || filterKey === 'low') params.priority = filterKey
    if (filterKey === 'today') {
      params.due = 'today'
      params.status = 'todo'
    }
    if (filterKey === 'soon') {
      params.due = 'week'
      params.status = 'todo'
    }
    const data = await get('/todos', params)
    setTodos(data.items || [])
  }

  const loadOverview = async () => {
    const data = await get('/todos', { page: 1, page_size: 100, sort_by: 'created_at', sort_order: 'desc' })
    setOverviewTodos(data.items || [])
  }

  const loadCategories = async () => {
    const data = await get('/categories')
    setCategories(data || [])
  }

  const loadStats = async () => {
    const data = await get('/stats/summary')
    setStats(data || { total_todos: 0, today_completed: 0, week_completion_rate: 0 })
  }

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await ensureAuth()
        await Promise.all([loadCategories(), loadStats(), loadOverview()])
        await loadTodos()
        setReady(true)
      } catch (err) {
        messageApi.error('后端连接失败，请确认服务已启动')
      }
    }
    bootstrap()
  }, [])

  useEffect(() => {
    if (!ready) return
    const handler = setTimeout(() => {
      Promise.all([loadTodos(), loadOverview()]).catch(() => {})
    }, 300)
    return () => clearTimeout(handler)
  }, [ready, searchValue, filterKey, sortKey])

  const getDueState = (dateStr) => {
    if (!dateStr) return null
    const target = dayjs(dateStr)
    if (target.isBefore(dayjs(), 'day')) return 'overdue'
    if (target.diff(dayjs(), 'day') <= 2) return 'soon'
    return null
  }

  const handleToggle = async (item) => {
    const next = item.status === 'done' ? 'todo' : 'done'
    await put(`/todos/${item.id}`, { status: next })
    await Promise.all([loadTodos(), loadStats(), loadOverview()])
  }

  const handleDelete = async (item) => {
    await del(`/todos/${item.id}`)
    await Promise.all([loadTodos(), loadStats(), loadOverview()])
  }

  const handleClearDone = async () => {
    await del('/todos/clear-done')
    await Promise.all([loadTodos(), loadStats(), loadOverview()])
  }

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const openEdit = (item) => {
    setEditing(item)
    form.setFieldsValue({
      title: item.title,
      description: item.description,
      priority: item.priority,
      due_date: item.due_date ? dayjs(item.due_date) : null,
      category_id: item.category_id || undefined,
    })
    setModalOpen(true)
  }

  const submitForm = async () => {
    const values = await form.validateFields()
    const payload = {
      ...values,
      due_date: values.due_date ? values.due_date.format('YYYY-MM-DD') : null,
    }
    if (editing) {
      await put(`/todos/${editing.id}`, payload)
    } else {
      await post('/todos', payload)
    }
    setModalOpen(false)
    await Promise.all([loadTodos(), loadStats(), loadOverview()])
  }

  const renderTodoItem = (item) => {
    const priority = priorityMeta[item.priority]
    const dueState = getDueState(item.due_date)
    const due = dueState ? dueMeta[dueState] : null
    const done = item.status === 'done'
    const category = item.category_id ? categoryMap.get(item.category_id) : null
    return (
      <div className={`todo-item ${done ? 'done' : ''}`} key={item.id}>
        <button type="button" className={`check-btn ${done ? 'checked' : ''}`} onClick={() => handleToggle(item)}>
          {done && <CheckOutlined />}
        </button>
        <div className="todo-main">
          <div className="todo-title">{item.title}</div>
          <div className="todo-meta">
            <span className="meta-pill" style={{ color: priority.color }}>
              <span className="dot" style={{ background: priority.color }} />
              {priority.label}
            </span>
            {item.due_date && (
              <span
                className={`meta-pill ${due ? 'alert' : ''}`}
                style={{ color: due ? due.color : '#6B778C' }}
              >
                {due ? due.label : '截止日期'} / {item.due_date}
              </span>
            )}
            {category && (
              <span className="meta-pill" style={{ color: category.color }}>
                <span className="dot" style={{ background: category.color }} />
                {category.name}
              </span>
            )}
          </div>
        </div>
        <div className="todo-actions">
          <Tooltip title="编辑">
            <button type="button" className="icon-btn" onClick={() => openEdit(item)}>
              <EditOutlined />
            </button>
          </Tooltip>
          <Tooltip title="删除">
            <button type="button" className="icon-btn danger" onClick={() => handleDelete(item)}>
              <DeleteOutlined />
            </button>
          </Tooltip>
        </div>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="brand">
            <span className="logo">✓</span>
            {!collapsed && <span className="brand-text">Todo List</span>}
          </div>
          <button
            type="button"
            className="collapse-btn"
            onClick={() => setCollapsed((prev) => !prev)}
            aria-label="切换侧边栏"
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </button>
        </div>

        <div className="sidebar-body">
          <div className="sidebar-section">
            <div className="section-title">快捷分类</div>
            <div className="sidebar-list">
              {quickCategories.map((item) => (
                <button
                  type="button"
                  className={`sidebar-item ${filterKey === item.key ? 'active' : ''}`}
                  key={item.key}
                  onClick={() => setFilterKey(item.key)}
                >
                  <span className="item-label">{item.label}</span>
                  {!collapsed && (
                    <span className="count-chip">
                      {item.count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="sidebar-section">
            <div className="section-title">自定义分类</div>
            <div className="sidebar-list">
              {categories.map((item) => (
                <button type="button" className="sidebar-item" key={item.id}>
                  <span className="item-label">
                    <span className="color-dot" style={{ background: item.color }} />
                    {item.name}
                  </span>
                  {!collapsed && <span className="item-action">···</span>}
                </button>
              ))}
              <button type="button" className="sidebar-item add-category">
                <span className="item-label">+ 新增分类</span>
              </button>
            </div>
          </div>

          <div className="sidebar-section stats">
            <div className="section-title">统计概览</div>
            <div className="stat-card">
              <div className="stat-row">
                <span>待办总数</span>
                <strong>{stats.total_todos}</strong>
              </div>
              <div className="stat-row">
                <span>今日完成</span>
                <strong>{stats.today_completed}</strong>
              </div>
              <div className="stat-progress">
                <div className="progress-label">本周完成率 {Math.round(stats.week_completion_rate * 100)}%</div>
                <div className="progress-bar">
                  <span style={{ width: `${Math.round(stats.week_completion_rate * 100)}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div className="topbar-left">
            <Input
              className="search-input"
              prefix={<SearchOutlined />}
              placeholder="搜索待办（标题 / 标签）"
              value={searchValue}
              onChange={(event) => setSearchValue(event.target.value)}
              allowClear
            />
            <Button type="primary" icon={<PlusOutlined />} className="primary-btn" onClick={openCreate}>
              新增待办
            </Button>
            <Dropdown
              menu={{
                items: filterItems,
                onClick: ({ key }) => setFilterKey(key),
              }}
              trigger={['click']}
            >
              <Button icon={<FilterOutlined />} className="ghost-btn">
                筛选
              </Button>
            </Dropdown>
            <Dropdown
              menu={{
                items: sortItems,
                onClick: ({ key }) => setSortKey(key),
              }}
              trigger={['click']}
            >
              <Button icon={<SortAscendingOutlined />} className="ghost-btn">
                排序
              </Button>
            </Dropdown>
          </div>
          <button type="button" className="clear-btn" onClick={handleClearDone}>
            清空已完成
          </button>
        </header>

        <section className="list-panel">
          <div className="panel-header">
            <div>
              <h1>Todo List</h1>
              <p>专注今天，轻量管理。所有功能在当前界面完成。</p>
            </div>
            <Badge count={todos.length} showZero color="#4A90E2" />
          </div>

          <div className={`list-body ${showList ? 'has-list' : ''}`}>
            {todos.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">＋</div>
                <div className="empty-text">暂无待办，点击新增开始吧～</div>
              </div>
            )}

            {showList && (
              <div className="todo-list">
                {todos.map(renderTodoItem)}
              </div>
            )}
          </div>
        </section>
      </main>

      <Modal
        title={editing ? '编辑待办' : '新增待办'}
        open={modalOpen}
        onOk={submitForm}
        onCancel={() => setModalOpen(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form layout="vertical" form={form} initialValues={{ priority: 'medium' }}>
          <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="输入待办标题" />
          </Form.Item>
          <Form.Item name="description" label="详情">
            <Input.TextArea rows={3} placeholder="补充描述（可选）" />
          </Form.Item>
          <Form.Item name="due_date" label="截止日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="priority" label="优先级">
            <Select
              options={[
                { label: '高', value: 'high' },
                { label: '中', value: 'medium' },
                { label: '低', value: 'low' },
              ]}
            />
          </Form.Item>
          <Form.Item name="category_id" label="分类">
            <Select
              allowClear
              placeholder="选择分类（可选）"
              options={categories.map((item) => ({ label: item.name, value: item.id }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default App
