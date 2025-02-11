dev:
	npx nodemon -e "js html py" --exec "poetry run servefs --port 7001 -d files"

auth:
	npx nodemon -e "js html py" --exec "poetry run servefs -b foo:123 -d ./files --port 7001"

reload:
	uvicorn servefs.main:app --port 7001 --reload

format:
	poetry run isort .

shiv:
	echo "Build standalone \"servefs.cli\""
	which shiv || pip install shiv
	shiv servefs -o servefs.cli -e servefs.cli:app
	echo "Successfully created \"servefs.cli\""
