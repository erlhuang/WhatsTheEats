from app import db
from app.models import Listing, Item
import bs4, re

def crawlcnine():
    #have to manually download dining hall menus everyday because
    #dining hall website blocks requests... still looking for better solution
    menuhtml = open('c9menu.html')
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
        if('Information' in items.getText()):
            startPrinting = False
        if(startPrinting and (len(items.getText()) > 3)):
            list = Listing.query.filter_by(acronym='c9c10').first()
            finditem = list.itemSearch(items.getText())
            if finditem is None:
                newItem = Item(title=items.getText(), voteup=True)
                list.menu_items.append(newItem)
            else:
                finditem.voteup = True
