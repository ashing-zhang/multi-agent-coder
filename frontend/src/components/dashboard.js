// 仪表盘组件（展示用户信息和Agent协作流程）
export function renderDashboard(props = {}) {
    const container = document.createElement('div');
    container.className = 'dashboard';
    container.innerHTML = `
        <div class="dashboard-authbar">
            <button class="login-btn small-btn" id="dashboard-login">登录</button>
            <button class="logout-btn small-btn" id="dashboard-logout">退出登录</button>
        </div>
        <div class="dashboard-actions">
            <button class="dashboard-action" data-action="requirement">需求Agent</button>
            <button class="dashboard-action" data-action="doc">文档Agent</button>
            <button class="dashboard-action" data-action="coder">代码生成Agent</button>
            <button class="dashboard-action" data-action="reviewer">代码审查Agent</button>
            <button class="dashboard-action" data-action="finalizer">代码整合Agent</button>
            <button class="dashboard-action" data-action="agent_workflow">Agent Workflow</button>
        </div>
        <div id="agent-form-area"></div>
    `;
    // 登录状态提示
    const loginStatus = document.createElement('span');
    loginStatus.className = 'login-status';
    loginStatus.style = 'margin-left:12px;font-size:14px;color:#15803d;display:none;';
    loginStatus.textContent = '已登录';
    container.querySelector('.dashboard-authbar').appendChild(loginStatus);

    function setLoginState(loggedIn) {
        const loginBtn = container.querySelector('#dashboard-login');
        const logoutBtn = container.querySelector('#dashboard-logout');
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
    // 默认未登录
    setLoginState(false);
    // 登录/退出事件
    container.querySelector('#dashboard-login').onclick = () => {
        if (props.onLogin) props.onLogin();
        setLoginState(true);
    };
    container.querySelector('#dashboard-logout').onclick = () => {
        if (props.onLogout) props.onLogout();
        setLoginState(false);
    };

    // DeepSeek API Key输入区域
    const apiKeyDiv = document.createElement('div');
    apiKeyDiv.style = 'margin: 12px 0 0 0; display: flex; align-items: center; gap: 8px;';
    apiKeyDiv.innerHTML = `
        <input id="deepseek-api-key-input" type="text" placeholder="DeepSeek API Key" style="flex:1;max-width:260px;padding:6px 10px;border-radius:5px;border:1px solid #ccc;font-size:15px;" />
        <button id="set-deepseek-key-btn" class="login-btn small-btn" type="button">设置API Key</button>
    `;
    container.insertBefore(apiKeyDiv, container.querySelector('.dashboard-actions'));
    // 提示条
    let apiKeyMsg = document.createElement('div');
    apiKeyMsg.className = 'agent-message';
    apiKeyMsg.style = 'margin-top:6px;padding:6px 10px;border-radius:5px;font-size:14px;display:none;';
    apiKeyDiv.appendChild(apiKeyMsg);
    // 事件绑定
    apiKeyDiv.querySelector('#set-deepseek-key-btn').onclick = async () => {
        const key = apiKeyDiv.querySelector('#deepseek-api-key-input').value.trim();
        if (!key) {
            apiKeyMsg.textContent = '请输入API Key';
            apiKeyMsg.style.background = '#fee2e2';
            apiKeyMsg.style.color = '#b91c1c';
            apiKeyMsg.style.border = '1px solid #fecaca';
            apiKeyMsg.style.display = '';
            return;
        }
        apiKeyMsg.textContent = '设置中...';
        apiKeyMsg.style.background = '#e6f0ff';
        apiKeyMsg.style.color = '#2563eb';
        apiKeyMsg.style.border = '1px solid #b6d4fe';
        apiKeyMsg.style.display = '';
        try {
            /*
                向后端发送一个 POST 请求，把用户输入的 API Key 传递给 
                /api/set_deepseek_key 接口，实现 API Key 的设置。
            */
            const res = await fetch('/api/set_deepseek_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: key })  //转换为JSON字符串
            });
            if (res.ok) {
                const data = await res.json();
                apiKeyMsg.textContent = 'API已设置';
                apiKeyMsg.style.background = '#e6fbe6';
                apiKeyMsg.style.color = '#15803d';
                apiKeyMsg.style.border = '1px solid #a7f3d0';
                // 保存model_client标志到全局
                window._model_client = data.model_client;
            } else {
                apiKeyMsg.textContent = 'API Key设置失败';
                apiKeyMsg.style.background = '#fee2e2';
                apiKeyMsg.style.color = '#b91c1c';
                apiKeyMsg.style.border = '1px solid #fecaca';
                window._model_client = undefined;
            }
        } catch (e) {
            apiKeyMsg.textContent = '网络错误，请稍后重试';
            apiKeyMsg.style.background = '#fee2e2';
            apiKeyMsg.style.color = '#b91c1c';
            apiKeyMsg.style.border = '1px solid #fecaca';
            window._model_client = undefined;
        }
    };

    // agent表单配置，增加附件上传字段
    const agentFormConfig = {
        requirement: {
            title: '生成任务的需求文档',
            fields: [
                { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入你想完成的编码任务(任务描述可附件上传)', required: true },
                // 可选项，不是必选项
                { label: '附件', name: 'file', type: 'file', accept: '.txt,.md,.pdf,.doc,.docx,.zip,.rar,.7z,.py,.js,.java,.cpp,.c,.json,.csv', required: false }
            ]
        },
        doc: {
            title: '编写代码的README文件',
            fields: [
                { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入你想生成文档的代码', required: true },
                { label: '附件', name: 'file', type: 'file', accept: '.txt,.md,.py,.js,.java,.cpp,.c,.json,.csv,.zip', required: false }
            ]
        },
        coder: {
            title: '根据需求描述或需求文档生成代码',
            fields: [
                { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入需求描述', required: true },
                { label: '附件', name: 'file', type: 'file', accept: '.txt,.md,.pdf,.doc,.docx,.zip,.rar,.7z,.py,.js,.java,.cpp,.c,.json,.csv', required: false }
            ]
        },
        reviewer: {
            title: '对代码提供优化建议',
            fields: [
                { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入代码', required: true },
                { label: '附件', name: 'file', type: 'file', accept: '.txt,.md,.py,.js,.java,.cpp,.c,.json,.csv,.zip', required: false }
            ]
        },
        finalizer: {
            title: '根据代码和优化建议修改代码',
            fields: [
                { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入代码和优化建议', required: true },
                { label: '附件', name: 'file', type: 'file', accept: '.txt,.md,.py,.js,.java,.cpp,.c,.json,.csv,.zip', required: false }
            ]
        },
        agent_workflow: {
            title: '根据用户描述的需求端到端生成可信赖代码',
            fields: [
                { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入完整需求描述', required: true },
                { label: '附件', name: 'file', type: 'file', accept: '.txt,.md,.pdf,.doc,.docx,.zip,.rar,.7z,.py,.js,.java,.cpp,.c,.json,.csv', required: false }
            ]
        }
    };

    // 保存生成结果到本地
    function showSaveButton(result, type, agentType) {
        const area = container.querySelector('#agent-form-area');
        let saveBtn = area.querySelector('.agent-save-btn');
        if (saveBtn) saveBtn.remove();
        saveBtn = document.createElement('button');
        saveBtn.textContent = '保存到本地';
        saveBtn.className = 'agent-save-btn login-btn small-btn';
        saveBtn.type = 'button';
        saveBtn.style.marginLeft = '10px';
        saveBtn.onclick = () => {
            const blob = new Blob([result], { type: 'text/plain' });
            let ext = '.txt';
            if (type === 'md') ext = '.md';
            if (type === 'py') ext = '.py';
            // 可根据agentType进一步细分
            const filename = `${agentType}_result_${Date.now()}${ext}`;
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            setTimeout(() => {
                document.body.removeChild(link);
                URL.revokeObjectURL(link.href);
            }, 100);
        };
        area.appendChild(saveBtn);
    }

    // 通用表单渲染，支持file类型
    function showAgentForm(type, onSubmit) {
        const config = agentFormConfig[type] || agentFormConfig['agent_workflow'];
        // 在 container 这个节点下查找第一个 id 为 agent-form-area 的子元素
        const area = container.querySelector('#agent-form-area');
        area.innerHTML = '';
        const form = document.createElement('form');
        form.className = 'agent-form';
        let html = `<h4>${config.title}</h4>`;
        config.fields.forEach(field => {
            html += `<label for="agent-${type}-${field.name}">${field.label}</label>`;
            if (field.type === 'input') {
                html += `<input id="agent-${type}-${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}" class="login-input" ${field.required ? 'required' : ''} />`;
            } else if (field.type === 'textarea') {
                html += `<textarea id="agent-${type}-${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}" class="login-input" ${field.required ? 'required' : ''}></textarea>`;
            } else if (field.type === 'file') {
                html += `<input id="agent-${type}-${field.name}" name="${field.name}" type="file" class="login-input" ${field.accept ? `accept='${field.accept}'` : ''} ${field.required ? 'required' : ''} />`;
            }
        });
        html += `<div style="margin-top:10px;">
                  <button type="submit" class="login-btn small-btn">生成</button>
                  <button type="button" class="register-cancel-btn" id="agent-cancel">取消</button>
                </div>`;
        form.innerHTML = html;
        form.onsubmit = async (e) => {
            e.preventDefault();
            onSubmit(form);
        };
        form.querySelector('#agent-cancel').onclick = () => { area.innerHTML = ''; };
        area.appendChild(form);
    }

    const agentActions = {
        requirement: async () => {
            showAgentForm('requirement', async (form) => {
                const requirement = form.requirement.value.trim();
                if (!requirement) return;
                const area = container.querySelector('#agent-form-area');
                // 检查API key和model_client是否已设置
                if (!window._model_client) {
                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '请先设置API key';
                    msgDiv.style.background = '#fee2e2';
                    msgDiv.style.color = '#b91c1c';
                    msgDiv.style.border = '1px solid #fecaca';
                    return;
                }
                // 创建/复用消息提示div
                let msgDiv = area.querySelector('.agent-message');
                if (!msgDiv) {
                    msgDiv = document.createElement('div');
                    msgDiv.className = 'agent-message';
                    msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                    area.appendChild(msgDiv);
                }
                // 显示生成中提示
                msgDiv.textContent = '生成中...';
                msgDiv.style.background = '#e6f0ff';
                msgDiv.style.color = '#2563eb';
                msgDiv.style.border = '1px solid #b6d4fe';
                // 发起请求
                const token = localStorage.getItem('token');
                try {
                    const res = await fetch('/requirements/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token ? { 'Authorization': 'Bearer ' + token } : {})
                        },
                        body: JSON.stringify({ description: requirement })
                    });
                    if (res.ok) {
                        const data = await res.json();
                        // 展示分析结果
                        let resultDiv = area.querySelector('.requirement-analysis-result');
                        if (!resultDiv) {
                            resultDiv = document.createElement('div');
                            resultDiv.className = 'requirement-analysis-result';
                            resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                            area.appendChild(resultDiv);
                        }
                        resultDiv.innerHTML = `<b>需求分析结果：</b><pre style='white-space:pre-wrap;word-break:break-all;margin:8px 0 0 0;'>${data.requirement_analysis || '无分析结果'}</pre>`;
                        showSaveButton(data.requirement_analysis || '', 'md', 'requirement');
                        // 成功提示
                        msgDiv.textContent = '需求分析已完成，可保存到本地！';
                        msgDiv.style.background = '#e6fbe6';
                        msgDiv.style.color = '#15803d';
                        msgDiv.style.border = '1px solid #a7f3d0';
                    } else {
                        msgDiv.textContent = '需求分析失败，请重试';
                        msgDiv.style.background = '#fee2e2';
                        msgDiv.style.color = '#b91c1c';
                        msgDiv.style.border = '1px solid #fecaca';
                    }
                } catch (e) {
                    msgDiv.textContent = '网络错误，请稍后重试';
                    msgDiv.style.background = '#fee2e2';
                    msgDiv.style.color = '#b91c1c';
                    msgDiv.style.border = '1px solid #fecaca';
                }
            });
        },
        agent_workflow: async () => {
            showAgentForm('agent_workflow', async (form) => {
                const requirement = form.requirement.value.trim();
                if (!requirement) return;
                const token = localStorage.getItem('token');
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
                    // 假设保存final_code
                    showSaveButton(data.final_code || JSON.stringify(data, null, 2), 'py', 'agent_workflow');
                    alert('Agent Workflow 执行完成！\n' + JSON.stringify(data, null, 2));
                } else {
                    alert('Agent Workflow 执行失败');
                }
            });
        },
        doc: async () => showAgentForm('doc', async (form) => {
            const requirement = form.requirement.value.trim();
            if (!requirement) return;
            // 这里只演示保存md
            showSaveButton(requirement, 'md', 'doc');
            alert('文档已生成，可保存到本地！');
        }),
        coder: async () => showAgentForm('coder', async (form) => {
            const requirement = form.requirement.value.trim();
            if (!requirement) return;
            showSaveButton(requirement, 'py', 'coder');
            alert('代码已生成，可保存到本地！');
        }),
        reviewer: async () => showAgentForm('reviewer', async (form) => {
            const requirement = form.requirement.value.trim();
            if (!requirement) return;
            showSaveButton(requirement, 'txt', 'reviewer');
            alert('审查建议已生成，可保存到本地！');
        }),
        finalizer: async () => showAgentForm('finalizer', async (form) => {
            const requirement = form.requirement.value.trim();
            if (!requirement) return;
            showSaveButton(requirement, 'py', 'finalizer');
            alert('整合代码已生成，可保存到本地！');
        })
    };

    let lastActiveActionBtn = null;
    container.querySelectorAll('.dashboard-action').forEach(btn => {
        btn.onclick = (e) => {
            // 只在点击按钮时切换高亮
            if (lastActiveActionBtn !== btn) {
                if (lastActiveActionBtn) {
                    lastActiveActionBtn.classList.remove('dashboard-action-active');
                }
                btn.classList.add('dashboard-action-active');
                lastActiveActionBtn = btn;
            }
            if (props.onAction) {
                props.onAction(async () => {
                    const action = btn.dataset.action;
                    if (agentActions[action]) {
                        await agentActions[action]();
                    } else {
                        alert('暂未实现该Agent的独立API');
                    }
                });
            }
            e.stopPropagation(); // 防止冒泡
        };
    });
    return container;
}
