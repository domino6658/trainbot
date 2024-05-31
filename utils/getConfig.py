import os
import yaml

var = 'hello'
def getconfig():
    if not os.path.isfile('config.yml'):
        with open('config.yml','x+') as file:
            file.write('''---

# BOT CONFIG
bot:
  # Discord bot token
  token: 

  # The command prefix for the bot
  command_prefix: 

  # The channel to send startup messages in
  startup_channel_id: 


# PTV API
ptv_api:
  # Dev ID
  dev_id: 

  # Key
  key: 


# RARE SERVICE SEARCHER
rare_service_searcher:
  # Enter the channel ID and role ID for each server
  servers:
    - 
      # Channel ID
      - 
      # Role ID
      - 

    # Add more servers here if you want
    - 
      - 
      - 

    - 
      - 
      - 

  # Enable rare service searcher? (True or False)
  enabled: False
''')
        print('\nA config file (config.yml) has been generated. Please fill out the values in the file and run bot.py again.\n')
        input()
        exit()

    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
    config['rare_service_searcher']['servers'] = [i for i in config['rare_service_searcher']['servers'] if i != [None,None]]
    return config