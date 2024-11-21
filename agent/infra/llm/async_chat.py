# -*-coding:utf-8 -*-
'''
AsyncChat调用openai sdk的异步接口，目前支持openai、azure、zhipu、deepseek、qwen渠道的LLM的异步接入
    支持 AIter定义的3种流模式，并统一通过 async for 返回一系列msg信息，每一帧msg格式如下：
    {
        "index":0/1/2/.../N,
        "content":"xxxxx"/None,
        "finish_reason":None/"stop"/... # 遵循模型标准
    }
'''

import os
import asyncio
import time

from openai import AsyncOpenAI
from openai import AsyncAzureOpenAI

from agent.infra.llm.aiter import AIter


class AsyncChat():
    __key_turns = 0
    def __init__(self, channel):
        self._channel = channel
        self._client = None
        self._current_index = 0
        self._repsonse = None
        self.predict = None
        key_list = os.getenv(channel.upper()+"_API_KEY").split(',')
        api_key = key_list[int(AsyncChat.__key_turns % len(key_list))]
        AsyncChat.__key_turns += 1
        base_url = os.getenv(channel.upper()+"_API_BASE")

        if channel == "azure": # azure channel need more configures
            self._client = AsyncAzureOpenAI(
                api_version='2024-02-15-preview',
                azure_endpoint=base_url,
                api_key=api_key,
                #base_url=base_url
            )
        else:
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )

    async def create(self, messages, model, stream_mode="complete", temperature=0.01, top_p=0.5):
        self._model = model
        is_stream = (stream_mode != "complete")
        self._repsonse = await self._client.chat.completions.create(
                messages=messages,
                model=model,
                stream=is_stream,
                temperature=temperature,
                top_p=top_p
            )
        self.predict = AIter(self._repsonse, stream_mode)

async def async_test():
    chat = AsyncChat("ali")
    sentence_split_test_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你好？"},
    ]    
    sentence_scene_messages = [{'content': '# Task\n你是一个标签分类器，请对输入进行标注。\n\n# Attention\n- 可以标注多个标签。\n- 标签最多不超过10个。\n- 输出以json的格式。是一个标签列表。\n- 输出为中文。\n\n# 输入：我脖子上的淋巴结出现了一天，好像用手可以移动，质地有点硬，但我没有发烧。', 'role': 'user'}]
    print(f'---request:{time.time()}')
    #await chat.create(messages=sentence_split_test_messages, model='gpt-4o', stream_mode="sentence")
    await chat.create(messages=sentence_scene_messages, model="Pro/Qwen/Qwen2.5-7B-Instruct", stream_mode="sentence")
    resp = ""
    print(f'---created:{time.time()}')
    async for msg in chat.predict:
        resp += msg["content"] 
        print(f'---piece:{time.time()}')
        print(msg)
    print(f'---finish:{time.time()}')
    print(f"-----full msg:{resp}")

    
if __name__ == "__main__":
    asyncio.run(async_test())