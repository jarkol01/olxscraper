up:
	docker-compose up -d

stop:
	docker-compose stop

down:
	docker-compose down --remove-orphans

rm: stop
	docker-compose rm -f

removevolumes: stop
	docker-compose down -v

lock:
	uv pip compile pyproject.toml requirements/dev.in -o requirements/dev.txt && \
	uv pip compile pyproject.toml requirements/prod.in -o requirements/prod.txt

managepy:
	python manage.py $(arguments)

mypy:
	mypy .
