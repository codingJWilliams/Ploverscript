#!/home/magneticduck/caption/.venv/bin/python
#from noobski_auth import reddit
import praw
import passwords


reddit = praw.Reddit(client_id=passwords.client_id,
                     client_secret=passwords.client_secret,
                     password=passwords.password,
                     user_agent=passwords.user_agent,
                     username=passwords.username)

import glob
import webbrowser
import ast
import os
import time
import calendar
import datetime

small_indent = "  | "

def get_time():
    return calendar.timegm(time.gmtime())

def show_delta(second):
    return datetime.timedelta(seconds=round(second))

# Requires at least one GET.
def pull_links(tor_thread):
    linked = reddit.submission(url=tor_thread.url)
    return dict(
        submit=(lambda x: linked.reply(x)),
        tor_thread=(tor_thread.shortlink),
        foreign_thread=linked.shortlink, 
        content=linked.url)

def with_status(status, operation):
    print(small_indent + status + "...")
    res = operation()
    print(small_indent + "   ...done")
    return res

def wait_lock(comment):
    while True:
        for reply in comment.replies:
            return "The post is yours!" in reply.body
        time.sleep(2)
        comment.refresh()

def with_state(name, app):
    with open(name,'r') as f:
        state = ast.literal_eval(f.read())

    app(state)

    with open(name,'w') as f:
        f.write(str(state))

def is_fresh(thing, already_seen):
    was_seen = thing in already_seen 
    already_seen[thing] = 1
    return not was_seen

def scan_thread(tor_thread):
    if tor_thread.link_flair_text != "Unclaimed":
        return None

    transcribot = None

    tor_thread.comments.replace_more()
    for comment in tor_thread.comments.list():

        if comment.author not in ["transcribersofreddit", "transcribot"]:
            print(small_indent + "  another user is here but the thread is not Claimed!")
            print(small_indent + "  ignoring...")
            return None

    for comment in tor_thread.comments:
        if comment.author == "transcribot":
            print(small_indent + "  found transcribot")
            transcribot = comment.replies[0].body
            transcribot = transcribot[:transcribot.rfind("---\n")]

    return dict(transcribot=transcribot)

def write_template(code):
    with_status('writing "{}" template'.format(code), lambda: 
            os.system("cat template/{} > working.md; echo '___BEGIN OCR___\n' >> working.md; cat tmp/ocr.txt >> working.md; cat footer >> working.md".format(code)))

# Walk through the recent submissions and try to transcribe something. 
# Returns 0 to quit, 1 to wait for new content, 2 to run again immediately.
def transcribe_something(already_seen):
    print(small_indent + "refreshing TOR listing...")
    for tor_thread in reddit.subreddit('transcribersofreddit').new(limit=100):
        if not is_fresh(tor_thread.id, already_seen):
            continue

        print("[START]")

        scan_results = with_status("scanning {}".format(tor_thread.shortlink), lambda: scan_thread(tor_thread)) 

        if not scan_results:
            continue

        # Pull information we need to decide whether to claim.
        links = with_status("pulling links", lambda: pull_links(tor_thread))
        with_status("downloading content", lambda: os.system("wget -q -O data {} > /dev/null".format(links['content'])))

        if scan_results['transcribot']:
            with open("tmp/ocr.txt", "w") as f:
                f.write(scan_results['transcribot'])
        else:
            with_status("running tesseract", lambda: os.system("tesseract data tmp/ocr > /dev/null"))

        write_template("default")
        print(small_indent + "TOR thread is: " + links['tor_thread'])

        resp = input("[CLAIM?] ").rstrip()
        if resp == "q":
            return 0
        if resp.lower() not in map(lambda x: x.split("/")[-1], glob.glob("./template/*")):
            continue
        write_template(resp)

        # Claim and wait for lock and transcriber to finish.
        start_time = get_time()
        claim_msg = "Claiming post {}.".format(tor_thread.id)
        print(small_indent + claim_msg)
        claim_comment = tor_thread.reply(claim_msg)
        time.sleep(1)
        if not with_status("waiting for lock", lambda: wait_lock(claim_comment)):
            lost_msg = "Race condition lost after {} spent in lock limbo.".format(
                    show_delta(get_time() - start_time))
            print(small_indent + lost_msg)
            claim_comment.edit("~~{}~~\n{}".format(claim_comment, lost_msg))
            input("[DESIST!] ")
            continue
        locked_time = get_time()
        input("[SUBMIT?] ")

        # Submit and register our work.
        os.system("cp working.md archive/{}".format(tor_thread.id))
        links['submit'](open('working.md', 'r').read())
        done_msg = "Done with {} after {} ({} spent in lock limbo).".format(
                tor_thread.id, 
                show_delta(get_time() - start_time),
                show_delta(locked_time - start_time))
        print(small_indent + done_msg)
        print(small_indent + "foreign thread is: " + links['foreign_thread'])
        tor_thread.reply(done_msg) 
        claim_comment.delete()
        return 2

    return 1

if __name__ == "__main__":
    def app(already_seen):
        while True:
            res = transcribe_something(already_seen)
            if res == 0:
                return
            if res == 1:
                print(small_indent + "waiting for fresh content...")
                sleep(5)

    with_state("tmp/seen", app)