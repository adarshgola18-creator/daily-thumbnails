# Daily Thumbnails Automation (Gmail)

One-time setup:
1. Create a free GitHub account (github.com) if you don't have one.
2. Create a new **private** repository, e.g. `daily-thumbnails`.
3. Upload every file/folder in this project to that repo, keeping the same structure
   (`templates/`, `.github/workflows/daily.yml`, `generate.py`, `send_email.py`, `requirements.txt`).
4. Create a Gmail **App Password** (needs 2-Step Verification turned on for the Gmail account):
   myaccount.google.com -> Security -> 2-Step Verification -> App passwords -> generate one
   for "Mail". Copy the 16-character password shown.
5. In your GitHub repo: Settings -> Secrets and variables -> Actions -> New repository secret.
   Add three secrets:
   - `GMAIL_USER` — the Gmail address that will send the mail
   - `GMAIL_APP_PASSWORD` — the 16-character App Password from step 4
   - `TO_ADDRESSES` — who should receive it, comma-separated if more than one
     (e.g. `nupur@company.com,you@gmail.com`)
6. Done. The workflow runs automatically on the schedule set in `daily.yml`
   (edit the `cron` line to change the time — it's in UTC, IST = UTC+5:30).
   You can also trigger it manually anytime from the repo's "Actions" tab ->
   "Daily thumbnails" -> "Run workflow".

The calendar-style third thumbnail is not included yet — it will be added once that
template's automation is finalised.
