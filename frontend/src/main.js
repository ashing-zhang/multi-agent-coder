// 主入口加载dashboard
import { renderDashboard, renderDashboardAuthbar } from './components/dashboard.js';
// 如有其它组件需要import，可在此处添加

async function renderMain() {
    const authbarContainer = document.getElementById('dashboard-authbar-container');
    const dashboardRoot = document.getElementById('dashboard-root');
    if (!authbarContainer || !dashboardRoot) {
        console.error('Authbar or dashboard root container not found!');
        return;
    }
    dashboardRoot.innerHTML = '';
    authbarContainer.innerHTML = '';

    // 渲染dashboard主体，并传入onAuthbar回调
    const dashboard = renderDashboard({
        onLogin: () => window.location.href = 'index.html',
        onLogout: () => {
            localStorage.removeItem('token');
            window.location.reload();
        },
        onAction: action => action(),
        onAuthbar: (userinfo, apiKeyBtnHtml, isLoggedIn, props) => {
            authbarContainer.innerHTML = '';
            const authbar = renderDashboardAuthbar(userinfo, apiKeyBtnHtml, isLoggedIn, props);
            authbarContainer.appendChild(authbar);
        }
    });
    dashboardRoot.appendChild(dashboard);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderMain);
} else {
    renderMain();
} 