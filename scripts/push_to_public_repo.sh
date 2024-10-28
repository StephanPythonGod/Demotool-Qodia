git checkout master
git pull upstream master
git pull origin main --allow-unrelated-histories
git commit
git status
git checkout --orphan new-master
git add .
git commit -m "Initial commit with the latest changes"
git branch -D master
git branch -m master
git push --force upstream master
git branch -D master