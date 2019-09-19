from app import create_app, db
from app.models import User, Post, Listing, Item, ListingUserPref, ItemUserPref

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Listing': Listing, 'Item': Item, 'ListingUserPref': ListingUserPref, 'ItemUserPref': ItemUserPref}
