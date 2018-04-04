import praw
import passwords
import calendar, datetime, time

# Version!

version = "0.1"
tag_msg = lambda msg: msg + "\n\nI'm using Ploverscript v{}. Learn more [here](https://github.com/codingJWilliams/Ploverscript).".format(version)

# Formatting stuff.

small_indent = "    | "
big_indent =   "    |    "

def with_status(status, operation):
    print(small_indent + status + "...")
    res = operation()
    print(big_indent + "...done.")
    return res

# Time stuff.

def get_time():
    return calendar.timegm(time.gmtime())

def show_delta(second):
    return datetime.timedelta(seconds=round(second))


# Reddit stuff.

reddit = praw.Reddit(client_id=passwords.client_id,
                     client_secret=passwords.client_secret,
                     password=passwords.password,
                     user_agent=passwords.user_agent,
                     username=passwords.username)

def pull_content(tor_thread):
    foreign_thread = reddit.submission(url=tor_thread.url)
    # TODO: deal with links to imgur albums -- at least those with a single image
    return dict(
        tor_thread=tor_thread,
        foreign_thread=foreign_thread, 
        content=foreign_thread.url)

def pull_transcription(archive_thread):
    submission = pull_content(reddit.submission(url=archive_thread.url))

    # Look for the "done" comment to see if they're using Ploverscript.
    author = None
    script = False
    submission["tor_thread"].comments.replace_more()
    for comment in submission["tor_thread"].comments.list():
        if "done" in comment.body.lower() and comment.author not in ["transcribersofreddit", "transcribot"]:
            if "done" in comment.body.lower():
                author = comment.author
                script = "lock limbo" in comment.body.lower()
                break

    transcription = None
    submission["foreign_thread"].comments.replace_more() # oof
    for comment in submission["foreign_thread"].comments:
        if (not author or comment.author == author) and "*Image Transcription" in comment.body:
            transcription = comment
            break

    if not transcription:
        return None

    submission.update({
        "author": author or transcription.author,
        "script": script,
        "transcription": transcription})
    return submission

