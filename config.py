import json
import os 

if not os.path.isfile("config.json"):
    constants = {
            'player':{
                'hp': 10,
                'knife': 'ThrowingKnife',
                'level': 1
            }
    
    
    }
    with open("config.json", 'w') as cfg:
        json.dump(constants, cfg, indent=4)
        cfg.seek(0)
        

with open('config.json', 'r') as cfg:
    cfg.seek(0)
    const = json.load(cfg)
    
vals = [f"{key}: {val}" for (key, val) in zip(const.keys(), const.items())]
print(vals)



        

        