import { getToken, validateToken } from './auth.js';
import { agentFormConfig } from './agentFormConfig.js';
import {
    onSubmitRequirement,
    onSubmitAgentWorkflow,
    onSubmitDoc,
    onSubmitCoder,
    onSubmitReviewer,
    onSubmitFinalizer,
    onSubmitTest
} from './agent_result_area.js';

// 登录和登出事件
async function renderDashboardAuthbar(authbar, apiKeyBtnHtml, isLoggedIn, props = {}) {
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
        loginBtn.onclick = async () => {
            window.location.href = 'login.html';
        };
    }
    const logoutBtn = authbar.querySelector('#dashboard-logout');
    if (logoutBtn) {
        logoutBtn.onclick = async () => {
            try {
                const token = localStorage.getItem('token');
                if (token && props.onLogout) await props.onLogout();
            } catch (e) {
                console.error('Logout error:', e);
                localStorage.removeItem('token');
            }
        };
    }
    return authbar;
}

// 通用表单渲染，支持file类型
// onSubmit 是一个回调函数，当表单提交时会被调用，通常用于处理表单数据的生成、请求等逻辑
async function showAgentForm(container, type, onSubmit) {
    console.log("showAgentForm entered")
    const config = agentFormConfig[type] || agentFormConfig['agent_workflow'];
    const formArea = container.querySelector('#agent-form-area');
    const resultArea = container.querySelector('#agent-result-area');
    formArea.innerHTML = '';
    resultArea.innerHTML = '';
    // document: 这是一个全局对象，代表了整个 HTML 文档。它是我们与页面内容交互的入口点。
    // .createElement(): 这是 document 对象的一个方法，专门用来创建 HTML 元素。
    // 'form': 这是一个字符串参数，传递给 createElement 方法，告诉它我们想要创建的元素的标签名。你可以换成 'div', 'p', 'img' 等任何有效的 HTML 标签。
    // 当您执行 const myForm = document.createElement('form'); 时，这个新的 <form> 元素仅仅存在于 JavaScript 的内存中。它还没有出现在网页上，用户是看不到它的。
    const form = document.createElement('form');
    // 设置className,方便用 CSS 选择和样式化
    form.className = 'agent-form';
    form.setAttribute('data-agent-type', type);
    let html = `<h4>${config.title}</h4>`;
    config.fields.forEach(field => {
        html += `<label for="agent-${type}-${field.name}">${field.label}</label>`;
        if (field.type === 'input') {
            html += `<input id="agent-${type}-${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}" class="login-input" />`;
        } else if (field.type === 'textarea') {
            html += `<textarea id="agent-${type}-${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}" class="login-input"></textarea>`;
        } else if (field.type === 'file') {
            html += `<input id="agent-${type}-${field.name}" name="${field.name}" type="file" class="login-input" ${field.accept ? `accept='${field.accept}'` : ''} ${field.required ? 'required' : ''} multiple />`;
        }
    });
    html += `<div style="margin-top:10px;">
            <button type="submit" class="login-btn small-btn">生成</button>
            <button type="button" class="register-cancel-btn" id="agent-cancel">取消</button>
        </div>`;
    form.innerHTML = html;

    // 当表单提交时触发此事件处理函数
    form.onsubmit = async (e) => {
        // 阻止表单的默认提交行为（防止页面刷新）
        e.preventDefault();
        // 调用 onSubmit 函数处理表单数据和结果显示
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

        // 检查并设置API Key按钮的初始状态
async function updateApiKeyButtonState(container, apiKey) {
    //querySelector：CSS选择器
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

// 异步校验token有效性
async function checkLoginValid(node) {
    const token = localStorage.getItem('token');
    if (!token) {
        showLoginRequiredDialog(node);
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
            showLoginRequiredDialog(node);
        }
        return false;
    } catch {
        showLoginRequiredDialog(node);
        return false;
    }
}

//登录事件
async function login_event(container) {
        const loginBtn = container.querySelector('#dashboard-login');
        if (loginBtn) {
            loginBtn.onclick = () => {
                window.location.href = 'login.html';
            };
        }
}

//登出事件
async function logout_event(container, logout_func) {
        const logoutBtn = container.querySelector('#dashboard-logout');
        if (logoutBtn) {
            logoutBtn.onclick = async () => {
                try {
                    const token = localStorage.getItem('token');
                if (token && logout_func) logout_func();
                } catch (e) {
                    console.error('Logout error:', e);
                    localStorage.removeItem('token');
                }
            };
        }
}

// 显示自定义“请先登录”弹窗
async function showLoginRequiredDialog(node) {
    // 如果页面上已经存在id为'login-required-dialog'的弹窗，则不再重复创建，直接返回
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
    // 新增：弹窗关闭时重新渲染 Authbar 为未登录状态
    const rerenderAuthbarAsLoggedOut = () => {
        let authbar = node;
        if (authbar) {
            let apiKeyBtnHtml = `<button class=\"login-btn small-btn\" id=\"show-apikey-btn\" type=\"button\" style=\"margin-left:18px;\">设置API Key</button>`;
            renderDashboardAuthbar(authbar, apiKeyBtnHtml, false, {});
        }
    };
    dialog.querySelector('#login-required-ok-btn').onclick = () => {
        document.body.removeChild(dialog);
        rerenderAuthbarAsLoggedOut();
    };
    dialog.addEventListener('click', (e) => {
        if (e.target === dialog) {
            document.body.removeChild(dialog);
            rerenderAuthbarAsLoggedOut();
        }
    });
}

// 显示自定义警告弹窗
async function warning(message, type = 'warning') {
    // 如果已存在弹窗，先移除
    const existingDialog = document.getElementById('custom-warning-dialog');
    if (existingDialog) {
        document.body.removeChild(existingDialog);
    }

    // 根据类型设置不同的图标和标题
    let icon, title;
    switch (type) {
        case 'error':
            icon = '❌';
            title = '错误';
            break;
        case 'success':
            icon = '✅';
            title = '成功';
            break;
        case 'info':
            icon = 'ℹ️';
            title = '提示';
            break;
        default: // warning
            icon = '⚠️';
            title = '警告';
            break;
    }

    const dialog = document.createElement('div');
    dialog.id = 'custom-warning-dialog';
    dialog.className = 'custom-warning-dialog';

    dialog.innerHTML = `
        <div class="custom-warning-content">
            <div class="custom-warning-icon">${icon}</div>
            <div class="custom-warning-title">${title}</div>
            <div class="custom-warning-message">${message}</div>
            <button id="warning-ok-btn" class="custom-warning-btn ${type}">
                确定
            </button>
        </div>
    `;

    document.body.appendChild(dialog);

    // 绑定确定按钮事件
    const okBtn = dialog.querySelector('#warning-ok-btn');
    okBtn.onclick = () => {
        document.body.removeChild(dialog);
    };

    // 点击背景关闭弹窗
    dialog.addEventListener('click', (e) => {
        if (e.target === dialog) {
            document.body.removeChild(dialog);
        }
    });

    // 按 ESC 键关闭弹窗
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            document.body.removeChild(dialog);
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);

    // 自动聚焦到确定按钮
    okBtn.focus();
}

async function all_agent_actions(main_container, auth_container) {
    const agentActions = {
        requirement: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'requirement', (form, resultArea) => onSubmitRequirement(form, resultArea));
        },
        agent_workflow: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'agent_workflow', (form, resultArea) => onSubmitAgentWorkflow(form, resultArea));
        },
        doc: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'doc', (form, resultArea) => onSubmitDoc(form, resultArea));
        },
        coder: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'coder', (form, resultArea) => onSubmitCoder(form, resultArea));
        },
        reviewer: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'reviewer', (form, resultArea) => onSubmitReviewer(form, resultArea));
        },
        finalizer: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'finalizer', (form, resultArea) => onSubmitFinalizer(form, resultArea));
        },
        test: async () => {
            if (!(await checkLoginValid(auth_container))) {
                return;
            }
            await showAgentForm(main_container, 'test', (form, resultArea) => onSubmitTest(form, resultArea));
        }
    };

    return agentActions;
}

