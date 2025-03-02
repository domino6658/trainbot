import paramiko
import asyncio
from utils import getConfig
config = getConfig.Config()
from discord.ext import commands

async def send(commands, bot: commands.Bot, exit=False):
    host = config.server.host
    port = config.server.port
    username = config.server.username
    password = config.server.password
    
    # Create an SSH client
    ssh = paramiko.SSHClient()
    # Automatically add the server's host key (not recommended for production)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the server
        ssh.connect(host, port, username, password)
        channel = ssh.invoke_shell()
        
        for command in commands:
            print(f"Executing command '{command}'")
            # Send the command
            channel.send(command + '\n')
            
            # Read the output in real-time
            while True:
                if channel.recv_ready():
                    output = channel.recv(1024).decode()
                    print(output, end='')
                    if "appending output to 'nohup.out'" in output or output.endswith('# '):  # Adjust the prompt detection as needed
                        break
                asyncio.sleep(1)
        if exit:
            await bot.close()
    finally:
        # Close the connection
        ssh.close()
