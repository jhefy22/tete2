import discord
import asyncio
import signal
from discord.ext import commands
from datetime import datetime, timedelta
import os  # Importa o módulo os

# Token do seu bot no Discord, agora carregado da variável de ambiente
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuração de usuários e canais
USERS = {
    'Conta1': {
        'usuarios': ["653052855195926541", "1081318747941371955"],  # Substitua pelos IDs reais
        'itens': {
            'armadura': {'inicio': '2024-12-08 23:51:00', 'duracao': 48},  # 48 horas para armadura
            'ferramenta': {'inicio': '2024-12-08 23:51:00', 'duracao': 24},  # 24 horas para ferramenta
        }
    },
    'Conta2': {
        'usuarios': ["927954144193548368", "696005942722166855"],  # Substitua pelos IDs reais
        'itens': {
            'armadura': {'inicio': '2024-12-08 23:54:00', 'duracao': 48},  # 48 horas para armadura
            'ferramenta': {'inicio': '2024-12-08 23:54:00', 'duracao': 24},  # 24 horas para ferramenta
        }
    },
    'Conta3': {
        'usuarios': ["684474497742667786"],  # Substitua pelos IDs reais
        'itens': {
            'armadura': {'inicio': '2024-12-08 23:54:00', 'duracao': 48},  # 48 horas para armadura
            'ferramenta': {'inicio': '2024-12-08 23:54:00', 'duracao': 24},  # 24 horas para ferramenta
        }
    },
}

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True  # Permitir que o bot leia o conteúdo das mensagens
bot = commands.Bot(command_prefix="!", intents=intents)

# Função para calcular o tempo restante e formatar
def time_remaining(start_time, duration):
    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(hours=duration)
    remaining_time = end_time - datetime.now()
    return remaining_time, end_time

# Envio das notificações
async def send_notification(usuarios, item, remaining_time, end_time, channel):
    # Verifica se o tempo restante é menor ou igual a 5 minutos
    if remaining_time <= timedelta(minutes=5):
        remaining_str = f"{remaining_time.seconds//3600}h {(remaining_time.seconds//60)%60}min"
        # Mencionar os usuários com os IDs
        mentioned_users = [f"<@{user_id}>" for user_id in usuarios]  # Usando IDs para mencionar
        await channel.send(f"{', '.join(mentioned_users)}, o item **{item}** iniciado em {end_time.strftime('%d/%m %H:%M')} termina daqui a {remaining_str}!")

# Função principal para gerenciar as contagens e enviar as notificações
async def manage_crafting():
    while True:
        for conta, dados in USERS.items():
            for item, info in dados['itens'].items():
                # Calcular tempo restante
                remaining_time, end_time = time_remaining(info['inicio'], info['duracao'])
                
                # Verifica se a notificação de 5 minutos antes deve ser enviada
                channel = bot.get_channel(1315850750328307753)  # Substitua pelo ID do seu canal
                if channel is not None:  # Verifique se o canal foi encontrado
                    if remaining_time <= timedelta(minutes=5) and remaining_time > timedelta(seconds=0):
                        await send_notification(dados['usuarios'], item, remaining_time, end_time, channel)
                
                # Reinicia o ciclo de contagem quando o item acaba
                if remaining_time <= timedelta(seconds=0):
                    # Reiniciar o item
                    print(f"Item {item} para {conta} terminou! Reiniciando contagem...")
                    USERS[conta]['itens'][item]['inicio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Inicia de novo

        await asyncio.sleep(60)  # Verifica a cada minuto

# Evento quando o bot estiver online
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    channel = bot.get_channel(1315850750328307753)  # Substitua pelo ID do seu canal
    if channel:
        await channel.send("O bot foi iniciado com sucesso e está em funcionamento!")
    await manage_crafting()

# Evento quando o bot se desconectar
@bot.event
async def on_disconnect():
    channel = bot.get_channel(1315850750328307753)  # Substitua pelo ID do seu canal
    if channel:
        await channel.send("O bot foi desconectado!")

# Captura o encerramento do script para enviar a notificação de desligamento
def handle_shutdown(signal, frame):
    channel = bot.get_channel(1315850750328307753)  # Substitua pelo ID do seu canal
    if channel:
        asyncio.run(channel.send("O bot foi desligado manualmente!"))
    bot.loop.stop()

# Configurar o sinal para captura do encerramento do script
signal.signal(signal.SIGINT, handle_shutdown)  # Captura quando o Ctrl+C é pressionado no terminal

# Rodar o bot
bot.run(TOKEN)
