# Local development
stop:
	docker compose stop

down:
	docker compose down

up:
	docker compose up -d

restart:
	docker compose restart

logs:
	docker compose logs server --follow

shell:
	docker compose exec -it server sh

shell_plus:
	docker compose exec -it server python manage.py shell_plus

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
