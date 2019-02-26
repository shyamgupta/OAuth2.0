from db_setup import Base, Category, Item,User
# Connect to the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Create a sample user
user1 = User(name="John Doe",email="johndoe@email.com")

# Create Categories
categories = ['Soccer','Basketball','Baseball','Frisbee','Snowboarding','Rock Climbing','Foosball','Skating','Hockey']
for category in categories:
    cat = Category(name=category)
    session.add(cat)
    session.commit()



# Create Items
cat1 = session.query(Category).filter_by(name="Hockey").first()
item1 = Item(name="Stick",description = "A hockey stick is a piece of sport equipment used by the players in all the forms of hockey to move the ball or puck (as appropriate to the type of hockey) either to push, pull, hit, strike, flick, steer, launch or stop the ball/puck during play with the objective being to move the ball/puck around the playing area using the stick.",category=cat1,user=user1)
session.add(item1)
session.commit()

cat2 = session.query(Category).filter_by(name="Snowboarding").first()
item2 = Item(name="Goggles",description="A nice pair of snowboard goggles can be the difference between a fun day on the slopes, and heading in to the lodge early because you cannot see. On stormy days, the snow and cloudy grey skies can blend into one another, making it nearly impossible to see where you are riding. The high contrast design of snowboard goggle lenses can help you see the bumps and obstacles in the snow that might otherwise send you flying or falling. Conversely, on a bright and sunny day, snowboard goggles protect your eyes better than sunglasses due to their full face coverage and dark tint, mirrored lenses. Snowboard goggles are also designed to fit well with snowboard helmets, offering a seamless connection that will keep you warm, protected, and of course, looking good.",category=cat2,user=user1)
session.add(item2)
session.commit()

item3 = Item(name="Snowboard",description="Snowboards are boards where both feet are secured to the same board, which are wider than skis, with the ability to glide on snow.[1] Snowboards widths are between 6 and 12 inches or 15 to 30 centimeters.[2] Snowboards are differentiated from monoskis by the stance of the user.",category=cat2,user=user1)
session.add(item3)
session.commit()


cat3 = session.query(Category).filter_by(name="Soccer").first()
item4 = Item(name="Two shinguards",description="A shin guard or shin pad is a piece of equipment worn on the front of the shin to protect  from injury. These are commonly used in sports including association football, baseball, ice hockey, field hockey, lacrosse, cricket, mountain bike trials, and other sports. This is due to either being required by the rules of the sport or worn voluntarily by the participants for protective measures.",category=cat3,user=user1)
session.add(item4)
session.commit()

item5 = Item(name="Jersey",description="A jersey is an item of knitted clothing, traditionally in wool or cotton, with sleeves, worn as a pullover, as it does not open at the front, unlike a cardigan. It is usually close fitting and machine knitted in contrast to a guernsey that is more often hand knit with a thicker yarn. The word is usually used interchangeably with sweater.[1]The shirts now commonly worn by sports teams as part of the team uniform are also referred to as jersey's, although they bear little resemblance to the original hand knitted woolen garments.",category=cat3,user=user1)
session.add(item5)
session.commit()

cat4 = session.query(Category).filter_by(name="Frisbee").first()
item6 = Item(name="Frisbee",description="A frisbee is a gliding toy or sporting item that is generally plastic and roughly 8 to 10 inches (20 to 25 cm) in diameter with a pronounced lip. It is used recreationally and competitively for throwing and catching, as in flying disc games. The shape of the disc is an airfoil in cross section which allows it to fly by generating lift as it moves through the air. Spinning it imparts a stabilizing gyroscopic force, allowing it to be both aimed and thrown for distance.",category=cat4,user=user1)
session.add(item6)
session.commit()

cat5 = session.query(Category).filter_by(name="Baseball").first()
item7 = Item(name="Bat",description="A baseball bat is a smooth wooden or metal club used in the sport of baseball to hit the ball after it is thrown by the pitcher. By regulation it may be no more than 2.75 inches (7.0 cm) in diameter at the thickest part and no more than 42 inches (1.067 m) in length. Although historically bats approaching 3 pounds (1.4 kg) were swung,[1] today bats of 33 ounces (0.94 kg) are common, topping out at 34 ounces (0.96 kg) to 36 ounces (1.0 kg)",category=cat5,user=user1)
session.add(item7)
session.commit()

print 'Created successfully'


