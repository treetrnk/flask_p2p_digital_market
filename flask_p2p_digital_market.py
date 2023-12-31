from app import create_app, db
from app.models import User, Page, Tag, Subscriber, Definition, Link, Product, Record, Comment
from datetime import datetime

app = create_app()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 
            'User': User, 
            'Page': Page, 
            'Tag': Tag, 
            'Subscriber': Subscriber,
            'Definition': Definition,
            'Link': Link,
            'Product': Product,
            'Record': Record,
            'Comment': Comment,
            'install': install,
        }

#@app.before_first_request
#def set_nav():
#    Page.set_nav()
