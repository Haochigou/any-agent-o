"""支持token、sentence和complete模式的异步迭代器

针对LLM流式返回的tokens，按照指定的方式分割后返回，其中：
1. token：按照模型原始输出的token流，原样返回
2. sentence：按照sentence splitor中定义的字符串进行分句，但当这些符号出现在配对的符号中间时，不进行切分
3. complete：获取所有的模型返回并发挥

    Raises:
        StopAsyncIteration: 迭代器访问结束后抛出

    Returns:
        dict: {'index':0, 'content':'', 'finish_reason':''}
"""

import re


class AIter:
    sentence_splitors = ['。', '!', '！', '?', '？', '\n', '. ', '\n\n', '\\n', '.\"', '}', ']']
    left_matches = ['(', '《', '{', '[', '（']
    right_matches = [')', '》', '}', ']', '）']
    double_quotes = ["\""] # 这里没有计算\'符号，在英文中可能有多种用法
    SENTENCE_CHECK_START_OFFSET = 3
    sentence_splitors_str = '['+ '|'.join(sentence_splitors) + ']'
    def __init__(self, response, stream_mode):
        self._response = response
        self._stream_mode = stream_mode
        self._index = 0
        self._sentence = ""
        self._finish_reason = "stop"        
        self._check_sentence_offset = AIter.SENTENCE_CHECK_START_OFFSET
        self._left_match_cnt = 0
        self._right_match_cnt = 0
        self._double_quotes_cnt = 0
        self._match_check_offset = 0

    def __aiter__(self):
        return self
    
    def __reset_sentence(self, new_sentence = ""):
        self._left_match_cnt = 0
        self._right_match_cnt = 0
        self._match_check_offset = 0
        self._double_quotes_cnt = 0
        self._check_sentence_offset = AIter.SENTENCE_CHECK_START_OFFSET
        self._sentence = new_sentence
    
    def __check_matches(self):
        for left_match in AIter.left_matches:
            self._left_match_cnt += self._sentence[self._match_check_offset:].count(left_match)
        for right_match in AIter.right_matches:
            self._right_match_cnt += self._sentence[self._match_check_offset:].count(right_match)
        
        for q in AIter.double_quotes:
            self._double_quotes_cnt += self._sentence[self._match_check_offset:].count(q)
        
        self._match_check_offset = len(self._sentence)
        
        return (self._right_match_cnt >= self._left_match_cnt) and (self._double_quotes_cnt % 2 == 0)
    
    async def __anext__(self):
        smsg = {'index':self._index, 'content':''}
        self._index += 1
        if self._stream_mode == "complete":
            if self._index > 1:
                raise StopAsyncIteration           
            smsg['content'] = self._response.choices[0].message.content.replace('\n', '\\n').replace('\"', '\\"')
            smsg['finish_reason'] = self._response.choices[0].finish_reason
            return smsg
        else:
            async for chunk in self._response:
                #print(chunk)
                if len(chunk.choices) == 0:
                    continue
                choice = chunk.choices[0]
                self._finish_reason = choice.finish_reason
                if self._stream_mode == "token":
                    smsg['content'] = choice.delta.content
                    smsg['finish_reason'] = choice.finish_reason
                    return smsg
                elif self._stream_mode == "sentence":                    
                    if choice.delta.content is not None:
                        self._sentence += choice.delta.content
                    else:
                        smsg['content'] = None if len(self._sentence) == 0 else self._sentence
                        smsg['finish_reason'] = choice.finish_reason
                        self.__reset_sentence("")                        
                        return smsg
                    #print(f"token:{choice.delta.content}")
                    is_left_right_matched = self.__check_matches()
                    #print(f"sentence:{self._sentence}， offset:{self._check_sentence_offset}, is match:{is_left_right_matched}, left:{self._left_match_cnt}, right:{self._right_match_cnt}, quotes:{self._double_quotes_cnt}")
                    if any(e in self._sentence[self._check_sentence_offset:] for e in AIter.sentence_splitors):
                        if not is_left_right_matched:                            
                            continue
                        else:
                            smsg['finish_reason'] = self._finish_reason
                            if self._sentence[-1] not in AIter.sentence_splitors and self._sentence[-1] not in AIter.double_quotes:
                                segs = re.split(AIter.sentence_splitors_str, self._sentence)
                                smsg['content'] = self._sentence.rstrip(segs[-1]).replace('\n', '\\n').replace('\"', '\\"')  
                                self.__reset_sentence(segs[-1])
                            else:
                                smsg['content'] = self._sentence.replace('\n', '\\n').replace('\"', '\\"')                        
                                self.__reset_sentence("")                        
                            
                            return smsg
                    else:
                        continue    
            raise StopAsyncIteration
