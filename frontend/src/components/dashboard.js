// 仪表盘组件（展示用户信息和Agent协作流程）
function renderDashboard(user) {
    const dash = document.createElement('div');
    dash.className = 'dashboard';
    dash.innerHTML = `<h3>欢迎，${user.username}（${user.role}）</h3>`;
    dash.appendChild(window.renderAgents());
    dash.appendChild(window.renderWorkflow());
    // 可扩展更多交互
    return dash;
}

window.renderDashboard = renderDashboard;
