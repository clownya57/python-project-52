.PHONY: install migrate collectstatic dev render-start build lint

install:
	uv sync

migrate:
	.venv/bin/python manage.py migrate

collectstatic:
	.venv/bin/python manage.py collectstatic --noinput

dev:
	uv run python manage.py runserver

render-start:
	PATH="$(CURDIR)/.venv/bin:$$PATH" gunicorn task_manager.wsgi

build:
	./build.sh

lint:
	uv run ruff check .
