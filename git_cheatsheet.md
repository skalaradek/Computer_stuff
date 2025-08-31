 # 🧾 Git Cheat Sheet

---

## ⚙️ Basic Git Commands

| **Action**                     | **Command**                                      | **Description**                                      |
|-------------------------------|--------------------------------------------------|------------------------------------------------------|
| 🔧 Initialize Repo            | `git init`                                       | Start a new Git repository                          |
| 📂 Check Status               | `git status`                                     | Show current changes and staging status             |
| ➕ Stage File(s)              | `git add <file>`<br>`git add .`                  | Stage one file or all changes                       |
| ✅ Commit Changes             | `git commit -m "message"`                        | Save staged changes with a message                  |
| 🔗 Add Remote Repo            | `git remote add origin <repo-url>`              | Link local repo to remote (e.g., GitHub)            |
| 🚀 Push to Remote             | `git push -u origin main`                        | Upload commits to remote repo                       |
| ⬇️ Pull from Remote           | `git pull origin main`                          | Fetch and merge changes from remote                 |
| 🌿 Create Branch              | `git checkout -b <branch-name>`                 | Create and switch to a new branch                   |
| 🔄 Switch Branch              | `git checkout <branch-name>`                    | Move to another branch                              |
| 🔀 Merge Branch               | `git merge <branch-name>`                       | Merge another branch into current one               |
| 🧨 View Commit History        | `git log`                                        | See commit history                                  |
| 🔍 View Changes               | `git diff`                                       | Show unstaged changes                               |
| 🚫 Ignore Files               | `.gitignore`                                     | File listing patterns to exclude from tracking      |
| 🧹 Remove File from Staging   | `git reset <file>`                              | Unstage a file                                      |
| 🗑️ Delete Branch              | `git branch -d <branch-name>`                   | Delete a local branch                               |
| 🧠 Clone Repo                 | `git clone <repo-url>`                          | Copy a remote repo locally                          |

---

## ⚔️ Resolving Git Conflicts

| **Step**                      | **Command / Action**                              | **Description**                                      |
|------------------------------|---------------------------------------------------|------------------------------------------------------|
| 🔄 Merge or Pull             | `git merge <branch>`<br>`git pull origin <branch>`| May trigger a conflict                               |
| 📋 Check Conflict Status     | `git status`                                      | Shows which files are conflicted                     |
| 📝 Edit Conflicted Files     | —                                                 | Manually resolve conflict markers (`<<<<<<<`, etc.)  |
| ➕ Stage Resolved Files      | `git add <file>`                                  | Mark conflicts as resolved                           |
| ✅ Commit Merge              | `git commit`                                      | Finalize the merge after resolving conflicts         |
| 🧰 Use Merge Tool (optional) | `git mergetool`                                   | Launch configured merge tool                         |

---

## 🛡️ Conflict Prevention Tips

| **Tip**                        | **Command / Practice**                                      | **Description**                                                                 |
|-------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------------------|
| 🔄 Pull Often                 | `git pull origin main`                                       | Keep your local repo up to date before starting work                           |
| 🌿 Use Feature Branches       | `git checkout -b feature/my-feature`                         | Work on isolated branches instead of `main`                                     |
| 📦 Commit Frequently          | —                                                            | Make small, focused commits to reduce merge complexity                         |
| 🗣️ Communicate with Team      | —                                                            | Coordinate changes to shared files and avoid overlap                           |
| 🚫 Use `.gitignore`           | `.gitignore` file                                            | Prevent tracking of unnecessary or temporary files                             |
| ⚠️ Avoid Simultaneous Edits   | —                                                            | Don’t edit the same lines/files as teammates at the same time                  |
| 🧼 Use Rebase Carefully       | `git fetch origin`<br>`git rebase origin/main`               | Rebase local branches to keep history clean (avoid on shared branches)         |
| 🔍 Review Pull Requests       | GitHub/GitLab interface                                      | Check for conflicts before merging                                              |
| 🤖 Automate with CI/CD        | CI tools (GitHub Actions, GitLab CI, etc.)                   | Automatically test and detect conflicts early                                   |
| 🧰 Use Merge Tools            | `git config --global merge.tool <tool>`<br>`git mergetool`   | Use visual tools to resolve conflicts more easily                              |

