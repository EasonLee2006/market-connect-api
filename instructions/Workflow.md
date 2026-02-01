# 📜 Market Connect: Git Command Cheat Sheet

### 🟢 1. First Time Setup (Do this once)

*Goal: Connect your laptop to your personal fork (Origin) and the team repo (Upstream).*

1. **Fork** the main repository on GitHub to your own account.
2. **Clone** your personal fork to your computer:
```bash
git clone https://github.com/YOUR_USERNAME/market-connect-api.git
cd market-connect-api

```

3. **Add the Team Repo** as "Upstream":
```bash
# Replace TEAM_URL with the link to the main project repo
git remote add upstream https://github.com/hsnu1562/market-connect-api.git

# Prevent accidental direct pushes to the main repo
git remote set-url --push upstream no_push
```

(replace **TEAM_ORG** with **hsnu_1562**)

4. **Configure Rebase Behavior** (Saves headaches later):
```bash
git config pull.rebase true
```
---

### 🟡 2. Starting a New Task (The "Morning" Routine)

*Goal: Make sure you are starting from the freshest code.*

1. **Go to main and sync with the team:**
```bash
git checkout main
git fetch upstream
git rebase upstream/main
```

*(Translation: "Download the team's latest work and update my local main to match exactly.")*
2. **Create your feature branch:**
```bash
# Naming convention: feature/name-of-task or fix/bug-name
git checkout -b feature/booking-logic
```
---

### 🟠 3. Doing the Work (The "Coding" Loop)

*Goal: Save your progress locally.*

1. **Code, code, code...**
2. **Stage your files:**
```bash
git add .
```

3. **Commit (Save snapshot):**
```bash
git commit -m "Add booking logic to database.py"
```
---

### 🔵 4. Sharing Your Work (The "End of Day" Routine)

*Goal: Update your branch with any new changes from the team, then push.*

1. **The "Safety Sync" (CRITICAL STEP):**
*Before you push, check if friends added code while you were working.*
```bash
git fetch upstream
git rebase upstream/main
```

* *If no conflicts:* Great! Move to step 2.
* *If conflicts:* See the "red zone" below.

2. **Push to YOUR fork:**
```bash
git push origin feature/booking-logic
```

*(Note: If you rebased in step 1 and had previously pushed this branch, you might need to use `git push -f origin feature/booking-logic`)*.
3. **Create Pull Request:**
Go to GitHub and click **"Compare & Pull Request"**.

---

### 🔴 5. The Rescue Zone (When Rebase Fails)

*Scenario: You tried to rebase, and Git screams "CONFLICT".*

Don't panic. This just means you and a friend edited the same line of code.

1. **VS Code is your friend:**
Open the files that are red in your file explorer.
Look for `<<<<<<< HEAD` and `>>>>>>> upstream/main`.
Choose **"Accept Current Change"** (Yours) or **"Accept Incoming Change"** (Theirs), or edit it manually to combine both.
2. **Continue the rebase:**
Once you fixed the files and saved them:
```bash
git add .
git rebase --continue

```

3. **Still stuck? Abort!**
If it's too messy and you want to go back to how it was before you started rebasing:
```bash
git rebase --abort

```
---

### One Final Golden Rule for your Team

**Never work directly on the `main` branch.**
