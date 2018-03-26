# Ploverscript
Ploverscript is a lightweight tool to automate the process of transcribing with r/transcribersofreddit. Its usage has been officially endorsed. A Ploverscript user can find posts, claim them, compose transcriptions attending to style guidelines, and submit their work in a streamlined workflow -- no web browser required. The keyboard warrior among us will be pleased to hear that no mouse input is necessary. Here's how it works:

* You start the script, point an image viewer at `data`, and point your favorite text editor at `working.md`. You will be interacting with the text editor and the script's CLI during the transcription process.
* New posts from the TOR subreddit are fetched silently.
* Ploverscript tries to locate the most recent image post in the listing that fulfills certain conditions. These conditions are: to not be claimed by another user, and to not have previously been rejected by the transcriber.
  * If there are no posts meeting the criteria -- (congratulations) -- Ploverscript waits a few seconds and returns to the first step, refreshing the listing.
  * Otherwise, an image is downloaded to `data` and OCR (stolen from `/u/transcribot` or generated locally `tesseract`) is written to `working.md`. Ploverscript reminds you of rules in vigor on subreddit where the content was posted.
* Your image viewer and text editor reload their files. You inspect the image and the OCR you are given to work with. A link to the TOR thread is presented, should you be interested in inspecting anything else.
  * You can decline the transcription by pressing enter. In this case Ploverscript returns to step 3, seeking out the next most recent image.
* To claim the transcription, you write the name of a template (`reddit` for Reddit posts, `facebook` for Facebook shenanigans, `gru_plan` for the "Gru's Plan" meme, etc.) in the `[CLAIM?]` prompt. Ploverscript once again makes sure that the post is not claimed. 
  * If it is, it apologizes and returns to step 3. 
  * If it is not, it writes a fancy "claim" comment for you.
* You reload `working.md`, which now contains a template designed to remind you of proper formatting guidelines. OCR output is included in a convenient location. Crucial elements like the transcription header and footer are ready to go.
* Meanwhile, Ploverscript waits for the automatic comment reply that confirms our responsibility for the post. In the period up to this confirmation -- we call call it"lock limbo" -- Ploverscript won't let us submit our transcription.
  * Infrequently, we will lose a race condition. The script notifies us immediately, edits our "claim" comment in a fancy way, and waits for our crest-fallen confirmation to return to step 3.
  * Otherwise, the script notifies us of our confirmation. Pressing return at the `[SUBMIT?]` prompt submits `working.md` (remember to save it!) as a post on the foreign thread and finalizes our work a fancy "done" comment. A link to the thread is generated, should we want to review. We return to the first step, refreshing the listing.

Sounds good? Here's what you need to get started:

* A Unix-like shell. We've been working on Linux, but Windows and OSX support should be trivial additions.
* Some well-chosen version of Python 3.
* An image viewer that automatically reloads its image -- `geeqie` works for this. Alternatively, you can open `data` in your web browser and refresh the tab whenever appropriate.
* A text editor that lets you reload the file from disk easily. Almost anything will do.
* A "Reddit App" registered under your account. The authentication parameters should be written to `.local/share/Ploverscript/auth.json`. [TODO: make this nice.]

Remember to regularly check your work!
