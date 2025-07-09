// 登录表单组件
function renderLogin(onLogin) {
    const form = document.createElement('form');
    form.className = 'login-form';
    form.innerHTML = `
        <h2>登录</h2>
        <input name="username" placeholder="用户名" required class="login-input" />
        <input name="password" type="password" placeholder="密码" required class="login-input" />
        <button type="submit" class="login-btn">登录</button>
        <div class="register-link-container"><a href="register.html" class="register-link">没有账号？注册</a></div>
    `;
    form.onsubmit = async (e) => {
        e.preventDefault();
        const username = form.username.value;
        const password = form.password.value;
        // 调用后端API
        const res = await fetch('/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            onLogin && onLogin();
        } else {
            alert('登录失败');
        }
    };
    return form;
}

window.renderLogin = renderLogin;

// ===== 自动登出相关 =====
const AUTO_LOGOUT_MINUTES = 30; // 非活跃30分钟自动登出
let logoutTimer = null;

function resetLogoutTimer(onLogout) {
    if (logoutTimer) clearTimeout(logoutTimer);
    logoutTimer = setTimeout(() => {
        localStorage.removeItem('token');
        alert('您已长时间未操作，已自动登出。');
        if (typeof onLogout === 'function') onLogout();
        window.location.reload(); // 可选：刷新页面
    }, AUTO_LOGOUT_MINUTES * 60 * 1000);
}

function setupAutoLogout(onLogout) {
    ['mousemove', 'keydown', 'mousedown', 'touchstart'].forEach(event => {
        window.addEventListener(event, () => resetLogoutTimer(onLogout));
    });
    resetLogoutTimer(onLogout);
}
