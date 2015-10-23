#!/bin/bash

touch .nojekyll
echo "$GH_CNAME" > CNAME

git init
git config user.email "$GH_USER_EMAIL"
git config user.name "$GH_USER_NAME"
git add -A .
git commit -a -m "Travis #$TRAVIS_BUILD_NUMBER"
git remote add origin https://${GH_TOKEN}@github.com/$GH_USER_LOGIN/$GH_PUSH_REPO
git push --quiet --force origin master > /dev/null 2>&1
