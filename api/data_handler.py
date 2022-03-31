import json


async def get_input(user_id) -> str:
    with open("data.json", "r") as _:
        data = json.load(_)

        for set in data:
            if set['user_id'] == f"{user_id}":
                return set['content']
        
    return None

async def set_input(user_id, new_content):
    with open("data.json", "r") as _:
        data = json.load(_)

        new_set = {
            "user_id":f"{user_id}",
            "content":new_content
        }

        for set in data:
            if set['user_id'] == f"{user_id}":
                set['content'] = new_content
            
        if new_set not in data:
            data.append(new_set)

    with open("data.json", "w") as _:
        json.dump(obj=data, fp=_, indent=4)