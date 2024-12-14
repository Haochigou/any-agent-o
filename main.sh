export ARK_API_BASE=https://ark.cn-beijing.volces.com/api/v3
export ARK_API_KEY=7c47ba51-1ec5-445c-8b5d-9c1631c142aa
export ALI_API_KEY=sk-17b84805744f4fcb87fe405a18c95bc1
export ALI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
path=`pwd`
path=$path/logs
export LOG_DIR=$path

gunicorn agent.main:app -c gunicorn.config.py
