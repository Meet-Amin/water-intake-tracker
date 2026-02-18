import os
import textwrap
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.5)


class WaterIntakeAgent:
    def __init__(self):
        self.history = []

    def analyse_intake(self, intake_ml):
        prompt = f"""
               you are a hydration assistant.The user has consumed {intake_ml} ml of water today.
               Provide a hydration status and suggest if they need to drink more water """

        message = HumanMessage(content=prompt)
        response = llm.invoke([message])

        return response.content

    def summarize_history(self, daily_totals, goal_ml):
        if not daily_totals:
            return "No intake history yet. Start logging water to get insights."

        formatted_history = "\n".join(
            f"{date}: {total} ml" for date, total in daily_totals[-7:]
        )

        prompt = textwrap.dedent(
            f"""
            You are a hydration coach. The user has the following recent intake:
            {formatted_history}
            Their daily goal is {goal_ml} ml.
            Provide a short summary that highlights consistency, potential hydration risks, and one tip to stay on track.
            """
        )

        message = HumanMessage(content=prompt)
        response = llm.invoke([message])
        return response.content


if __name__ == "__main__":
    agent = WaterIntakeAgent()
    intake = 1500
    feedback = agent.analyse_intake(intake)
    print(feedback)
