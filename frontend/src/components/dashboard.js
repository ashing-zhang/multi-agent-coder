import { getToken, validateToken, setLoginState } from './auth.js';
import { checkAndSetLoginState } from './loginState.js';
import { agentFormConfig } from './agentFormConfig.js';
// 仪表盘组件（展示用户信息和Agent协作流程）
export function renderDashboardAuthbar(userinfo, apiKeyBtnHtml, isLoggedIn, props = {}) {
    const authbar = document.createElement('div');
    authbar.className = 'dashboard-authbar';
    if (isLoggedIn) {
        authbar.innerHTML = `
            <button class="logout-btn small-btn" id="dashboard-logout" style="vertical-align: middle;">退出登录</button>
            <span class="login-status">已登录</span>
            ${apiKeyBtnHtml}
        `;
    } else {
        authbar.innerHTML = `
            <button class="login-btn small-btn" id="dashboard-login" style="vertical-align: middle;">登录</button>
        `;
    }
    // 事件绑定
    const loginBtn = authbar.querySelector('#dashboard-login');
    if (loginBtn) {
        loginBtn.onclick = () => {
            window.location.href = 'login.html';
        };
    }
    const logoutBtn = authbar.querySelector('#dashboard-logout');
    if (logoutBtn) {
        logoutBtn.onclick = async () => {
            try {
                const token = localStorage.getItem('token');
                if (token && props.onLogout) props.onLogout();
            } catch (e) {
                console.error('Logout error:', e);
                localStorage.removeItem('token');
            }
        };
    }
    return authbar;
}
// 仪表盘组件（展示用户信息和Agent协作流程）
export function renderDashboard(props = {}) {
    // 创建一个新的 div 元素，作为仪表盘的主容器
    const container = document.createElement('div');
    container.className = 'dashboard';

    // ====== 新增：本地持久化相关函数 ======
    function persistAgentResult(agentType) {
        // 只存储 agentType
        localStorage.setItem('lastActiveAgent', agentType);
    }
    /**
     * 刷新还原：只恢复上次激活的 Agent 按钮和表单渲染，不恢复输入内容和结果
     */
    function restoreLastAgentResult() {
        const lastActiveAgent = localStorage.getItem('lastActiveAgent');
        if (!lastActiveAgent) return;
        setTimeout(() => {
            // 高亮按钮
            const btn = container.querySelector(`.dashboard-action[data-action='${lastActiveAgent}']`);
            if (btn) {
                btn.classList.add('dashboard-action-active');
            }
            // 只渲染空表单
            showAgentForm(lastActiveAgent, async () => {}, null, true);
        }, 0);
    }
    function clearPersistedAgentResult() {
        localStorage.removeItem('lastAgentResult');
        localStorage.removeItem('lastActiveAgent');
    }
    // ====== 本地持久化相关函数结束 ======

    // 表单内容缓存对象
    const lastFormData = {};

    // 通用表单渲染，支持file类型
    // onSubmit 是一个回调函数，当表单提交时会被调用，通常用于处理表单数据的生成、请求等逻辑
    function showAgentForm(type, onSubmit, initialFormData = null, restoreMode = false) {
        const config = agentFormConfig[type] || agentFormConfig['agent_workflow'];
        const formArea = container.querySelector('#agent-form-area');
        const resultArea = container.querySelector('#agent-result-area');
        // 渲染前保存当前表单内容
        if (formArea.firstChild && formArea.firstChild.tagName === 'FORM') {
            // 先获取当前表单（formArea 的第一个子元素）
            const oldForm = formArea.firstChild;
            // 获取当前表单的 agent 类型（data-agent-type 属性）
            const oldType = oldForm.getAttribute('data-agent-type');
            // 如果存在 agent 类型，则保存该类型下的表单数据
            if (oldType) {
                // 初始化该类型的缓存对象
                lastFormData[oldType] = {};
                // 遍历表单中的所有元素（input、textarea等）
                Array.from(oldForm.elements).forEach(el => {
                    // 只处理有 name 属性且类型为 textarea 或 input 的元素
                    if (el.name && (el.type === 'textarea' || el.type === 'input')) {
                        // 跳过文件类型的 input（file 类型不保存 value）
                        if (el.type === 'file') {
                            // 文件类型不做处理
                        } else {
                            // 其他类型（如文本框、文本域）保存其当前值
                            lastFormData[oldType][el.name] = el.value;
                        }
                    }
                });
            }
        }
        // 只在非恢复模式下清除缓存
        if (!restoreMode) clearPersistedAgentResult();
        formArea.innerHTML = '';
        resultArea.innerHTML = '';
        const form = document.createElement('form');
        form.className = 'agent-form';
        form.setAttribute('data-agent-type', type);
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
        // 不再恢复表单内容
        // 表单渲染后立即存储当前agent（仅非恢复模式）
        if (!restoreMode) {
            setTimeout(() => {
                persistAgentResult(type);
            }, 0);
        }
        // 表单输入时不再自动保存内容
        form.addEventListener('input', () => {
            // persistAgentResult(type, formData.requirement || '', null, formData); // 移除
        });
        form.onsubmit = async (e) => {
            e.preventDefault();
            onSubmit(form, resultArea);
        };
        form.querySelector('#agent-cancel').onclick = () => { formArea.innerHTML = ''; resultArea.innerHTML = ''; clearPersistedAgentResult(); };
        formArea.appendChild(form);
    }

    // 获取当前用户信息（含api_key）
    async function fetchUserInfo(token) {
        if (!token) return null;
        // 通过在请求头中添加Authorization: Bearer <token>，后端可以根据token识别用户并返回其信息
        const res = await fetch('/auth/userinfo', {
            headers: { 'Authorization': 'Bearer ' + token }
        });
        if (!res.ok) return null;
        return await res.json();
    }


    // 先检查登录状态，然后根据状态渲染不同的初始内容
    async function initializeDashboard() {
        // token 是保存在浏览器中的（如 localStorage），通过 getToken() 获取
        const token = getToken();
        let isLoggedIn = false;
        if (token) {
            try {
                isLoggedIn = await validateToken(token);
                if (!isLoggedIn) {
                    localStorage.removeItem('token');
                }
            } catch (e) {
                console.error('Token validation error:', e);
                localStorage.removeItem('token');
                isLoggedIn = false;
            }
        }
        let userinfo = null;
        if (isLoggedIn) {
            userinfo = await fetchUserInfo(token);
        }
        // 根据登录状态和api_key渲染不同的初始内容
        let apiKeyBtnHtml = '';
        if (userinfo && userinfo.api_key) {
            apiKeyBtnHtml = `<button class="login-btn small-btn" id="show-apikey-btn" type="button" style="margin-left:18px;background:#e6fbe6;color:#15803d;border:1px solid #a7f3d0;">API Key已设置</button>`;
        } else if (userinfo) {
            apiKeyBtnHtml = `<button class="login-btn small-btn" id="show-apikey-btn" type="button" style="margin-left:18px;">设置API Key</button>`;
        }
        
        let mainContentHtml = `
            <div class="dashboard-horizontal-wrapper" style="display:flex;align-items:center;justify-content:center;height:70vh;width:100%;">
                <div class="dashboard-content-row"></div>
                <div id="agent-result-area" style="flex:1;min-width:0;min-height:200px;"></div>
            </div>
        `;
        container.innerHTML = `${mainContentHtml}`;
        
        // 新增：为历史按钮单独创建语义化容器
        if (isLoggedIn) {
            // 新增：左上角历史按钮及结果区容器
            const historyBarHtml = `
                <div class="history-btn-bar" style="position:absolute;left:24px;top:24px;z-index:200;display:flex;align-items:flex-start;gap:18px;">
                    <button class="login-btn small-btn" id="show-history-btn" style="background:#f3f4f6;color:#2563eb;">显示历史需求</button>
                </div>
            `;
            const historyContainer = document.createElement('div');
            historyContainer.className = 'history-container';
            historyContainer.innerHTML = historyBarHtml;
            // 这里的 document 是指当前网页的文档对象（Document Object Model, DOM），
            // 它代表了整个页面的结构和内容。通过 document.body.appendChild(historyContainer)，
            // 我们将历史按钮的容器（historyContainer）添加到页面的 <body> 元素中，
            // 这样用户就能在页面上看到这个历史按钮了。
            document.body.appendChild(historyContainer);
        }
        // 渲染dashboard-content-row内容，并在渲染后绑定事件
        setTimeout(() => {
            const row = container.querySelector('.dashboard-content-row');
            if (row) {
                row.innerHTML = `
                    <div class="dashboard-actions" style="flex:0 0 180px;max-width:200px;margin:0 0 0 0;">
                        <button class="dashboard-action" data-action="requirement">需求生成Agent</button>
                        <button class="dashboard-action" data-action="coder">代码生成Agent</button>
                        <button class="dashboard-action" data-action="doc">文档生成Agent</button>
                        <button class="dashboard-action" data-action="reviewer">代码审查Agent</button>
                        <button class="dashboard-action" data-action="finalizer">代码整合Agent</button>
                        <button class="dashboard-action" data-action="test">测试生成Agent</button>
                        <button class="dashboard-action" data-action="agent_workflow">Agent Workflow</button>
                    </div>
                    <div id="agent-form-area" style="flex:0 0 380px;max-width:420px;min-height:200px;"></div>
                `;
                // 先恢复表单/结果，再绑定事件
                restoreLastAgentResult();
                initializeDashboardFeatures(userinfo);
            }
            // 新增：绑定历史需求按钮事件
            if (isLoggedIn) {
                const btn = document.querySelector('#show-history-btn');
                if (btn) {
                    btn.onclick = function() {
                        window.location.href = 'history.html';
                    };
                }
            }
        }, 0);
        // 不要在setTimeout外部再调用initializeDashboardFeatures
        // 通知外部渲染authbar
        if (props.onAuthbar) {
            props.onAuthbar(userinfo, apiKeyBtnHtml, isLoggedIn, props);
        }
    }

    // 初始化仪表盘功能
    function initializeDashboardFeatures(userinfo) {
        // 检查并设置API Key按钮的初始状态
        function updateApiKeyButtonState(apiKey) {
            const apiKeyBtn = container.querySelector('#show-apikey-btn');
            if (apiKeyBtn && apiKey) {
                apiKeyBtn.textContent = 'API Key已设置';
                apiKeyBtn.style.background = '#e6fbe6';
                apiKeyBtn.style.color = '#15803d';
                apiKeyBtn.style.border = '1px solid #a7f3d0';
            } else if (apiKeyBtn) {
                apiKeyBtn.textContent = '设置API Key';
                apiKeyBtn.style.background = '';
                apiKeyBtn.style.color = '';
                apiKeyBtn.style.border = '';
            }
        }
        // 登录/退出事件
        const loginBtn = container.querySelector('#dashboard-login');
        if (loginBtn) {
            loginBtn.onclick = () => {
                window.location.href = 'login.html';
            };
        }
        const logoutBtn = container.querySelector('#dashboard-logout');
        if (logoutBtn) {
            logoutBtn.onclick = async () => {
                try {
                    const token = localStorage.getItem('token');
                    if (token && props.onLogout) props.onLogout();
                } catch (e) {
                    console.error('Logout error:', e);
                    localStorage.removeItem('token');
                }
            };
        }
        // API Key 弹窗逻辑
        let apiKeyDialog = null;
        const apiKeyBtn = container.querySelector('#show-apikey-btn');
        if (apiKeyBtn) {
            apiKeyBtn.onclick = () => {
                // 如果API Key已经设置，显示清除选项
                if (userinfo && userinfo.api_key) {
                    // 如果已经存在API Key清除弹窗，则不再重复创建，直接返回
                    if (document.getElementById('apikey-clear-dialog')) return;
                    const clearDialog = document.createElement('div');
                    clearDialog.id = 'apikey-clear-dialog';
                    clearDialog.style = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.18);z-index:9999;display:flex;align-items:center;justify-content:center;';
                    clearDialog.innerHTML = `
                        <div style="background:#fff;padding:28px 32px 18px 32px;border-radius:12px;box-shadow:0 4px 24px #888;min-width:320px;display:flex;flex-direction:column;align-items:center;">
                            <div style="font-size:16px;color:#222;margin-bottom:18px;">API Key已设置。是否要清除当前的API Key？</div>
                            <div style="display:flex;gap:12px;">
                              <button id="clear-apikey-confirm-btn" class="login-btn small-btn" type="button">确定</button>
                              <button id="clear-apikey-cancel-btn" class="register-cancel-btn" type="button">取消</button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(clearDialog);
                    clearDialog.querySelector('#clear-apikey-confirm-btn').onclick = async () => {
                        // 清除API Key
                        const token = getToken();
                        // 这段代码通过向后端接口 /api/set_key 发送POST请求，将 api_key 设为空字符串，从而清除用户当前设置的API Key。
                        // 请求头中包含了Content-Type和用户的Bearer Token用于身份验证。
                        await fetch('/api/set_key', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                            body: JSON.stringify({ api_key: '' })
                        });
                        // 关闭API Key清除弹窗
                        document.body.removeChild(clearDialog);
                        // 重新获取用户信息，确保前端状态与后端同步
                        const newUserinfo = await fetchUserInfo(token);
                        // 根据最新的API Key状态，更新按钮的显示（如禁用/启用、文字变化等）
                        updateApiKeyButtonState(newUserinfo.api_key);
                        // 更新本地的用户信息对象，保持数据一致
                        userinfo.api_key = newUserinfo.api_key;
                        // 美化弹窗：API Key已清除
                        if (!document.getElementById('apikey-cleared-dialog')) {
                            const dialog = document.createElement('div');
                            dialog.id = 'apikey-cleared-dialog';
                            dialog.style = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.18);z-index:9999;display:flex;align-items:center;justify-content:center;';
                            dialog.innerHTML = `
                                <div style="background:#fff;padding:28px 32px 18px 32px;border-radius:12px;box-shadow:0 4px 24px #888;min-width:320px;display:flex;flex-direction:column;align-items:center;">
                                    <div style="font-size:16px;color:#15803d;margin-bottom:18px;">API Key已清除</div>
                                    <button id="apikey-cleared-ok-btn" class="login-btn small-btn" type="button" style="min-width:80px;">确定</button>
                                </div>
                            `;
                            document.body.appendChild(dialog);
                            dialog.querySelector('#apikey-cleared-ok-btn').onclick = () => {
                                document.body.removeChild(dialog);
                            };
                            dialog.addEventListener('click', (e) => {
                                if (e.target === dialog) {
                                    document.body.removeChild(dialog);
                                }
                            });
                        }
                    };
                    clearDialog.querySelector('#clear-apikey-cancel-btn').onclick = () => {
                        document.body.removeChild(clearDialog);
                    };
                    clearDialog.addEventListener('click', (e) => {
                        if (e.target === clearDialog) {
                            document.body.removeChild(clearDialog);
                        }
                    });
                    return;
                }
                if (apiKeyDialog) return;
                apiKeyDialog = document.createElement('div');
                apiKeyDialog.style = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.18);z-index:9999;display:flex;align-items:center;justify-content:center;';
                apiKeyDialog.innerHTML = `
                    <div style="background:#fff;padding:28px 32px 18px 32px;border-radius:12px;box-shadow:0 4px 24px #888;min-width:320px;display:flex;flex-direction:column;align-items:center;">
                        <input id="deepseek-api-key-input" type="text" placeholder="DeepSeek API Key" style="width:220px;padding:8px 12px;border-radius:5px;border:1px solid #ccc;font-size:15px;margin-bottom:16px;" />
                        <div style="display:flex;gap:12px;">
                          <button id="set-deepseek-key-btn" class="login-btn small-btn" type="button">确定</button>
                          <button id="cancel-apikey-btn" class="register-cancel-btn" type="button">取消</button>
                        </div>
                        <div class="agent-message" id="apikey-msg" style="margin-top:10px;padding:4px 8px;border-radius:5px;font-size:13px;display:none;"></div>
                    </div>
                `;
                document.body.appendChild(apiKeyDialog);
                const apiKeyInput = apiKeyDialog.querySelector('#deepseek-api-key-input');
                const apiKeyMsg = apiKeyDialog.querySelector('#apikey-msg');
                apiKeyDialog.querySelector('#set-deepseek-key-btn').onclick = async () => {
                    const key = apiKeyInput.value.trim();
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
                        const token = getToken();
                        const res = await fetch('/set_key', {
                            method: 'POST',
                            // 设置请求头，指定内容类型为JSON，并添加Bearer类型的用户认证token
                            headers: { 
                                'Content-Type': 'application/json', // 请求体为JSON格式
                                'Authorization': 'Bearer ' + token  // 使用Bearer Token进行身份验证
                            },
                            body: JSON.stringify({ api_key: key })
                        });
                        if (res.ok) {
                            apiKeyMsg.textContent = 'API已设置';
                            apiKeyMsg.style.background = '#e6fbe6';
                            apiKeyMsg.style.color = '#15803d';
                            apiKeyMsg.style.border = '1px solid #a7f3d0';
                            // 刷新userinfo和按钮
                            const newUserinfo = await fetchUserInfo();
                            updateApiKeyButtonState(newUserinfo.api_key);
                            userinfo.api_key = newUserinfo.api_key;
                            setTimeout(() => {
                                if (apiKeyDialog && document.body.contains(apiKeyDialog)) {
                                    document.body.removeChild(apiKeyDialog);
                                    apiKeyDialog = null;
                                }
                            }, 1500);
                        } else {
                            apiKeyMsg.textContent = 'API Key设置失败';
                            apiKeyMsg.style.background = '#fee2e2';
                            apiKeyMsg.style.color = '#b91c1c';
                            apiKeyMsg.style.border = '1px solid #fecaca';
                        }
                    } catch (e) {
                        apiKeyMsg.textContent = '网络错误，请稍后重试';
                        apiKeyMsg.style.background = '#fee2e2';
                        apiKeyMsg.style.color = '#b91c1c';
                        apiKeyMsg.style.border = '1px solid #fecaca';
                    }
                };
                apiKeyDialog.querySelector('#cancel-apikey-btn').onclick = () => {
                    document.body.removeChild(apiKeyDialog);
                    apiKeyDialog = null;
                };
                apiKeyDialog.addEventListener('click', (e) => {
                    if (e.target === apiKeyDialog) {
                        document.body.removeChild(apiKeyDialog);
                        apiKeyDialog = null;
                    }
                });
            };
        }

        // 显示自定义“请先登录”弹窗
        function showLoginRequiredDialog() {
            if (document.getElementById('login-required-dialog')) return;
            const dialog = document.createElement('div');
            dialog.id = 'login-required-dialog';
            dialog.style = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.18);z-index:9999;display:flex;align-items:center;justify-content:center;';
            dialog.innerHTML = `
                <div style="background:#fff;padding:28px 32px 18px 32px;border-radius:12px;box-shadow:0 4px 24px #888;min-width:320px;display:flex;flex-direction:column;align-items:center;">
                    <div style="font-size:16px;color:#222;margin-bottom:18px;">请先登录！</div>
                    <button id="login-required-ok-btn" class="login-btn small-btn" type="button" style="min-width:80px;">确定</button>
                </div>
            `;
            document.body.appendChild(dialog);
            dialog.querySelector('#login-required-ok-btn').onclick = () => {
                document.body.removeChild(dialog);
            };
            dialog.addEventListener('click', (e) => {
                if (e.target === dialog) {
                    document.body.removeChild(dialog);
                }
            });
        }
        // 异步校验token有效性
        async function checkLoginValid() {
            const token = localStorage.getItem('token');
            if (!token) {
                showLoginRequiredDialog();
                return false;
            }
            try {
                const res = await fetch('/auth/validate_token', {
                    method: 'GET',
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                if (res.ok) return true;
                if (res.status === 401) {
                    localStorage.removeItem('token');
                    showLoginRequiredDialog();
                }
                return false;
            } catch {
                showLoginRequiredDialog();
                return false;
            }
        }

        // 流式处理函数
        async function streamAgentResponse(url, data, resultDiv, msgDiv) {
            try {
                const token = localStorage.getItem('token');
                const res = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { 'Authorization': 'Bearer ' + token } : {})
                    },
                    body: JSON.stringify(data)
                });

                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }

                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let result = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    result += chunk;

                    // 实时渲染到结果区域
                    resultDiv.innerHTML = `<pre style='white-space:pre-wrap;word-break:break-all;margin:8px 0 0 0;'>${result}</pre>`;
                }

                // 流式完成后的处理
                msgDiv.textContent = '生成完成，可保存到本地！';
                msgDiv.style.background = '#e6fbe6';
                msgDiv.style.color = '#15803d';
                msgDiv.style.border = '1px solid #a7f3d0';

                return result;
            } catch (e) {
                msgDiv.textContent = '流式请求失败，请重试';
                msgDiv.style.background = '#fee2e2';
                msgDiv.style.color = '#b91c1c';
                msgDiv.style.border = '1px solid #fecaca';
                throw e;
            }
        }

        // 保存生成结果到本地
        function showSaveButton(result, type, agentType) {
            const resultArea = container.querySelector('#agent-result-area'); // Changed from area
            let saveBtn = resultArea.querySelector('.agent-save-btn');
            if (saveBtn) saveBtn.remove();
            // 创建一个新的 button 元素，用于“保存到本地”功能
            saveBtn = document.createElement('button');
            saveBtn.textContent = '保存到本地';
            saveBtn.className = 'agent-save-btn login-btn small-btn';
            saveBtn.type = 'button';
            // 设置保存按钮的左边距为10像素，使其与前面的元素有一定的间隔
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
            resultArea.appendChild(saveBtn);
        }



        const agentActions = {
            requirement: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                // 1. 展示“需求分析”表单，用户填写后回调此函数
                showAgentForm('requirement', async (form, resultArea) => {
                    // 2. 获取用户输入的需求描述，并去除首尾空格
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return; // 如果未填写需求，直接返回

                    // 3. 获取用于展示结果的区域
                    const area = container.querySelector('#agent-result-area');

                    // 4. 检查用户信息和API key是否已设置，未设置则提示
                    if (!userinfo || !userinfo.api_key) {
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

                    // 5. 创建或复用消息提示div，显示“生成中...”的提示
                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '生成中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    // 6. 创建或复用需求分析结果展示区域
                    let resultDiv = area.querySelector('.requirement-analysis-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'requirement-analysis-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>需求分析结果：</b>';

                    // 7. 调用流式API进行需求分析，将结果实时展示到resultDiv
                    try {
                        const result = await streamAgentResponse(
                            '/requirements/stream',
                            { description: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('requirement', requirement, result); // 移除
                        showSaveButton(result, 'md', 'requirement');
                    } catch (e) {
                        // 10. 捕获并打印流式API异常
                        console.error('Stream error:', e);
                    }
                });
            },
            agent_workflow: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                showAgentForm('agent_workflow', async (form, resultArea) => {
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return;
                    const area = container.querySelector('#agent-result-area');

                    if (!userinfo || !userinfo.api_key) {
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
                    msgDiv.textContent = 'Workflow执行中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    // 创建结果展示区域
                    let resultDiv = area.querySelector('.workflow-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'workflow-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>Agent Workflow 执行结果：</b>';

                    // 使用流式API
                    try {
                        const result = await streamAgentResponse(
                            '/workflow/stream',
                            { requirement: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('agent_workflow', requirement, result); // 移除
                        showSaveButton(result, 'py', 'agent_workflow');
                    } catch (e) {
                        console.error('Workflow stream error:', e);
                    }
                });
            },
            doc: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                showAgentForm('doc', async (form, resultArea) => {
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return;
                    const area = container.querySelector('#agent-result-area');

                    if (!userinfo || !userinfo.api_key) {
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

                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '生成中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    let resultDiv = area.querySelector('.doc-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'doc-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>文档生成结果：</b>';

                    try {
                        const result = await streamAgentResponse(
                            '/agent/doc/stream',
                            { requirement: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('doc', requirement, result); // 移除
                        showSaveButton(result, 'md', 'doc');
                    } catch (e) {
                        console.error('Doc stream error:', e);
                    }
                });
            },
            coder: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                showAgentForm('coder', async (form, resultArea) => {
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return;
                    const area = container.querySelector('#agent-result-area');

                    if (!userinfo || !userinfo.api_key) {
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

                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '生成中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    let resultDiv = area.querySelector('.coder-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'coder-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>代码生成结果：</b>';

                    try {
                        const result = await streamAgentResponse(
                            '/agent/coder/stream',
                            { requirement: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('coder', requirement, result); // 移除
                        showSaveButton(result, 'py', 'coder');
                    } catch (e) {
                        console.error('Coder stream error:', e);
                    }
                });
            },
            reviewer: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                showAgentForm('reviewer', async (form, resultArea) => {
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return;
                    const area = container.querySelector('#agent-result-area');

                    if (!userinfo || !userinfo.api_key) {
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

                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '审查中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    let resultDiv = area.querySelector('.reviewer-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'reviewer-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>代码审查结果：</b>';

                    try {
                        const result = await streamAgentResponse(
                            '/agent/reviewer/stream',
                            { requirement: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('reviewer', requirement, result); // 移除
                        showSaveButton(result, 'txt', 'reviewer');
                    } catch (e) {
                        console.error('Reviewer stream error:', e);
                    }
                });
            },
            finalizer: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                showAgentForm('finalizer', async (form, resultArea) => {
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return;
                    const area = container.querySelector('#agent-result-area');

                    if (!userinfo || !userinfo.api_key) {
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

                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '整合中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    let resultDiv = area.querySelector('.finalizer-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'finalizer-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>代码整合结果：</b>';

                    try {
                        const result = await streamAgentResponse(
                            '/agent/finalizer/stream',
                            { requirement: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('finalizer', requirement, result); // 移除
                        showSaveButton(result, 'py', 'finalizer');
                    } catch (e) {
                        console.error('Finalizer stream error:', e);
                    }
                });
            },
            test: async () => {
                if (!(await checkLoginValid())) {
                    return;
                }
                showAgentForm('test', async (form, resultArea) => {
                    const requirement = form.requirement.value.trim();
                    if (!requirement) return;
                    const area = container.querySelector('#agent-result-area');

                    if (!userinfo || !userinfo.api_key) {
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

                    let msgDiv = area.querySelector('.agent-message');
                    if (!msgDiv) {
                        msgDiv = document.createElement('div');
                        msgDiv.className = 'agent-message';
                        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
                        area.appendChild(msgDiv);
                    }
                    msgDiv.textContent = '生成中...';
                    msgDiv.style.background = '#e6f0ff';
                    msgDiv.style.color = '#2563eb';
                    msgDiv.style.border = '1px solid #b6d4fe';

                    let resultDiv = area.querySelector('.test-result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.className = 'test-result';
                        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
                        area.appendChild(resultDiv);
                    }
                    resultDiv.innerHTML = '<b>测试生成结果：</b>';

                    try {
                        const result = await streamAgentResponse(
                            '/agent/test/stream',
                            { requirement: requirement },
                            resultDiv,
                            msgDiv
                        );
                        // persistAgentResult('test', requirement, result); // 移除
                        showSaveButton(result, 'py', 'test');
                    } catch (e) {
                        console.error('Test stream error:', e);
                    }
                });
            }
        };

        container.querySelectorAll('.dashboard-action').forEach(btn => {
            btn.onclick = (e) => {
                // 新：点击时移除所有按钮的高亮，再高亮当前按钮
                container.querySelectorAll('.dashboard-action').forEach(b => b.classList.remove('dashboard-action-active'));
                btn.classList.add('dashboard-action-active');
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
        // --- 新增：如果有高亮按钮但表单区为空，自动触发一次点击，保证表单和按钮状态同步 ---
        setTimeout(() => {
            const activeBtn = container.querySelector('.dashboard-action.dashboard-action-active');
            const formArea = container.querySelector('#agent-form-area');
            // 如果有高亮按钮且表单区为空（或未渲染），自动触发点击
            if (activeBtn && (!formArea || !formArea.firstChild)) {
                activeBtn.click();
            }
        }, 0);
    }

    // 开始初始化
    console.log('Starting dashboard initialization...');
    initializeDashboard().catch(error => {
        console.error('Dashboard initialization failed:', error);
        container.innerHTML = '<div style="color: red; padding: 20px;">Dashboard 初始化失败: ' + error.message + '</div>';
    });
    return container;
}
