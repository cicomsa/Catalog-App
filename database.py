#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog import *

engine = create_engine('sqlite:///categoriesitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
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

# Items
item1 = Items(title="Stick", description="Stick description",
              category=category9, user_id='none')

session.add(item1)
session.commit()

item2 = Items(title="Goggles", description="Goggles description",
              category=category5, user_id='none')

session.add(item2)
session.commit()

item3 = Items(title="Showboard",
              description="Showboard description",
              category=category5, user_id='none')

session.add(item3)
session.commit()

item4 = Items(title="Two shinguards",
              description="Two shinguards description",
              category=category1, user_id='none')

session.add(item4)
session.commit()

item5 = Items(title="Shinguards",
              description="Shinguards description",
              category=category1, user_id='none')

session.add(item5)
session.commit()

item5 = Items(title="Frisbee",
              description="Frisbee description",
              category=category4, user_id='none')

session.add(item5)
session.commit()

item6 = Items(title="Bat",
              description="Bat description",
              category=category3, user_id='none')

session.add(item6)
session.commit()

item7 = Items(title="Jersey",
              description="Jersey description",
              category=category1, user_id='none')

session.add(item7)
session.commit()

item8 = Items(title="Soccer Cleats",
              description="Soccer Cleats description",
              category=category1, user_id='none')

session.add(item8)
session.commit()

print("added all items!")
