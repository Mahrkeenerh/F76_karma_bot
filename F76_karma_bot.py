import praw, datetime, sys, json, traceback
from time import sleep

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


def get_user(text):

    for word in text.split():
        if "u/" in word:
            return word.strip()


# load lists
def load():

    global record

    with open("record.json") as json_file:
        record = json.load(json_file)


# save lists
def save():

    global record

    with open("record.json", "w") as json_file:
        json.dump(record, json_file)


print("Starting")
load()


while True:
    try:
        for comment in subreddit.stream.comments():
            comment_time = datetime.datetime.fromtimestamp(comment.created_utc)

            # only check new posts
            if comment_time > start_time:
                lowercase_body = comment.body.lower()

                if "u/" in lowercase_body and "karma" in lowercase_body:
                    user = get_user(lowercase_body)
                    print(comment.author)

                    if user == str(comment.author):
                        continue

                    if user not in record and "karma" in lowercase_body:
                        record[user] = 0

                    if "+karma" in lowercase_body:
                        record[user] += 1
                        comment.reply("You've successfully added karma to %s, they now have: %d karma" % (user, record[user]))
                        save()
                    
                    if "-karma" in lowercase_body:
                        record[user] -= 1
                        comment.reply("You've successfully subtracted karma from %s, they now have: %d karma" % (user, record[user]))
                        save()

                    if "?karma" in lowercase_body:
                        comment.reply("%s has: %d karma" % (user, record[user]))
                        save()

    # An error - sleep and hope it works now
    except:
        print("\n", datetime.datetime.now())
        print("En error occured with comments")
        print(traceback.print_exception(*sys.exc_info()))
        sleep(60)
