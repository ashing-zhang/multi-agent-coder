// agent_result_area.js

// 创建或获取结果区域
function createResultArea(container, type, label) {
    let resultDiv = container.querySelector(`.${type}-result`);
    if (!resultDiv) {
        resultDiv = document.createElement('div');
        resultDiv.className = `${type}-result`;
        resultDiv.style = 'margin-top:16px; padding:12px; background:#f8f8ff; border-radius:8px; box-shadow:0 1px 4px #eee;';
        container.appendChild(resultDiv);
    }
    resultDiv.innerHTML = `<b>${label}</b>`;
    return resultDiv;
}

// 显示消息提示
function showAgentMessage(container, message, style = {}) {
    let msgDiv = container.querySelector('.agent-message');
    if (!msgDiv) {
        msgDiv = document.createElement('div');
        msgDiv.className = 'agent-message';
        msgDiv.style = 'margin-top:10px;padding:8px 12px;border-radius:6px;font-size:15px;';
        container.appendChild(msgDiv);
    }
    msgDiv.textContent = message;
    Object.assign(msgDiv.style, style);
    return msgDiv;
}

// 实时渲染流式内容
function renderStreamingResult(resultDiv, content) {
    resultDiv.innerHTML = `<pre style='white-space:pre-wrap;word-break:break-all;margin:8px 0 0 0;'>${content}</pre>`;
}

// 保存按钮
function showSaveButton(result, type, agentType, resultArea) {
    let saveBtn = resultArea.querySelector('.agent-save-btn');
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

// ========== 各 Agent 的 onSubmit 处理函数 ========== //

/**
 * 通用的 agent 提交处理函数
 * @param {Object} options
 *   - form: 表单对象
 *   - resultArea: 结果区域 DOM
 *   - userinfo: 用户信息
 *   - streamUrl: 请求的后端流式接口
 *   - resultDivClass: 结果区域的 class 名
 *   - resultDivTitle: 结果区域的标题 HTML
 *   - saveExt: 保存按钮的文件扩展名
 *   - saveName: 保存按钮的文件名前缀
 *   - requireApiKey: 是否需要 API key
 *   - msgText: 处理中提示文本
 *   - msgTextDone: 完成提示文本
 *   - msgTextError: 错误提示文本
 *   - msgTextColor: 处理中提示颜色
 *   - msgTextBg: 处理中提示背景
 *   - msgTextBorder: 处理中提示边框
 *   - msgTextDoneColor: 完成提示颜色
 *   - msgTextDoneBg: 完成提示背景
 *   - msgTextDoneBorder: 完成提示边框
 *   - msgTextErrorColor: 错误提示颜色
 *   - msgTextErrorBg: 错误提示背景
 *   - msgTextErrorBorder: 错误提示边框
 *   - buildRequestBody: (可选) 构造请求体的方法，默认 {requirement}
 */
async function onSubmitAgentGeneric({
    form,
    resultArea,
    streamUrl,
    resultDivClass,
    resultDivTitle,
    saveExt,
    saveName,
    requireApiKey = true,
    msgText = '生成中...',
    msgTextDone = '生成完成，可保存到本地！',
    msgTextError = '流式请求失败，请重试',
    msgTextColor = '#2563eb',
    msgTextBg = '#e6f0ff',
    msgTextBorder = '1px solid #b6d4fe',
    msgTextDoneColor = '#15803d',
    msgTextDoneBg = '#e6fbe6',
    msgTextDoneBorder = '1px solid #a7f3d0',
    msgTextErrorColor = '#b91c1c',
    msgTextErrorBg = '#fee2e2',
    msgTextErrorBorder = '1px solid #fecaca',
    buildRequestBody
}) {
    // 获取需求文本
    const requirement = form.requirement.value.trim();
    if (!requirement) return;
    const area = resultArea;

    // 检查是否有文件输入
    const fileInput = form.querySelector('input[type="file"]');
    let fileContent = null;
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        // 只处理文本文件（如需二进制可扩展）
        try {
            fileContent = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsText(file);
            });
        } catch (e) {
            showAgentMessage(area, '文件读取失败，请重试', {
                background: '#fee2e2', color: '#b91c1c', border: '1px solid #fecaca'
            });
            return;
        }
    }

    // 显示处理中消息，使用传入参数
    const msgDiv = showAgentMessage(area, msgText, {
        background: msgTextBg, color: msgTextColor, border: msgTextBorder
    });

    // 创建结果区域，使用传入参数
    const resultDiv = createResultArea(area, resultDivClass, resultDivTitle);

    try {
        let result = '';
        const token = localStorage.getItem('token');

        // 构造请求体，优先用 buildRequestBody，否则默认 { description: requirement }
        let requestBody = buildRequestBody
            ? buildRequestBody(requirement)
            : { description: requirement };
        // 如果有文件内容，合并到请求体
        if (fileContent !== null) {
            requestBody.fileContent = fileContent;
            // 你也可以根据后端需要，合并到 description 或单独字段
        }

        // 三元表达式​：仅当 token 存在时添加 Authorization 头，避免无效字段
        // await：暂停当前 async 函数执行，等待 fetch 返回的 Promise 完成（不阻塞主线程）
        const res = await fetch(streamUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': 'Bearer ' + token } : {})
            },
            body: JSON.stringify(requestBody)
        });
    
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            result += chunk;
            renderStreamingResult(resultDiv, result);
        }

        // 生成完成，使用传入参数
        msgDiv.textContent = msgTextDone;
        msgDiv.style.background = msgTextDoneBg;
        msgDiv.style.color = msgTextDoneColor;
        msgDiv.style.border = msgTextDoneBorder;

        // 显示保存按钮，使用传入参数
        try {
            showSaveButton(result, saveExt, saveName, area);
        } catch (e) {
            console.error('showSaveButton 执行出错:', e);
        }
    } catch (e) {
        // 错误提示，使用传入参数
        showAgentMessage(area, msgTextError, {
            background: msgTextErrorBg,
            color: msgTextErrorColor,
            border: msgTextErrorBorder
        });
    }
}

