# Git & GitHub, from zero — for this project

You don't need to understand git deeply to use it. You need to understand
five commands and one idea. Read this once, then just follow the numbered
steps below in order.

## The one idea

Git tracks changes to files in a folder, over time, on your own computer.
GitHub is a website that stores a copy of that history online, so:
(a) you don't lose it if your laptop dies, and
(b) anyone (an admissions reader, an interviewer) can open a link and see
your actual commit history — dates, messages, what changed when. That
history is itself evidence you built this over months, which is the whole
point of doing this properly instead of zipping a folder at the end.

---

## Step 0 — Install git (one-time, do this first)

Check if you already have it:

```
git --version
```

If that prints a version number, skip to Step 1. If it errors:

- **Windows:** download and install from https://git-scm.com/downloads
  (click through the installer with default options — you don't need to
  change anything).
- **Mac:** open Terminal and run `git --version` — macOS will usually
  prompt you to install developer tools automatically. Say yes.
- **Linux:** `sudo apt install git` (Ubuntu/Debian) or equivalent for
  your distro.

Restart your terminal after installing, then confirm `git --version` works.

## Step 1 — Tell git who you are (one-time)

```
git config --global user.name "Your Name"
git config --global user.email "the-email-you'll-use-for-github@example.com"
```

This just labels your commits — it's not a login, and it doesn't need to
match anything yet.

## Step 2 — Create a GitHub account

Go to https://github.com and sign up. Free tier is all you need. Pick a
username you don't mind an admissions committee seeing — it'll be visible
in the repo URL.

## Step 3 — Create the empty repository on GitHub

1. Once logged in, click the **+** icon top-right → **New repository**.
2. Name it something like `dota-regional-rating`.
3. Set it to **Public** (a private repo shows no history to anyone viewing
   your profile — defeats the purpose here).
4. **Do NOT** check "Add a README" — you already have one locally, and
   letting GitHub create one too causes a conflict you'd have to resolve
   immediately as a beginner. Leave all the checkboxes unchecked.
5. Click **Create repository**. You'll land on a page with setup
   instructions and a URL that looks like:
   `https://github.com/your-username/dota-regional-rating.git`
   Copy that URL — you need it in Step 5.

## Step 4 — Point your local folder at git (you already did this once)

The `pull_matches.py` folder I gave you already has git initialized with
one commit inside it. On your own machine, unzip it, `cd` into it, and confirm:

```
cd dota-regional-rating
git log --oneline
```

You should see one commit: `Week 1: pre-registered claim, repo scaffold...`
If you see that, git is already tracking this folder — you don't need to
run `git init` again.

## Step 5 — Connect your local folder to the GitHub repo you made

```
git remote add origin https://github.com/your-username/dota-regional-rating.git
git branch -M main
git push -u origin main
```

- Line 1: tells your local folder "the online copy lives at this URL,
  call it `origin`."
- Line 2: makes sure your main branch is named `main` (GitHub's default).
- Line 3: uploads your commit history to GitHub. The `-u` links `main`
  locally to `main` on GitHub so future pushes are just `git push`.

**First time pushing, GitHub will ask you to authenticate.** Password
login for git operations is disabled on GitHub now — it'll prompt you to
either log in via browser popup, or you'll need a **Personal Access
Token** instead of your password. If it asks for a token: GitHub Settings
→ Developer settings → Personal access tokens → generate one, give it
`repo` scope, and paste it in place of a password when prompted. Save that
token somewhere, you won't see it again.

Refresh the GitHub page — your files should now be there.

## Step 6 — Your actual weekly workflow from here on

Every time you make progress — a script works, you fix a bug, you add a
finding to the research log — do this three-step routine:

```
git add -A
git commit -m "short description of what changed"
git push
```

- `git add -A` stages every change in the folder.
- `git commit -m "..."` saves a snapshot with a message. Write real
  messages — "fix cluster mapping bug" not "update" — because these
  messages are part of what makes the history legible to someone reading
  it later.
- `git push` uploads that snapshot to GitHub.

Do this **often** — after every real session, not just at the end of the
project. A commit history with one entry per week for 4 months is
believable evidence of sustained work. A history with two commits, one at
the start and one the day before a deadline, reads exactly like what it is.

## A mistake to avoid

Don't wait until something is "finished" to commit it. Commit broken code,
half-working scripts, messy notebook experiments — that's normal and it's
what a real research process looks like. The commit history is supposed
to show iteration, not just a polished final state.

## Checking it worked

Once pushed, go to `https://github.com/your-username/dota-regional-rating`
in a browser. You should see your README rendered on the page, your
folder structure, and — if you click "commits" — your commit history with
real timestamps. That page is what you'll eventually link in an
application or send to anyone asking about this project.
