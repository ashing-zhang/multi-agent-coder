// 登录表单组件
function renderLogin(onLogin) {
    const form = document.createElement('form');
    form.className = 'login-form';
    form.innerHTML = `
        <h2>登录</h2>
        <input name="username" placeholder="用户名" required style="width:100%;margin-bottom:12px;padding:8px;" />
        <input name="password" type="password" placeholder="密码" required style="width:100%;margin-bottom:12px;padding:8px;" />
        <button type="submit" style="width:100%;padding:10px;">登录</button>
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
