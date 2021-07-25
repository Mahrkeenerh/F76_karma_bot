import praw, datetime, sys, json, traceback
from time import sleep

from prawcore import auth

class User():

    def __init__(self):
        self.trade = 0
        self.giveaway = 0
        self.up_posts = {}
        self.down_posts = {}

# posts
# post id: [user, user, user]


with open("config.json") as config_file:
    config_json = json.load(config_file)

    userAgent = config_json['userAgent']
    cID = config_json['cID']
    cSC = config_json['cSC']
    userN = config_json['userN']
    userP = config_json['userP']

    reddit = praw.Reddit(user_agent=userAgent, 
        client_id=cID, 
        client_secret=cSC, 
        username=userN, 
        password=userP)

    subreddit = reddit.subreddit(config_json['subreddit'])

start_time = datetime.datetime.now()
record = {}


def get_target(text):

    for word in text.split():
        if "u/" in word:
            return word.strip()


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


print("Starting")
load()


while True:
    try:
        for comment in subreddit.stream.comments():
            comment_time = datetime.datetime.fromtimestamp(comment.created_utc)

            # only check new posts
            if comment_time > start_time:
                lowercase_body = comment.body.lower()

                if "!courier" in lowercase_body:
                    comment.reply("u/" + str(comment.author) + " has requested a courier.\n\nCalling %s ." % ("u/astrokurt u/BrokenSpartan23 u/Davisparker8 u/DunnDunnas u/fast-sparrow u/GODisAWESOME777 u/Huey9670 u/Lopsided-Cry5134 u/NoodleShopKing u/SASCAT666 u/Savvy_Untapper u/silent_neo_27 u/SSD002 u/Themudget u/Viking122584 u/vZ_Bigboy"))

                if "u/" in lowercase_body:
                    target = get_target(lowercase_body)
                    author = "u/" + str(comment.author).lower()
                    post_id = comment.submission.id

                    # Add both users to records
                    if target not in record:
                        record[target] = User()

                    if author not in record:
                        record[author] = User()

                    # User trying to change their own karma
                    if target == author:
                        if "+trade" in lowercase_body or "-trade" in lowercase_body or "+giveaway" in lowercase_body or "-giveaway" in lowercase_body:
                            comment.reply("You can't alter your own karma.")
                            continue

                    # Trying to add karma
                    if "+trade" in lowercase_body or "+giveaway" in lowercase_body:
                        if post_id not in record[author].up_posts:
                            record[author].up_posts[post_id] = []

                        if target in record[author].up_posts[post_id]:
                            comment.reply("You can only add karma to one user under one post once.")
                            continue

                        if "+trade" in lowercase_body:
                            record[target].trade += 1
                        else:
                            record[target].giveaway += 1

                        record[author].up_posts[post_id].append(target)
                        
                        comment.reply("%s has successfully added karma to %s.\n\nThey now have %d trade and %d giveaway karma." % (author, target, record[target].trade, record[target].giveaway))
                        save()
                        continue

                    # Trying to subtract karma
                    if "-trade" in lowercase_body or "-giveaway" in lowercase_body:
                        if post_id not in record[author].down_posts:
                            record[author].down_posts[post_id] = []

                        if target in record[author].down_posts[post_id]:
                            comment.reply("You can only subtract karma from one user under one post once.")
                            continue

                        if "-trade" in lowercase_body:
                            record[target].trade -= 1
                        else:
                            record[target].giveaway -= 1

                        record[author].down_posts[post_id].append(target)
                        
                        comment.reply("%s has successfully subtracted karma from %s.\n\nThey now have %d trade and %d giveaway karma." % (author, target, record[target].trade, record[target].giveaway))
                        save()
                        continue

                    # info karma
                    if "?karma" in lowercase_body:
                        comment.reply("%s has %d trade and %d giveaway karma." % (target, record[target].trade, record[target].giveaway))

    # An error - sleep and hope it works now
    except:
        print("\n", datetime.datetime.now())
        print("En error occured with comments")
        print(traceback.print_exception(*sys.exc_info()))
        sleep(60)
