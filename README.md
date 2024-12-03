# any-agent-o 介绍

## 概述

本项目是一套agent框架，能够结合领域知识，融合LLM等自然语言模型以及规则进行人机交互的系统。

## 整体结构

## 功能模块

## 未来规划

## 协议

    GPL v2

## 部署

1. 安装系统依赖 sudo apt-get install pkg-config python3-dev default-libmysqlclient-dev build-essential cmake
2. 获取本项目并放置到预定目录下，后续用 /your/deploy/path 表示部署路径
3. 安装python依赖库 

    1）安装anaconda

    2）创建python环境 conda create --name "project-name" python=3.10

    3）安装python依赖 进入本项目的安装路径xxxx，执行以下命令 conda activate project-name pip install -r requirements.txt

4. 部署应用

    1）vim ~/.bashrc,在文件末尾增加以下内容：

       export ALI_API_KEY=your-ali-api-key export ALI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1 
       export ARK_API_KEY=your-ark-api-key export ARK_API_BASE=https://ark.cn-beijing.volces.com/api/v3
       export LOG_DIR=/your/deploy/path/logs

    2）修改数据库配置文件， vim /your/deploy/path/agent/config/dbs.yaml 配置mysql和milvus连接信息

    3）修改应用配置文件， vim /your/deploy/path/gunicorn.config.py 确定启动参数，建议bind和workers配置如下

       bind = '0.0.0.0:7890'#绑定fastapi的端口号
       workers = multiprocessing.cpu_count() * 2 + 1 #并行工作进程数

启动项目 进入本项目安装路径/your/deploy/path，执行以下命令启动项目： nohup ./main.sh & 或在tmux中，直接执行 ./main.sh
