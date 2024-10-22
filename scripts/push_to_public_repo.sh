#!/bin/bash

# Define the branch name to be used temporarily
TEMP_BRANCH="temp-upstream-branch"

# Ensure you're on the main branch
git checkout main

# Create a new temporary branch from the current state of main
git checkout -b $TEMP_BRANCH

# Apply file exclusions here (you can either modify `.gitignore`, `.git/info/exclude`, or use `git rm --cached`)
# Example: Use git rm --cached to remove specific files from the commit
# git rm --cached sensitive_file.txt
# git rm --cached large_dataset.csv

# Or modify `.git/info/exclude` to exclude files on this branch only
# echo 'sensitive_file.txt' >> .git/info/exclude
# echo 'large_dataset.csv' >> .git/info/exclude

# Stage all changes except for excluded files
git add .

# Commit the changes
git commit -m "Committing changes for upstream only"

# Push the changes to upstream (main branch)
git push upstream $TEMP_BRANCH:main

# Switch back to the main branch
git checkout main

# Optional: Delete the temporary branch after pushing
git branch -D $TEMP_BRANCH

echo "Changes have been pushed to upstream and the temporary branch has been deleted."
