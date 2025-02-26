import os
import json

class Config(object):
    def __init__(self):
        
        self.load_config()

    def load_config(self):
        with open('config/config.json') as f:
            self.config = json.load(f)
        if os.name == 'posix':
            level = self.config['bot']['main']
        else:
            level = self.config['bot']['development']
        del self.config['bot']['development']
        del self.config['bot']['main']
        for key, value in level.items():
            self.config['bot'][key] = value
        
        def dict_to_class(obj, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    sub_obj = type(key, (object,), {})
                    setattr(obj, key, dict_to_class(sub_obj, value))
                else:
                    setattr(obj, key, value)
            return obj

        dict_to_class(self, self.config)
        
        del self.config
        
            

# class Dict2Class(object): 
      
#     def __init__(self, my_dict): 
          
#         for key in my_dict: 
#             setattr(self, key, my_dict[key]) 

config = Config()