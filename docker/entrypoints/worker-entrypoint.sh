#!/bin/sh

celery -A olxscraper worker -l INFO
