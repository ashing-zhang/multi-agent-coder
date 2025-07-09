// 主动登出组件
function renderLogout(onLogout) {
    const btn = document.createElement('button');
    btn.className = 'logout-btn';
    btn.textContent = '退出登录';
    btn.onclick = () => {
        localStorage.removeItem('token');
        alert('您已退出登录。');
        if (typeof onLogout === 'function') onLogout();
        window.location.reload();
    };
    return btn;
}

window.renderLogout = renderLogout; 