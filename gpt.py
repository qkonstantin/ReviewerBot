import asyncio
import g4f


class GPT:
    def __init__(self, question):
        self.question = question

    async def ask_gpt_async(self) -> str:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.ask_gpt)
        return result

    def ask_gpt(self) -> str:
        return g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_long,
            messages=[{"role": "user", "content": self.question}],
        )
