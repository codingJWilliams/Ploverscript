from util import *
import passwords
import os
import calendar
import html
import time
import datetime

def escape_body(body):
    return html.escape(body).replace(" ", "&nbsp;").replace("\n", "<br>")

def render_transcription(archive_thread, delta):
    pulled = with_status("Pulling transcription", lambda: pull_transcription(archive_thread))
    if not pulled:
        print(small_indent + "Something went wrong!")
        return
    if pulled["transcription"]:
        with open("tor_archive/index.html", "a+") as f:
            f.write('<div class="entry"><code>{}</code><div class="info"><a href="{}">{}</a><a href="{}">view comment</a><div>points: {}</div><div>T - {}</div>{}</div></div>'.format(
                escape_body(pulled["transcription"].body),
                "https://reddit.com/u/" + pulled["author"].name,
                "/u/" + pulled["author"].name,
                "https://reddit.com/" + pulled["transcription"].permalink,
                pulled["transcription"].score,
                show_delta(start - pulled["transcription"].created_utc),
                "<div> Using Ploverscript </div>" if pulled["script"] else ""
            ))

if __name__ == "__main__":
    os.system("cp tor_archive/template.html tor_archive/index.html")
    start = get_time()
    for submission in reddit.subreddit("tor_archive").new(limit=None):
        print(small_indent + submission.shortlink)
        delta = get_time() - submission.created_utc 
        print(small_indent + "Now at: T - {}.".format(show_delta(delta)))
        if delta > 24 * 60 * 60:
            break
        render_transcription(submission, start)

