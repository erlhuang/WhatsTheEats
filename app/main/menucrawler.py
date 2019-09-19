from app import db
import requests, bs4, re

def crawlcnine():
    givenURL = 'https://nutrition.sa.ucsc.edu/longmenu.aspx?sName=UC+Santa+Cruz+Dining&locationNum=05&locationName=Cowell+Stevenson+Dining+Hall&dtdate=&naFlag=1&WeeksMenus=UCSC+-+This+Week%27s+Menus&mealName='
    res = requests.get(givenURL)
    res.raise_for_status()
