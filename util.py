import praw
import passwords
import calendar, datetime, time

# Version!

version = "0.1"
with_version = lambda msg: msg + "\n\nI'm using Ploverscript v{}. Learn more [here](https://github.com/codingJWilliams/Ploverscript).".format(version)

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

def fetch_post(tor_thread):
    foreign_thread = reddit.submission(url=tor_thread.url)
    # TODO: deal with links to imgur albums -- at least those with a single image
    return dict(
        tor_thread=tor_thread,
        foreign_thread=foreign_thread, 
        content=foreign_thread.url)
