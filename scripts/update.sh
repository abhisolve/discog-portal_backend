#! /bin/sh

pip install -r ../requirements.txt
python ../manage.py migrate
git fetch upstream
git merge upstream/master --ff-only