// 交互式Agent协作可视化组件
const agents = [
    { name: "需求分析Agent", color: "#4f8cff" },
    { name: "代码生成Agent", color: "#34bfa3" },
    { name: "代码审查Agent", color: "#ffb74d" },
    { name: "代码整合Agent", color: "#f06292" },
    { name: "文档Agent", color: "#9575cd" },
    { name: "测试Agent", color: "#64b5f6" }
];

function renderAgents() {
    const container = document.createElement('div');
    container.className = 'agent-visual';
    agents.forEach(agent => {
        const card = document.createElement('div');
        card.className = 'agent-card';

        // 圆形色块
        const avatar = document.createElement('div');
        avatar.className = 'agent-avatar';
        avatar.style.background = agent.color;

        // 名称
        const name = document.createElement('div');
        name.className = 'agent-name';
        name.textContent = agent.name;

        card.appendChild(avatar);
        card.appendChild(name);
        container.appendChild(card);
    });
    return container;
}

window.renderAgents = renderAgents;
