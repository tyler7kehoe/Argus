import json


async def get_input(guild_id, user_id) -> str:
    with open("data/data.json", "r") as _:
        data = json.load(_)

        for set in data:
            if set['guild_id'] == guild_id:
                for item in set['wallets']:
                    if item['user_id'] == f"{user_id}":
                        return item['content']

    return None


async def set_input(guild_id, user_id, new_content):
    with open("data/data.json", "r") as _:
        data = json.load(_)

        new_set = {
            'guild_id': guild_id,
            'wallets': [{
                "user_id": f"{user_id}",
                "content": new_content
            }]
        }
        found = False
        found_user = False
        for set in data:
            if set['guild_id'] == guild_id:
                found = True
                for item in set['wallets']:
                    if item['user_id'] == f"{user_id}":
                        item['content'] = new_content
                        found_user = True
                if not found_user:
                    set['wallets'].append({'user_id': f'{user_id}', 'content': new_content})

        if not found:
            data.append(new_set)

    with open("data/data.json", "w") as _:
        json.dump(obj=data, fp=_, indent=4)