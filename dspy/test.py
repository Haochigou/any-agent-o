import dspy

#  定义并设置大模型
lm = dspy.AzureOpenAI(api_key='e1001104b5ae4d0e81a331d2c2160034',
                      api_base='https://ai-southceus.openai.azure.com',
                      api_version='2024-02-15-preview',
                      model='4o-2')

dspy.settings.configure(lm=lm)

#  定义输入输出参数 类定义方式

class QA(dspy.Signature):
    question = dspy.InputField()
    answer = dspy.OutputField()

question = "what is the color of the sea?"
summarize = dspy.ChainOfThought(QA)
response = summarize(question=question)

print(f"问题：{question} \n答案：{response.answer}")
print(summarize)