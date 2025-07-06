// 代码生成与多Agent协作交互组件
function renderWorkflow() {
    const container = document.createElement('div');
    container.className = 'workflow-panel';
    container.innerHTML = `
        <h2>多Agent代码生成</h2>
        <textarea id="requirement-input" rows="4" style="width:100%;margin-bottom:12px;" placeholder="请输入你的代码需求，如：写一个斐波那契数列函数..."></textarea>
        <button id="run-workflow-btn" style="padding:10px 24px;">生成代码</button>
        <div id="workflow-result" style="margin-top:24px;"></div>
    `;
    container.querySelector('#run-workflow-btn').onclick = async () => {
        const requirement = container.querySelector('#requirement-input').value.trim();
        if (!requirement) { alert('请输入需求'); return; }
        const token = localStorage.getItem('token');
        const resultDiv = container.querySelector('#workflow-result');
        resultDiv.innerHTML = '正在生成，请稍候...';
        const res = await fetch('/workflow/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ requirement })
        });
        if (res.ok) {
            const data = await res.json();
            resultDiv.innerHTML = `
                <h3>分析任务</h3>
                <pre>${data.tasks.map((t,i)=>`${i+1}. ${t}`).join('\n')}</pre>
                <h3>生成代码</h3>
                <pre>${data.codes.join('\n\n')}</pre>
                <h3>代码优化建议</h3>
                <pre>${data.suggestions}</pre>
                <h3>最终代码</h3>
                <pre>${data.final_code}</pre>
                <h3>自动生成文档</h3>
                <pre>${data.doc}</pre>
                <h3>单元测试代码</h3>
                <pre>${data.test_code}</pre>
            `;
        } else {
            resultDiv.innerHTML = '生成失败，请重试';
        }
    };
    return container;
}

window.renderWorkflow = renderWorkflow;
