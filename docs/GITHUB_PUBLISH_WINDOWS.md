# GitHub publication (manual approval and real authentication required)

This release package does not create a GitHub repository or push commits. Publish only after inspecting code, licensing, and evidence. Suggested independent repository: `freshcanibowl/ai-missy-offline-qvac`.

On your own Windows computer, after reviewing files and running tests:

```powershell
# Requires gh auth login completed with the desired GitHub account.
Set-Location "$env:USERPROFILE\Downloads\AI_Missy_Offline_Build05"
py -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'TESTS_FAILED' }
git init
git checkout -b main
git add README.md core.py server.py package.json .gitignore scripts tests web data docs
# Review exact staged paths before committing:
git diff --cached --name-only
git diff --cached --check
# Only after you have reviewed the staging list:
git commit -m "feat: AI Missy Offline QVAC hackathon MVP"
gh repo create freshcanibowl/ai-missy-offline-qvac --public --source . --remote origin --push
```

If the repository already exists, stop rather than overwrite or force push. Never commit local-evidence, node_modules, SQLite files, or API keys. Do not claim public repo created until `gh repo view` succeeds.
