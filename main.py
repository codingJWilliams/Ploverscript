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
import time, json
import calendar
import datetime

small_indent = "   | "
big_indent =   "   |   "

def get_time():
    return calendar.timegm(time.gmtime())

def show_delta(second):
    return datetime.timedelta(seconds=round(second))

# Requires at least one GET.
def pull_links(tor_thread):
    linked = reddit.submission(url=tor_thread.url)
    return dict(
        submit=(lambda x: linked.reply(x)),
        tor_thread=tor_thread,
        foreign_thread=linked, 
        content=linked.url)

def with_status(status, operation):
    print(small_indent + status + "...")
    res = operation()
    print(big_indent + "...done")
    return res

def forget_image():
    os.system("cp resources/nocontent.png data")

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

def thread_ok(tor_thread):
    if tor_thread.link_flair_text != "Unclaimed":
        print(big_indent + "Thread is not unclaimed.")
        return False

    tor_thread.comments.replace_more()
    for comment in tor_thread.comments.list():
        if comment.author not in ["transcribersofreddit", "transcribot"]:
            print(big_indent + "Thread is unclaimed, but another user is already here. Avoiding.")
            return False

    return True

def get_transcribot(tor_thread):
    transcribot = None

    for comment in tor_thread.comments:
        if comment.author == "transcribot":
            if len(comment.replies) >= 1:
                transcribot = comment.replies[0].body
                transcribot = transcribot[:transcribot.rfind("---\n")]
                print(big_indent + "Found transcribot!")
                break

    return transcribot

def write_template(code):
    os.system("cat template/{} > working.md; echo '___BEGIN OCR___\n' >> working.md; cat tmp/ocr.txt >> working.md; cat footer >> working.md".format(code))

# Walk through the recent submissions and try to transcribe something. 
# Returns 0 to quit, 1 to wait for new content, 2 to run again immediately.
def transcribe_something(already_seen):
    print(small_indent + "refreshing TOR listing...")
    for tor_thread in reddit.subreddit('transcribersofreddit').new(limit=100):
        if not is_fresh(tor_thread.id, already_seen):
            continue

        # Scan the TOR thread for availability and transcribot.
        print("[START]")
        def scan():
            if not thread_ok(tor_thread):
                return (False, None)
            transcribot = get_transcribot(tor_thread) 
            return (True, transcribot)
        available, transcribot = with_status("scanning {}".format(tor_thread.shortlink), scan)
        if not available: 
            continue

        # Fetch the post.
        def fetch():
            links = pull_links(tor_thread)
            os.system("wget -q -O data {} > /dev/null".format(links['content']))
            if os.WEXITSTATUS(os.system("identify data &> /dev/null")):
                print(big_indent + "Content is not an image.")
                return None
            return links
        links = with_status("fetching content", fetch)
        if not links:
            forget_image()
            continue

        if transcribot:
            with open("tmp/ocr.txt", "w") as f:
                f.write(transcribot)
        else:
            with_status("running tesseract", lambda: os.system("tesseract data tmp/ocr &> /dev/null"))
        write_template("none")
        foreign_subreddit = links['foreign_thread'].subreddit.display_name

        # Get information and rules.
        print('[{} from /r/{}]'.format(
            links['foreign_thread'].shortlink,  
            foreign_subreddit))
        notable_rules = json.loads(open("notable_rules.json").read())
        rules = notable_rules.get(foreign_subreddit)
        if rules:
            print(small_indent + "rules in vigor:")
            print("\n".join(map((big_indent + "- {}").format, rules)).rstrip())

        # Prompt for claim.
        resp = input("[CLAIM?] ").rstrip()
        if resp == "q":
            forget_image()
            return 0
        if resp == "r":
            forget_image()
            return 2
        if resp.lower() not in map(lambda x: x.split("/")[-1], glob.glob("./template/*")):
            forget_image()
            continue
        write_template(resp)

        # Try to claim. Wait for confirmation to come through.
        def claim(tor_thread):
            tor_thread = reddit.submission(id=tor_thread.id) 
            if not thread_ok(tor_thread):
                input("[DESIST!] ")
                return None
            start_time = get_time()
            claim_msg = "Claiming post {}.".format(tor_thread.id)
            print((big_indent + '"{}"').format(claim_msg))
            return start_time, claim_msg, tor_thread.reply(claim_msg)
        claim_result = with_status("claiming", lambda: claim(tor_thread)) 
        if not claim_result:
            forget_image()
            continue
        start_time, claim_msg, claim_comment = claim_result
        if not with_status("waiting for lock", lambda: wait_lock(claim_comment)):
            lost_msg = "Race condition lost after {} spent in lock limbo.".format(
                    show_delta(get_time() - start_time))
            print((big_indent + '"{}"').format(lost_msg))
            claim_comment.edit("~~{}~~\n{}".format(claim_msg, lost_msg))
            input("[DESIST!] ")
            forget_image()
            continue
        locked_time = get_time()

        # Submit and register our work.
        input("[SUBMIT?] ")
        def submit():
            transcription = open("working.md", "r").read()
            if transcription.startswith("REFER"):
                transcription = "\n".join(transcription.split("\n")[1:])
            os.system("mkdir -p archive")
            open("archive/{}".format(tor_thread.id), "w").write(transcription)
            return links['submit'](transcription)
        foreign_comment = with_status("submitting transcription", submit)
        done_msg = "Done with {} after {} ({} spent in lock limbo).".format(
                tor_thread.id, 
                show_delta(get_time() - start_time),
                show_delta(locked_time - start_time))
        print((small_indent + '"{}"').format(done_msg))
        print("[{} is now transcribed]".format(links['foreign_thread'].shortlink))
        tor_thread.reply(done_msg) 
        claim_comment.delete()
        forget_image()
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

    forget_image()
    with_state("tmp/seen", app)
