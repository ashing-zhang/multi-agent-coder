// src/components/history.js
async function fetchHistoryMessages() {
    const token = localStorage.getItem('token');
    const contentDiv = document.getElementById('history-content');
    if (!token) {
        contentDiv.innerHTML = "<div style='color:#b91c1c;padding:18px;'>请先登录！</div>";
        return;
    }
    contentDiv.innerHTML = "<div style='padding:18px;'>加载中...</div>";
    try {
        const res = await fetch('/messages/', {
            headers: { 'Authorization': 'Bearer ' + token }
        });
        if (!res.ok) throw new Error('请求失败');
        const data = await res.json();
        if (!Array.isArray(data) || data.length === 0) {
            contentDiv.innerHTML = "<div style='padding:18px;'>暂无历史需求记录</div>";
            return;
        }
        let html = '';
        data.forEach((session, idx) => {
            const sessionId = session.session_id || idx;
            const sessionTitle = session.session_name || session.session_id;
            html += `<div class='history-session' style='margin:18px 0 8px 0;padding:8px 0 0 0;border-top:1px solid #e5e7eb;'>
                <div class='history-session-title' data-session='${sessionId}' style='cursor:pointer;font-weight:600;color:#2563eb;user-select:none;'>
                    ▶ <b>会话：</b>${sessionTitle}
                </div>
                <div class='history-session-messages' id='history-messages-${sessionId}' style='display:none;margin-left:12px;'></div>
            </div>`;
        });
        contentDiv.innerHTML = html;
        // 绑定折叠事件
        data.forEach((session, idx) => {
            const sessionId = session.session_id || idx;
            const titleDiv = contentDiv.querySelector(`.history-session-title[data-session='${sessionId}']`);
            const msgDiv = contentDiv.querySelector(`#history-messages-${sessionId}`);
            if (titleDiv && msgDiv) {
                titleDiv.onclick = function() {
                    if (msgDiv.style.display === 'none') {
                        // 展开
                        msgDiv.style.display = '';
                        titleDiv.innerHTML = `▼ <b>会话：</b>${session.session_name || session.session_id}`;
                        msgDiv.innerHTML = session.messages.map(msg =>
                            `<div style='margin:4px 0 4px 8px;padding:4px 8px;border-radius:6px;background:#f8fafc;'>`
                            + `<span style='color:#2563eb;font-weight:500;'>[${msg.role}]</span> `
                            + `<span style='color:#222;'>${msg.content}</span> `
                            + `<span style='color:#888;font-size:12px;margin-left:8px;'>${msg.created_at ? new Date(msg.created_at).toLocaleString() : ''}</span>`
                            + `</div>`
                        ).join('');
                    } else {
                        // 收起
                        msgDiv.style.display = 'none';
                        titleDiv.innerHTML = `▶ <b>会话：</b>${session.session_name || session.session_id}`;
                        msgDiv.innerHTML = '';
                    }
                };
            }
        });
    } catch (e) {
        contentDiv.innerHTML = `<div style='color:#b91c1c;padding:18px;'>加载历史需求失败：${e.message}</div>`;
    }
}

window.addEventListener('DOMContentLoaded', fetchHistoryMessages); 