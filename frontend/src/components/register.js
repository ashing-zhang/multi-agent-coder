function renderRegister() {
    const form = document.createElement('form');
    form.className = 'register-form';
    form.innerHTML = `
        <h2>注册新用户</h2>
        <input name="username" placeholder="用户名" required class="login-input" />
        <input name="email" type="email" placeholder="邮箱" required class="login-input" />
        <input name="password" type="password" placeholder="密码" required class="login-input" />
        <input name="confirm" type="password" placeholder="确认密码" required class="login-input" />
        <button type="submit" class="login-btn">注册</button>
        <a href="index.html" class="register-cancel-btn">返回登录</a>
    `;
    form.onsubmit = async (e) => {
        e.preventDefault();
        const username = form.username.value.trim();
        const email = form.email.value.trim();
        const password = form.password.value;
        const confirm = form.confirm.value;
        if (password !== confirm) {
            alert('两次输入的密码不一致');
            return;
        }
        const res = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        if (res.ok) {
            alert('注册成功，请登录！');
            window.location.href = 'index.html';
        } else {
            const err = await res.json().catch(() => ({}));
            alert('注册失败：' + (err.detail || '请检查输入'));
        }
    };
    return form;
}

document.getElementById('register-app').appendChild(renderRegister()); 