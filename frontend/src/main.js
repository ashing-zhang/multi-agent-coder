// 主入口加载dashboard
import { renderDashboard } from './components/dashboard.js';
// 如有其它组件需要import，可在此处添加

async function renderMain() {
    renderDashboard({
        onLogin: async () => {
            window.location.href = 'index.html';
        },
        onLogout: async () => {
            localStorage.removeItem('token');
            window.location.reload();
        }
    });
}    

// 确保 renderMain 函数在 DOM 树构建完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderMain);
} else {
    renderMain();
} 