// export function 必须在模块最外层作用域，​不可嵌套在代码块（如 if 或函数内）
// ({ description: requirement })：返回一个 ​JavaScript 对象，包含一个 description 属性，其值为传入的 requirement 参数。
// 外层括号 ( ) 是为了避免箭头函数将 { } 解析为代码块而非对象
export async function onSubmitRequirement(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/agent/requirement/stream',
        resultDivClass: 'requirement-analysis',
        resultDivTitle: '需求分析结果：',
        saveExt: 'md',
        saveName: 'requirement',
        requireApiKey: false,
        msgText: '生成中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试',
        buildRequestBody: (requirement) => ({ description: requirement })
    });
}

export async function onSubmitAgentWorkflow(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/workflow/stream',
        resultDivClass: 'workflow-result',
        resultDivTitle: 'Agent Workflow 执行结果：',
        saveExt: 'py',
        saveName: 'agent_workflow',
        requireApiKey: true,
        msgText: 'Workflow执行中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试'
    });
}

export async function onSubmitDoc(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/agent/doc/stream',
        resultDivClass: 'doc-result',
        resultDivTitle: '文档生成结果：',
        saveExt: 'md',
        saveName: 'doc',
        requireApiKey: true,
        msgText: '生成中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试'
    });
}

export async function onSubmitCoder(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/agent/coder/stream',
        resultDivClass: 'coder-result',
        resultDivTitle: '代码生成结果：',
        saveExt: 'py',
        saveName: 'coder',
        requireApiKey: true,
        msgText: '生成中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试'
    });
}

export async function onSubmitReviewer(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/agent/reviewer/stream',
        resultDivClass: 'reviewer-result',
        resultDivTitle: '代码审查结果：',
        saveExt: 'txt',
        saveName: 'reviewer',
        requireApiKey: true,
        msgText: '审查中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试'
    });
}

export async function onSubmitFinalizer(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/agent/finalizer/stream',
        resultDivClass: 'finalizer-result',
        resultDivTitle: '代码整合结果：',
        saveExt: 'py',
        saveName: 'finalizer',
        requireApiKey: true,
        msgText: '整合中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试'
    });
}

export async function onSubmitTest(form, resultArea) {
    return onSubmitAgentGeneric({
        form,
        resultArea,
        streamUrl: '/agent/test/stream',
        resultDivClass: 'test-result',
        resultDivTitle: '测试生成结果：',
        saveExt: 'py',
        saveName: 'test',
        requireApiKey: true,
        msgText: '生成中...',
        msgTextDone: '生成完成，可保存到本地！',
        msgTextError: '流式请求失败，请重试'
    });
}
