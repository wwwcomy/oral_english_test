git branch --merged | egrep -v "(^\*|master|dev|develop|stage)" | xargs git branch -d

Delete merged branch:
git branch --merged | egrep -v "(^\*|master|main|dev|develop|stage|production)" | xargs git branch -d
