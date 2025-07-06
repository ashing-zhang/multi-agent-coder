// 前端主入口
async function main() {
    const app = document.getElementById('app');
    const token = localStorage.getItem('token');
    if (!token) {
        app.appendChild(window.renderLogin(() => location.reload()));
        return;
    }
    // 获取用户信息
    const res = await fetch('/user/profile', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    if (res.ok) {
        const user = await res.json();
        app.appendChild(window.renderDashboard(user));
    } else {
        localStorage.removeItem('token');
        location.reload();
    }
}

main();
