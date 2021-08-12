import json


class User():

    def __init__(self):
        self.trade = 0
        self.giveaway = 0
        self.up_posts = {}
        self.down_posts = {}


record = {}


# load lists
def load():

    global record

    record = {}

    with open("record.json") as json_file:
        in_dict = json.load(json_file)

        for user in in_dict:
            record[user] = User()
            record[user].trade = in_dict[user][0]
            record[user].giveaway = in_dict[user][1]
            record[user].up_posts = in_dict[user][2]
            record[user].down_posts = in_dict[user][3]


# save lists
def save():

    global record

    out_dict = {user: [record[user].trade, record[user].giveaway, record[user].up_posts, record[user].down_posts] for user in record}

    with open("record.json", "w") as json_file:
        json.dump(out_dict, json_file)


load()

for user_key in record:
    
    user = record[user_key]
    user.trade += 100
    user.giveaway += 100

save()
