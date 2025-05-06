import chainlit as cl


@cl.on_chat_start
async def start():
    cl.Message(content="チャットを開始します！").send()

@cl.on_message
async def main(message: cl.Message):
    # ここでAIモデルへの問い合わせや他の処理を行う
    response_content = f"あなたのメッセージ: {message.content}"
    await cl.Message(content=response_content).send()

