
import database
from collections import namedtuple


element = namedtuple('adtuple', 'naslov cijena')
element2 = namedtuple('adtuple', 'naslov cijena')
element.naslov = "N"
element.cijena = 100
element2.naslov = "M"
element2.cijena = 200
db = database.Database()
db.update_database("2", (element))
db.update_database("3", (element2))
print db.search_database("2").cijena

