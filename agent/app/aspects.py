from typing import Awaitable
from typing import Any
from typing import List
from typing import Union
from typing import Callable
from datetime import datetime

import agent.domain as domain
from agent.domain.entities.chat import ChatRequest


def aio_robot_history(chat: Callable[[Any], Awaitable[str]]):
    async def wrapper(this) -> str:
        user = this._chat_request.user
        robot = this._chat_request.robot
        talk = this._chat_request.content
        
        # before
        hs = domain.get_robot_history_manager().get(user=user, robot=robot)
        if talk:
            hs.append({
                "role": "user",
                "time": round(datetime.now().timestamp()),
                "content": talk
            })
            hs.save()
        print(hs._history)
        this._messages.extend(hs.get_context(this._history_len))
        print(this._messages)
        
        # deal
        await this.create_chat()
        await chat(this)

        # after
        if this._full_msg and len(this._full_msg) > 0:
            hs.load()
            hs.append({
                "role": "assistant",
                "time": round(datetime.now().timestamp()),
                "content": this._full_msg
            })
            hs.save()

        return this._full_msg

    return wrapper