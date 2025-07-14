// 主入口加载dashboard
import { renderDashboard } from './components/dashboard.js';
// 如有其它组件需要import，可在此处添加

async function renderMain() {
    const { main, authbar, history } = renderDashboard({
        onLogin: async () => {
            window.location.href = 'index.html';
        },
        onLogout: async () => {
            localStorage.removeItem('token');
            window.location.reload();
        }
    });
    // 插入到页面指定容器
    document.getElementById('dashboard-root').appendChild(main);
    document.getElementById('dashboard-authbar-container').appendChild(authbar);
    // history（左上角历史按钮）如果有内容，可以插入到 body 或 dashboard-root 前
    if (history && history.innerHTML.trim()) {
        document.body.insertBefore(history, document.getElementById('dashboard-root'));
    }
}    

// 确保 renderMain 函数在 DOM 树构建完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderMain);
} else {
    renderMain();
} 