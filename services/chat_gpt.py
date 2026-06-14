from openai import AsyncOpenAI

class ChatGptService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key = api_key)
        self.messages = []

    async def send_message(self) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            max_tokens=1000,
            temperature=0.9,
        )
        message = response.choices[0].message
        self.messages.append({"role": message.role, "content": message.content})
        return message.content

    def set_prompt(self, prompt: str) -> None:
        self.messages.clear()
        self.messages.append({"role": "system", "content": prompt})

    async def add_message(self, messsage_text: str) -> str:
        self.messages.append({"role": "user", "content": messsage_text})
        return await self.send_message()

    async def send_question(self, prompt: str, message_text: str) -> str:
        self.messages.clear()
        self.messages.append({"role": "system", "content": prompt})
        self.messages.append({"role": "user", "content": message_text})
        return await self.send_message()



