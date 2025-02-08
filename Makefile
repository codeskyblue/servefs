dev:
	npx nodemon -e "js html py" --exec "uvicorn servefs.main:app --port 7001"

reload:
	uvicorn servefs.main:app --port 7001 --reload


format:
	poetry run isort .
