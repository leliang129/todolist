import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App as AntdApp, ConfigProvider } from 'antd'
import 'antd/dist/reset.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#4A90E2',
          borderRadius: 10,
          fontFamily: '"Karla", "Noto Sans", sans-serif',
          colorText: '#1C2A3A',
          colorBgLayout: 'transparent',
        },
      }}
    >
      <AntdApp>
        <App />
      </AntdApp>
    </ConfigProvider>
  </StrictMode>,
)
