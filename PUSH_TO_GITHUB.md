# How to Push This Repo to GitHub

## Step 1: Create the GitHub Repository

1. Go to https://github.com/new
2. Repository name: `chatbots-to-agents-code` (or your preferred name)
3. Description: `Code examples from the "From Chatbots to Agents" series`
4. **Important:** Choose **Public** (so readers can access it)
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Push Your Code

GitHub will show you instructions. Use these commands:

```bash
# Make sure you're in the repo directory
cd /Users/kkannav/Documents/visa-docs/medium-series/posts/series1/chatbots-to-agents-code

# Add the GitHub remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/chatbots-to-agents-code.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify It Worked

Visit: `https://github.com/YOUR-USERNAME/chatbots-to-agents-code`

You should see:
- ✓ README.md displaying
- ✓ part5-build-first-agent/ folder with the agent code
- ✓ Placeholder folders for parts 6-10

## Step 4: Get the URL for Your Articles

Your repo URL will be:
```
https://github.com/YOUR-USERNAME/chatbots-to-agents-code
```

Use this to replace the `(link)` placeholders in:
- `05_build_first_agent/medium.md` (line 301)
- `05_build_first_agent/substack.md`
- `05_build_first_agent/linkedin_newsletter.md`

The specific link for Part 5 code:
```
https://github.com/YOUR-USERNAME/chatbots-to-agents-code/tree/main/part5-build-first-agent
```

## Step 5: Update the README

After pushing, edit the main README.md on GitHub and replace:
```
git clone https://github.com/YOUR-USERNAME/chatbots-to-agents-code.git
```

With your actual GitHub username.

## Troubleshooting

**"remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/chatbots-to-agents-code.git
```

**Authentication issues**
- You may need to use a Personal Access Token instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication

**Push rejected**
```bash
# Make sure you didn't initialize the GitHub repo with any files
# If you did, you'll need to force push (careful!):
git push -u origin main --force
```

## What's Next?

1. Test that the repo is accessible at the GitHub URL
2. Update all `(link)` placeholders in your article files
3. As you publish Parts 6-10, add their code to the corresponding folders
4. Commit and push updates as you go

---

**Pro tip:** After each part is published, commit the new code with:
```bash
git add .
git commit -m "Add Part X: [Title]"
git push
```
