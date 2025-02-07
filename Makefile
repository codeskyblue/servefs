dev:
	npx nodemon -e "js html py" --exec "uvicorn servefs.main:app --port 7001"
