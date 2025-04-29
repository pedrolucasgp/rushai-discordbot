import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import google.api_core.exceptions
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.chat import ChatPromptTemplate
import asyncio

load_dotenv()

llm = ChatGoogleGenerativeAI(
    temperature=0.8,
    model="gemini-2.0-flash",
    max_tokens=1000,
    api_key=os.getenv("GEMINI_KEY"),
    timeout=60
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} está online!")

@bot.command(name="ask")
async def ask(ctx, *, message: str):
    async with ctx.channel.typing():

        with open("furia_datalog.md", "r", encoding="utf-8") as f:
            datalog_text = f.read()

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Seu nome é RushAI e você é um especialista em e-sports, mais especificamente sobre a organização chamada Furia.
            Você deve responder as perguntas focando no time de CS2 da Furia, masculino e feminino.
            Você deve responder as perguntas de forma clara e objetiva.
            Você deve usar como fonte principal esse markdown: {datalog_text}. Lembrando de se atentar a data, utilize as informações mais recentes, comparando com a data do prompt.
            Você deve usar informações que não estão no markdown, de sites como HLTV, Liquipedia, Dust2, e redes sociais da Furia.
            Você deve sempre responder em português, mesmo se a pergunta for em inglês.
            Você deve analisar a pergunta e resposta anterior para responder de forma mais precisa a pergunta atual.
            Você deve sempre deve ser politico e amigável, mesmo se a pergunta for ofensiva ou provocativa.
            Você NUNCA deve inventar informações, em hipótese alguma, mesmo se não souber a resposta.
            Você não deve cometer erros de português, mesmo se a pergunta tiver erros de português.
            Você não deve deixar respostas em aberto, ou incompletas, mesmo se a pergunta for aberta ou incompleta.
            """),
            ("user", message)
        ])
        formatted_messages = prompt.format_messages()

        response = await asyncio.to_thread(llm.invoke, formatted_messages)
        await ctx.reply(response.content)

    try:
        pass
    except google.api_core.exceptions.Cancelled as e:
        print(f"Erro de cancelamento na operação: {e}")
        await ctx.reply("A operação foi cancelada. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        await ctx.reply("Desculpe, ocorreu um erro ao tentar processar sua pergunta.")

bot.run(os.getenv("DISCORD_KEY"))