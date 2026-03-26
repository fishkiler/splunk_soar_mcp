# GitHub Upload Guide

## Authentication

- **GitHub Account**: fishkiler
- **Email**: jayoung@gmail.com
- **PAT Location Below**: GitHub Personal Access Token in the project:

github:
uname: <your_github_email>
pwd: <your_github_password>

GitHub Token: <description>
github_pat_XXXX...

```
GitHub Token: <description>
github_pat_XXXX...
```

### Required Token Permissions (Fine-Grained PAT)

When creating/updating a token at **GitHub > Settings > Developer settings > Personal access tokens > Fine-grained tokens**:

| Permission | Access | Why |
|---|---|---|
| Administration | Read and write | Create new repos |
| Contents | Read and write | Push code |
| Metadata | Read-only | Required by default |

### gh CLI Location

```
~/.local/bin/gh
```

If not installed, download from https://github.com/cli/cli/releases (use `linux_arm64` build for DGX Spark).

---

## Process: Upload Any Project to GitHub

### 1. Create `.gitignore`

Before initializing git, create a `.gitignore` in the project root. Common excludes:

```gitignore
# Virtual environments
.venv/
venv/
env/

# Secrets
.env
docs/scratch-pad.md

# Python caches
__pycache__/
*.pyc
*.pyo

# Large data / model files
data/
outputs/
adapters/
*.safetensors
*.bin
*.gguf
*.pt
*.pth

# Logs
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Claude Code
.claude/
tasks/
```

Adjust per project — check for large directories with:
```bash
du -sh */ | sort -rh | head -20
```

### 2. Initialize Git

```bash
git init
git branch -m main
git config user.email "jayoung@gmail.com"
git config user.name "jayoung"
```

### 3. Verify and Commit

```bash
# Dry-run to check what gets staged
git add -A --dry-run

# If it looks good, commit
git add -A
git commit -m "Initial commit: <project description>"
```

### 4. Authenticate gh CLI

```bash
echo "<your_pat_token>" | ~/.local/bin/gh auth login --with-token
~/.local/bin/gh auth setup-git
```

### 5. Create Repo and Push

```bash
# Private repo (recommended)
~/.local/bin/gh repo create <repo-name> --private --source=. --push

# Or public
~/.local/bin/gh repo create <repo-name> --public --source=. --push
```

If the repo already exists on GitHub:
```bash
git remote add origin https://github.com/fishkiler/<repo-name>.git
git push -u origin main
```

---

## Quick Reference (All-in-One)

For a project that already has a `.gitignore`:

```bash
git init && git branch -m main
git config user.email "jayoung@gmail.com"
git config user.name "jayoung"
git add -A && git commit -m "Initial commit"
echo "<pat>" | ~/.local/bin/gh auth login --with-token
~/.local/bin/gh auth setup-git
~/.local/bin/gh repo create <repo-name> --private --source=. --push
```
