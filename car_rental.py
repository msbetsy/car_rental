"""This module initializes application."""
import os
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission, NewsPost, Comment, Car, Rental, Opinion

app = create_app(os.getenv('FLASK_ENV') or 'development')
migrate = Migrate(app, db, render_as_batch=True)


@app.shell_context_processor
def make_shell_context():
    """Creates a shell context that adds the database and app instance and models to the shell session.

    :return: Shell context.
    :rtype: dict
    """
    # return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Car=Car, NewsPost=NewsPost,
    #             Comment=Comment, Rental=Rental, Opinion=Opinion)
    return dict(db=db, User=User, Role=Role, Permission=Permission, Car=Car, NewsPost=NewsPost, Comment=Comment,
                Rental=Rental, Opinion=Opinion)

# if __name__ == '__main__':
#     app.run()
