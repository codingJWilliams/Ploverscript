from util import *
import glob
import os, webbrowser
import ast, json

# Invalidate `data` by writing over it with a "no content loaded" image.
def forget_image():
    os.system("cp resources/nocontent.png data")

def wait_lock(comment):
    while True:
        for reply in comment.replies:
            return "The post is yours!" in reply.body
        time.sleep(2)
        comment.refresh()

def with_state(name, default, app):
    os.system("mkdir -p ./tmp")
    path = "tmp/" + name
    if os.path.isfile(path):
        with open(path, "r") as f:
            state = ast.literal_eval(f.read())
    else:
        state = default

    app(state)

    with open(path, "w") as f:
        f.write(str(state))

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
    def is_fresh(thing):
        was_seen = thing in already_seen 
        already_seen[thing] = 1
        return not was_seen

    print("\nRefreshing TOR listing...")
    for tor_thread in reddit.subreddit('transcribersofreddit').new(limit=100):
        if not is_fresh(tor_thread.id):
            continue

        # Scan the TOR thread for availability and transcribot.
        print("\n[0. START]")
        def scan():
            if not thread_ok(tor_thread):
                return (False, None)
            transcribot = get_transcribot(tor_thread) 
            return (True, transcribot)
        available, transcribot = with_status("Scanning {}".format(tor_thread.shortlink), scan)
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
        links = with_status("Fetching content", fetch)
        if not links:
            forget_image()
            continue

        if transcribot:
            with open("tmp/ocr.txt", "w") as f:
                f.write(transcribot)
        else:
            with_status("Running tesseract", lambda: os.system("tesseract data tmp/ocr &> /dev/null"))
        write_template("none")
        foreign_subreddit = links['foreign_thread'].subreddit.display_name

        # Get information and rules.
        print(small_indent + 'Post is {} from /r/{}.'.format(
            links['foreign_thread'].shortlink,  
            foreign_subreddit))
        notable_rules = json.loads(open("resources/notable_rules.json").read())
        rules = notable_rules.get(foreign_subreddit)
        if rules:
            print(small_indent + "Rules in vigor:")
            print("\n".join(map((big_indent + "- {}").format, rules)).rstrip())

        # Prompt for claim.
        resp = input("[1. CLAIM?] ").rstrip()
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
            claim_msg = None
            claim_msg = "Claiming post {}.".format(tor_thread.id)
            print((big_indent + '"{}"').format(claim_msg))
            return start_time, claim_msg, tor_thread.reply(tag_msg(claim_msg))
        claim_result = with_status("Claiming", lambda: claim(tor_thread)) 
        if not claim_result:
            forget_image()
            continue
        start_time, claim_msg, claim_comment = claim_result
        if not with_status("Waiting for lock", lambda: wait_lock(claim_comment)):
            lost_msg = "Race condition lost after {} spent in lock limbo.".format(
                    show_delta(get_time() - start_time))
            print((big_indent + '"{}"').format(lost_msg))
            claim_comment.edit("~~{}~~\n{}".format(claim_msg, lost_msg))
            input("[DESIST!] ")
            forget_image()
            continue
        locked_time = get_time()

        # Submit and register our work.
        input("[2. SUBMIT?] ")
        def submit():
            transcription = open("working.md", "r").read()
            if transcription.startswith("REFER"):
                transcription = "\n".join(transcription.split("\n")[1:])
            os.system("mkdir -p archive")
            open("archive/{}".format(tor_thread.id), "w").write(transcription)
            links['submit'](transcription)
            done_msg = "Done with {} after {} ({} spent in lock limbo).".format(
                    tor_thread.id, 
                    show_delta(get_time() - start_time),
                    show_delta(locked_time - start_time))
            print((small_indent + '"{}"').format(done_msg))
            tor_thread.reply(tag_msg(done_msg)) 
        with_status("Submitting transcription", submit)
        print("[3. DONE]")
        claim_comment.delete()
        forget_image()
        return 2

    return 1

if __name__ == "__main__":
    print("Starting Ploverscript v{}.".format(version))

    def app(already_seen):
        while True:
            res = transcribe_something(already_seen)
            if res == 0:
                return
            if res == 1:
                print("Waiting for fresh content...")
                sleep(5)

    forget_image()
    with_state("seen", {}, app)
