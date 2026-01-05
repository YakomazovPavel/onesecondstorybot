push:
	git add .
	git commit --allow-empty-message -m ""
	git push origin main
run:
	./.venv/bin/python ./manage.py runserver 0.0.0.0:8000
migrate:
	./.venv/bin/python ./manage.py makemigrations && ./.venv/bin/python ./manage.py migrate