async function agent_event(container, agentActions) {
    container.querySelectorAll('.dashboard-action').forEach(btn => {
        // 将 onclick 的处理器直接声明为 async 函数
        // 当一个事件（比如用户的点击 click、鼠标悬停 mouseover、键盘按下 
        // keydown 等）在某个 HTML 元素上发生时，浏览器会自动创建一个包含
        // 该事件所有详细信息的对象，并将这个对象作为参数传递给相应的事件处
        // 理函数。
        btn.onclick = async (event) => {
            // 1. 处理高亮（不变）
            // 先移除所有按钮的高亮状态
            container.querySelectorAll('.dashboard-action').forEach(b => b.classList.remove('dashboard-action-active'));
            // 给当前点击的按钮添加高亮状态
            btn.classList.add('dashboard-action-active');

            // 2. 直接执行异步逻辑（修正部分）
            try {
                const action = btn.dataset.action;
                if (agentActions[action]) {
                    await agentActions[action](); // 现在这行代码可以被正确执行
                } else {
                    await warning('暂未实现该Agent的独立API', 'warning');
                }
            } catch (error) {
                console.error("执行Action时出错:", error);
                await warning("操作失败，请查看控制台。", 'error');
            }

            // 3. 阻止冒泡（不变）
            event.stopPropagation();
        };
    });
}

