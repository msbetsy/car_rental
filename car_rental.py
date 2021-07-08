import os
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db)


if __name__ == '__main__':
    app.run()
