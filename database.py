from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog import *

engine = create_engine('sqlite:///categoriesitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Categories
category1 = Categories(name="Soccer")

session.add(category1)
session.commit()

category2 = Categories(name="Basketball")

session.add(category2)
session.commit()

category3 = Categories(name="Baseball")

session.add(category3)
session.commit()

category4 = Categories(name="Frisbee")

session.add(category4)
session.commit()

category5 = Categories(name="Snowboarding")

session.add(category5)
session.commit()

category6 = Categories(name="Rock Climbing")

session.add(category6)
session.commit()

category7 = Categories(name="Foosball")

session.add(category7)
session.commit()

category8 = Categories(name="Skating")

session.add(category8)
session.commit()

category9 = Categories(name="Hockey")

session.add(category9)
session.commit()

item1 = Items(title="Stick", description="Stick description",
              category=category9)

session.add(item1)
session.commit()


item2 = Items(title="Goggles", description="Goggles description",
              category=category5)

session.add(item2)
session.commit()

item3 = Items(title="Showboard",
              description="Showboard description", category=category5)

session.add(item3)
session.commit()

item4 = Items(title="Two shinguards",
              description="Two shinguards description", category=category1)

session.add(item4)
session.commit()

item5 = Items(title="Shinguards",
              description="Shinguards description", category=category1)

session.add(item5)
session.commit()

item5 = Items(title="Frisbee",
              description="Frisbee description", category=category4)

session.add(item5)
session.commit()

item6 = Items(title="Bat",
              description="Bat description", category=category3)

session.add(item6)
session.commit()

item7 = Items(title="Jersey",
              description="Jersey description", category=category1)

session.add(item7)
session.commit()

item8 = Items(title="Soccer Cleats",
              description="Soccer Cleats description", category=category1)

session.add(item8)
session.commit()

print("added all items!")