// 初始化仪表盘功能
async function initializeDashboardFeatures(nodes, userinfo, logout_func) {
    // 登录/退出事件
    login_event(nodes[1]);
    logout_event(nodes[1], logout_func);

        // API Key 弹窗逻辑
        let apiKeyDialog = null;
    const apiKeyBtn = nodes[1].querySelector('#show-apikey-btn');
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
                    await fetch('/set_key', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                            body: JSON.stringify({ api_key: '' })
                        });
                        // 关闭API Key清除弹窗
                        document.body.removeChild(clearDialog);
                        // 重新获取用户信息，确保前端状态与后端同步
                        const newUserinfo = await fetchUserInfo(token);
                        // 根据最新的API Key状态，更新按钮的显示（如禁用/启用、文字变化等）
                    updateApiKeyButtonState(nodes[1], newUserinfo.api_key);
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
                    // console.log("res:",res)
                        if (res.ok) {
                            apiKeyMsg.textContent = 'API已设置';
                            apiKeyMsg.style.background = '#e6fbe6';
                            apiKeyMsg.style.color = '#15803d';
                            apiKeyMsg.style.border = '1px solid #a7f3d0';
                            // 刷新userinfo和按钮
                        let newUserinfo = null;
                        try {
                            newUserinfo = await fetchUserInfo(token);
                        } catch (e) {
                            console.error('获取用户信息失败:', e);
                            // 可选：在 UI 上提示
                            apiKeyMsg.textContent = '获取用户信息失败';
                            apiKeyMsg.style.background = '#fee2e2';
                            apiKeyMsg.style.color = '#b91c1c';
                            apiKeyMsg.style.border = '1px solid #fecaca';
                            return;
                        }
                        // console.log("newUserinfo:",newUserinfo)
                        updateApiKeyButtonState(nodes[1], newUserinfo.api_key);
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

    const agentActions = await all_agent_actions(nodes[0])
    //点击其中一个agent的按钮
    await agent_event(nodes[0], agentActions)

    // --- 新增：如果有高亮按钮但表单区为空，自动触发一次点击，保证表单和按钮状态同步 ---
    setTimeout(() => {
        const activeBtn = nodes[0].querySelector('.dashboard-action.dashboard-action-active');
        const formArea = nodes[0].querySelector('#agent-form-area');
        // 如果有高亮按钮且表单区为空（或未渲染），自动触发点击
        if (activeBtn && (!formArea || !formArea.firstChild)) {
            activeBtn.click();
        }
    }, 0);
}

