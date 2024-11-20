# any-agent-o 介绍

## 概述

本项目是一套agent框架，能够结合领域知识，融合LLM等自然语言模型以及规则进行人机交互的系统。

## 整体结构

## 功能模块

## 未来规划

## 协议

## 安装步骤

1. 安装系统依赖
   sudo apt-get install pkg-config python3-dev default-libmysqlclient-dev build-essential cmake
2. 获取本项目并放置到预定目录下，如xxxx
3. 安装python依赖库
   1）安装anaconda
   2）创建python环境
      conda create --name "project-name" python=3.10
      vim ~/.bashrc,在文件末尾增加以下内容：
      export ALI_API_KEY=your-ali-api-key
      export ALI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
      export ARK_API_KEY=your-ark-api-key
      export ARK_API_BASE=https://ark.cn-beijing.volces.com/api/v3
   3）安装python依赖 
      进入本项目的安装路径xxxx，执行以下命令
      conda activate project-name
      pip install -r requirements.txt 
4. 启动项目
   进入本项目安装路径xxxx，执行以下命令启动项目：
   ./main.sh 或
   bash ./main.sh