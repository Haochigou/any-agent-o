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

5. 启动项目
  
    进入本项目安装路径/your/deploy/path，执行以下命令启动项目： nohup ./main.sh & 或在tmux中，直接执行 ./main.sh

## 知识库构建

1. 进入项目部署目录 /your/deploy/path

2. 进入python环境，如conda使用 conda activate xxxxx

3. 准备好待构建的知识文件, 路劲如： /your/knowledge/file/path，是QA形式的excel文件，至少包括2列数据，其中一列为“问”，一列为“答”，每组QA为一行

4. 执行构建

    python /your/deploy/path/agent/domain/entities/knowledge_manager.py -f /your/knowledge/file/path -c colloction_name -q "验证查询语句" -t milvus

    例如：

    python agent/domain/entities/knowledge_manager.py -f docs/milian-knowledge.xlsx -c milian_knowledge_v2 -q 水巴巴 -t milvus

    其中-t如果不指定默认构建在本地，指定milvus后，会从/your/deploy/path/agent/config/dbs.yaml中获取milvus链接信息，
    
    验证无误后，配置 /your/deploy/path/agent/config/scene.yaml 文件，修改如下配置：

    ```text
    open_talk:
        humi:
            knowledge:
            -
                name: colloction_name
    ```

    重启应用后知识生效。