from fake_useragent import UserAgent

class UserAgentGenerator:
    def __init__(self):
        self.ua = UserAgent()

    def get_random_user_agent(self) -> dict[str, str]:
        return {"User-Agent": self.ua.random}