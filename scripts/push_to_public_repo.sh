# 1. Checkout the master branch and pull the latest changes.
git checkout master
git pull upstream master
git pull origin main --allow-unrelated-histories

# 2. Create or modify `.gitignore` to specify files/folders to exclude from the public repo.
# For example:
# echo "secret_config.py" >> .gitignore
# echo "private_folder/" >> .gitignore

# 3. Remove unwanted files from Git's tracking based on `.gitignore`.
git rm -r --cached .

# 4. Stage remaining files based on the updated `.gitignore`.
git add .

# 5. Commit changes to apply `.gitignore`.
git commit -m "Update for public repo"

# 6. Create an orphan branch (new-master) to start a clean history.
git checkout --orphan new-master

# 7. Add files from the updated working directory.
git add .
git commit -m "🚀 Ready"

# 8. Delete the old master branch and rename `new-master` to `master`.
git branch -D master
git branch -m master

# 9. Force push the new master branch to the public repo.
git push --force upstream master


# (Optional) Delete local master branch if needed.
git checkout main
git branch -D master
