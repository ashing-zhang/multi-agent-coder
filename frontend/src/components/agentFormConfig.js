// agentFormConfig.js
// 各 Agent 表单的配置项


export const agentFormConfig = {
    requirement: {
        title: '生成任务的需求文档',
        fields: [
            { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入你想完成的编码任务(任务描述可附件上传)', required: false },
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
    test: {
        title: '为代码生成测试用例',
        fields: [
            { label: '输入', name: 'requirement', type: 'textarea', placeholder: '请输入需要测试的代码', required: true },
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

