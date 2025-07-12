// 认证相关工具函数

// 获取本地 token
export function getToken() {
    return localStorage.getItem('token');
}

// 校验 token 是否有效，返回 Promise<boolean>
export async function validateToken(token) {
    try {
        // 发送 GET 请求到 /auth/validate_token，携带 Authorization 头部（格式为 Bearer token），用于校验 token 是否有效
        const res = await fetch('/auth/validate_token', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        // res.ok 是 fetch API 返回的 Response 对象的一个属性，表示 HTTP 响应状态码是否在 200-299 之间（即请求是否成功）
        // 它与接口返回的数据内容无关，仅反映 HTTP 层面的成功与否
        return res.ok;
    } catch {
        return false;
    }
}

/*
    通过切换按钮和状态提示的显示/隐藏，让用户界面始终与实际登录状态保持一致，
    提升用户体验和安全性（UI 显示/隐藏）。
*/
export function setLoginState(container, loggedIn) {
    const loginBtn = container.querySelector('#dashboard-login');
    const logoutBtn = container.querySelector('#dashboard-logout');
    const loginStatus = container.querySelector('.login-status');
    if (loggedIn) {
        loginBtn.style.display = 'none';
        logoutBtn.style.display = '';
        loginStatus.style.display = '';
    } else {
        loginBtn.style.display = '';
        logoutBtn.style.display = 'none';
        loginStatus.style.display = 'none';
    }
} 