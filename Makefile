# Local development
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

# Utilities
lock:
	uv pip compile pyproject.toml requirements/dev.in -o requirements/dev.txt && \
	uv pip compile pyproject.toml requirements/prod.in -o requirements/prod.txt

managepy:
	python manage.py $(arguments)

# Deployment
prod_build:
	docker build -t olxscraper -f docker/prod.Dockerfile .

prod_tag:
	docker tag olxscraper jkoldun/olxscraper:latest

prod_push:
	docker push jkoldun/olxscraper:latest

deploy: prod_build prod_tag prod_push
