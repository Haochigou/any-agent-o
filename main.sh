export ARK_API_BASE=https://ark.cn-beijing.volces.com/api/v3
export ARK_API_KEY=f4fa014c-6bc3-4708-957e-d09b488fdee3
export ALI_API_KEY=sk-17b84805744f4fcb87fe405a18c95bc1
export ALI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
gunicorn agent.main:app -c gunicorn.config.py
