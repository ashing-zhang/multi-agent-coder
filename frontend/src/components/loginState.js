import { getToken, validateToken, setLoginState } from './auth.js';

// 检查并设置登录状态，供 dashboard.js 调用
export async function checkAndSetLoginState(container, props = {}) {
    const token = getToken();
    if (token) {
        // 验证token有效性
        try {
            const valid = await validateToken(token);
            if (valid) {
                setLoginState(container, true);
                // 已经是有效token，无需重复调用 onLogin 回调
            } else {
                localStorage.removeItem('token');
                setLoginState(container, false);
            }
        } catch (e) {
            console.error('Token validation error:', e);
            localStorage.removeItem('token');
            setLoginState(container, false);
        }
    } else {
        setLoginState(container, false);
    }
} 