from app import create_app, db
from app.models import User, Alias, Listing, Product, Order #, install
from datetime import datetime

app = create_app()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 
            'User': User, 
            'Alias': Alias, 
            'Listing': Listing, 
            'Product': Product,
            'Order': Order,
            #'install': install,
        }

#@app.before_first_request
#def set_nav():
#    Page.set_nav()
