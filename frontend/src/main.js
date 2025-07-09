// 主入口加载dashboard
import { renderDashboard } from './components/dashboard.js';
// 如有其它组件需要import，可在此处添加

function checkLogin() {
    const token = localStorage.getItem('token');
    return !!token;
}

function handleDashboardAction(action) {
    if (!checkLogin()) {
        alert('请先登录！');
        window.location.href = 'login.html';
        return;
    }
    action();
}

function renderMain() {
    const app = document.getElementById('app');
    app.innerHTML = '';
    const dashboard = renderDashboard({
        onLogin: () => window.location.href = 'login.html',
        onLogout: () => {
            localStorage.removeItem('token');
            window.location.reload();
        },
        onAction: handleDashboardAction
    });
    app.appendChild(dashboard);
}

renderMain();
