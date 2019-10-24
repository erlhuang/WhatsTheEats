from app import db
from app.models import Listing, Item
import bs4, re

menulistings = ['c9c10.html', 'cowell.html', 'rcc.html', 'crown.html', 'porter.html']

def crawlmenu():
    #have to manually download dining hall menus everyday because
    #dining hall website blocks requests... still looking for better solution
    i = 1
    items = Item.query.all()
    for item in items:
        item.voteup = False
    for menufile in menulistings:
        menuhtml = open(menufile)
        menuSoup = bs4.BeautifulSoup(menuhtml, "html.parser")
        listTitles = menuSoup.find_all('div')
        startPrinting = False
        id = 0
        for items in listTitles:
            #kinda ugly hardcode but it gets the job done
            if(items.getText() == 'Breakfast'):
                startPrinting = True
                continue
            if(items.getText() == 'Lunch'):
                id = 1
                continue
            if(items.getText() == 'Dinner'):
                id = 2
                continue
            if(items.getText() == 'Late Night'):
                id = 3
                continue
            if('Information' in items.getText() or 'information' in items.getText()):
                startPrinting = False
            if(startPrinting and (len(items.getText()) > 3)):
                list = Listing.query.filter_by(id=i).first()
                finditem = list.itemSearch(items.getText())
                if finditem is None:
                #If dh doesnt already have item we must add it to our database
                    newItem = Item(title=items.getText(), voteup=True)
                    list.menu_items.append(newItem)
                else:
                    finditem.voteup = True
        db.session.commit()
        i = i + 1
