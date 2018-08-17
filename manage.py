#!/usr/bin/env python3
# coding=utf-8

import os

import click
from flask_migrate import Migrate, upgrade

from blog import create_app
from blog.models import db, redis, Post, User, Category, Label, PostLabelRef
from blog.celerys.update_tasks import update_posts
from config import config

app = create_app(config[os.getenv('FLASK_ENV') or 'default'])
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        redis=redis,
        Post=Post,
        User=User,
        Category=Category,
        Label=Label,
        PostLabelRef=PostLabelRef,
        **app.celery_apps
    )


@app.cli.command(help="Update all posts.")
@click.option('--dropdb', is_flag=True, help="Drop and rebuild database.")
def deploy(dropdb):
    if dropdb:
        db.drop_all()
        upgrade()
        print("Database is droped and rebuilded.")
    print("---------- Start update. ----------")
    update_posts([], update_all=True)
    print("----------- End update. -----------")


for name, celery_app in app.celery_apps.items():
    if name in globals():
        raise NameError(f"Celery app name '{name}' is repeated.")   # noqa
    globals()[name] = celery_app