// 先检查登录状态，然后根据状态渲染不同的初始内容
async function initializeDashboard(props, nodes) {
    // 创建 fragment
    const frag = document.createDocumentFragment();
    // token 是保存在浏览器中的（如 localStorage），通过 getToken() 获取
    const token = getToken();
    let isLoggedIn = false;
    if (token) {
        try {
            isLoggedIn = await validateToken(token);
            console.log("isLoggedIn:", isLoggedIn)
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
    // 根据登录状态和api_key渲染不同的初始内容;如果未登录，则无api key相关按钮的渲染
    let apiKeyBtnHtml = '';
    if (userinfo && userinfo.api_key) {
        apiKeyBtnHtml = `<button class="login-btn small-btn" id="show-apikey-btn" type="button" style="margin-left:18px;background:#e6fbe6;color:#15803d;border:1px solid #a7f3d0;">API Key已设置</button>`;
    } else if (userinfo) {
        apiKeyBtnHtml = `<button class="login-btn small-btn" id="show-apikey-btn" type="button" style="margin-left:18px;">设置API Key</button>`;
    }
    renderDashboardAuthbar(nodes[1], apiKeyBtnHtml, isLoggedIn, props);

    // 这里定义了主内容区域的HTML结构
    // mainContentHtml 包含一个水平居中的容器（dashboard-horizontal-wrapper），
    // 该容器使用flex布局，使内容在页面中垂直和水平居中，且高度为70%的视口高度
    // 容器内部有两个主要区域：
    // 1. dashboard-content-row：用于后续插入左侧的功能按钮和表单区
    // 2. agent-result-area：用于显示Agent的输出结果，设置了自适应宽度和最小高度
    let mainContentHtml = `
        <main class="dashboard-horizontal-wrapper" style="display:flex;align-items:center;justify-content:center;height:70vh;width:100%;">
            <div class="dashboard-content-row"></div>
            <div id="agent-result-area" style="flex:1;min-width:0;min-height:200px;"></div>
        </main>
    `;
    nodes[0].innerHTML = `${mainContentHtml}`;

    // 为历史按钮单独创建语义化容器
    if (isLoggedIn) {
        // 左上角历史按钮及结果区容器
        const historyBarHtml = `
            <div class="history-btn-bar" style="position:absolute;left:24px;top:24px;z-index:200;display:flex;align-items:flex-start;gap:18px;">
                <button class="login-btn small-btn" id="show-history-btn" style="background:#f3f4f6;color:#2563eb;">显示历史需求</button>
            </div>
        `;
        nodes[2].innerHTML = historyBarHtml;
    }

    nodes.forEach(node => {
        frag.appendChild(node);
    })
    // 这里的 document 是指当前网页的文档对象（Document Object Model, DOM），
    // 它代表了整个页面的结构和内容。通过 document.body.appendChild(historyContainer)，
    // 我们将历史按钮的容器（historyContainer）添加到页面的 <body> 元素中，
    // 这样用户就能在页面上看到这个历史按钮了。
    document.body.appendChild(frag);

    // 渲染dashboard-content-row内容，并在渲染后绑定事件
                setTimeout(() => {
        // 元素类别前加.是因为这是CSS选择器语法，.表示“类选择器”，用于选中具有特定class的元素
        const row = document.querySelector('.dashboard-content-row');
        if (row) {
            row.innerHTML = `
                <nav class="dashboard-actions" style="flex:0 0 180px;max-width:200px;margin:0 0 0 0;">
                    <button class="dashboard-action" data-action="requirement">需求生成Agent</button>
                    <button class="dashboard-action" data-action="coder">代码生成Agent</button>
                    <button class="dashboard-action" data-action="doc">文档生成Agent</button>
                    <button class="dashboard-action" data-action="reviewer">代码审查Agent</button>
                    <button class="dashboard-action" data-action="finalizer">代码整合Agent</button>
                    <button class="dashboard-action" data-action="agent_workflow">Agent Workflow</button>
                </nav>
                <aside id="agent-form-area" style="flex:0 0 380px;max-width:420px;min-height:200px;"></aside>
            `;
        }
        initializeDashboardFeatures(nodes, userinfo, props.onLogout);
        // 新增：绑定历史需求按钮事件
        if (isLoggedIn) {
            const btn = document.querySelector('#show-history-btn');
            if (btn) {
                btn.onclick = function () {
                    window.location.href = 'history.html';
                };
            }
        }
    }, 0);
    // 不要在setTimeout外部再调用initializeDashboardFeatures  
}

// 仪表盘组件（展示用户信息和Agent协作流程）
export function renderDashboard(props = {}) {
    const nodes = [];
    // 创建一个新的 div 元素，作为仪表盘的主容器
    const main_container = document.createElement('main');
    main_container.className = 'dashboard';
    nodes.push(main_container)

    const right_top_header = document.createElement('header')
    right_top_header.className = 'user_status'
    nodes.push(right_top_header)

    const left_top_header = document.createElement('header')
    left_top_header.className = 'history_info'
    nodes.push(left_top_header)

    // 开始初始化
    console.log('Starting dashboard initialization...');
    initializeDashboard(props, nodes).catch(error => {
        console.error('Dashboard initialization failed:', error);
        main_container.innerHTML = '<div style="color: red; padding: 20px;">Dashboard 初始化失败: ' + error.message + '</div>';
    });
    return {
        main: main_container,
        authbar: right_top_header,
        history: left_top_header
    };
}
