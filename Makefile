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
	docker compose logs web --follow

shell:
	docker compose exec -it web bash

shell_plus:
	docker compose exec -it web python manage.py shell_plus

# Utilities
managepy:
	python manage.py $(arguments)

# Deployment
prod_build:
	docker build -t olxscraper -f deployment/prod.Dockerfile .

prod_tag:
	docker tag olxscraper jkoldun/olxscraper:latest

prod_push:
	docker push jkoldun/olxscraper:latest

prod_sync:
	rsync -av deployment/prod.compose.yaml jarek@34.116.254.111:/home/jarek/compose.yml
	rsync -av deployment/.env jarek@34.116.254.111:/home/jarek/.env

prod_restart:
	ssh jarek@34.116.254.111 "docker compose up --pull always -d"

deploy: prod_build prod_tag prod_push prod_sync prod_restart
