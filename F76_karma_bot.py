import praw, datetime, sys, json, traceback
from time import sleep
from threading import Thread

from prawcore import auth

class User():

    def __init__(self):
        self.trade = 100
        self.giveaway = 100
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


# notify all couriers
def notify_couriers(comment, couriers):

    couriers = couriers.split()

    while couriers:
        try:
            reddit.redditor(couriers[0]).message("Courier request", "Hey, " + str(comment.author) + " has requested a courier.\n\nLink to comment: " + comment.permalink + "\n\nIf you decide to take it on, please claim it by commenting under their request.")
            del couriers[0]

        except:
            if "RATELIMIT" in "".join(traceback.format_exception(*sys.exc_info())):
                print("Ratelimit,", len(couriers))
                sleep(60)

            else:
                print("\n", datetime.datetime.now())
                print("En error while posting a dm.")
                print("Courier:", couriers[0])
                print(traceback.print_exception(*sys.exc_info()))
                del couriers[0]


print("Starting")
load()


while True:
    try:
        for comment in subreddit.stream.comments():
            comment_time = datetime.datetime.fromtimestamp(comment.created_utc)

            # only check new posts
            if comment_time > start_time and str(comment.author).lower() != "f76_karma_bot":
                lowercase_body = comment.body.lower()

                x_couriers = "u/Savvy_Untapper u/vZ_Bigboy u/Lopsided-Cry5134"
                p_couriers = "u/astrokurt u/Huey9670 u/Lopsided-Cry5134 u/Pfsone u/Alferio420 https://www.facebook.com/groups/250431486153376/?ref=share"

                if "!courier" in lowercase_body:
                    if "xbox" in lowercase_body:
                        comment.reply("u/" + str(comment.author) + " has requested an xbox courier.\n\nSomebody from this list will message you: " + x_couriers)
                        Thread(target=notify_couriers, args=(comment, x_couriers)).start()

                    if "ps" in lowercase_body:
                        comment.reply("u/" + str(comment.author) + " has requested a ps courier.\n\nSomebody from this list will message you: " + p_couriers)
                        Thread(target=notify_couriers, args=(comment, p_couriers)).start()

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
