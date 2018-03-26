# Ploverscript
Ploverscript is a lightweight Python script that automates the process of transcribing with r/transcribersofreddit. 

## ⚠️ Warning ⚠️

To use the script you **must** modmail /r/TranscribersOfReddit mods to seek permission. Additionally, you must ensure you stick to the following guidelines:

* You must not *race* to transcribe; don't go so fast you miss things or don't adhere to the guidelines  
* You must follow format guides like a normal transcriber  
* If a post breaks the foreign subreddit's rules (which are *sometimes* displayed before the claim message), you should report it on the foreign sub and the /r/ToR post.

---

A Ploverscript user can find posts, claim them, compose transcriptions attending to style guidelines, and submit their work in a streamlined workflow -- no web browser wrangling required. Here's how it works:

* You start the script, point an image viewer at `data`, and point your favorite text editor at `working.md`. You will be interacting with the text editor and the script's CLI during the transcription process.
* New posts from the TOR subreddit are fetched silently.
* Ploverscript tries to locate the most recent image post in the listing, subject to certain conditions. These conditions are: to not be claimed by another user, and to not have been previously rejected by the transcriber.
  * If there are no such posts -- (congratulations) -- Ploverscript waits a few seconds and returns to the previous step, refreshing the listing.
  * Otherwise, an image is downloaded to `data` and OCR (taken from `/u/transcribot` or generated locally by `tesseract`) is written to `working.md`. Ploverscript reminds you of rules in vigor on subreddit where the content was posted.
* Your image viewer and text editor reload their files. You inspect the image and the OCR you are given to work with.
  * You can decline the transcription by pressing enter. In this case Ploverscript returns to step 3, seeking out the next most recent image. You can also quit with "q" or refresh the listing with "r".
* To claim the transcription, you enter the name of a template (`reddit` for Reddit posts, `facebook` for Facebook shenanigans, `gru_plan` for the "Gru's Plan" meme, etc.) in the `[CLAIM?]` prompt. For a list of all possible templates, check the top-level `template` directory. Ploverscript once again makes sure that the post is not claimed, notifying you and skipping the post if it is.
* You reload `working.md`, which now contains the template you chose. It is designed to remind you of proper formatting guidelines and includes a link to the wiki at the top. (Don't worry about deleting it -- that is done automatically.) OCR output is included in a convenient location. Crucial elements like the transcription header and footer are ready to go.
* Meanwhile, Ploverscript waits for the automatic comment reply that confirms our responsibility for the post. In the period up to this confirmation -- we call call it "lock limbo" -- Ploverscript won't let you submit your transcription.
  * Occasionally, we will lose a race condition. The script notifies us immediately and waits for our crest-fallen confirmation to desist the transcription.
  * Otherwise, the script notifies us of our confirmation. After completing and saving the transcription in `working.md`, pressing return at the `[SUBMIT?]`  prompt posts our work on the foreign thread and finalizes our work with a "done" comment. Remember to always save `working.md` in your editor before submitting.
* Hopefully, another quality transcription has graced Reddit. Ploverscript refreshes the listing and the process begins again.

Sounds good? Here's what you need to get started:

* A Unix-like shell. We've been working on Linux, but Windows and OSX support should be easy.
* Some well-chosen distribution of Python 3 with PRAW installed.
* An image viewer that automatically reloads its image -- geeqie works for this. Alternatively, you can open `data` in your web browser and refresh the tab whenever appropriate, or use `feh` with `feh --scale-down -R 0.2 /path/to/data`
* A text editor that lets you reload the file from disk easily. Almost anything will do.
* A "Reddit App" registered under your account. The authentication parameters should be written in `passwords.py` using the template in `passwords.py.template`.

Remember to regularly review your comment history and messages!

## Bonus Features

Transcriptions you produce with Ploverscript are saved to `archive/`, and the `report.py` CLI lets you query and recall them. This is useful for {re,cross}posts or memes that you have not templated.

Entering a search string will recall a transcription containing it, and entering "Y" will copy the previous search result into `working.md`. 

