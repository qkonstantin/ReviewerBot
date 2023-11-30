import g4f


class GPT:
    def __init__(self, question):
        self.question = question

    def ask_gpt(self) -> str:
        return g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_long,
            messages=[{"role": "user", "content": self.question}],
        )
