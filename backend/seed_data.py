"""
Seed script to populate Rebel Trade Network with simulated users
showcasing all current features: profiles, posts, connections, messages
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import bcrypt
import hashlib
import base64
from cryptography.fernet import Fernet
import random

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Encryption setup (same as server.py)
def get_encryption_key():
    key = os.environ.get("ENCRYPTION_KEY", "default-encryption-key-32b!")
    key_bytes = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

fernet = Fernet(get_encryption_key())

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

# Simulated user data representing diverse homesteaders
SEED_USERS = [
    {
        "email": "martha.fields@example.com",
        "password": "homestead123",
        "name": "Martha Fields",
        "location": "Austin, TX",
        "bio": "Third-generation homesteader specializing in heritage poultry and heirloom vegetables. Living off-grid for 15 years.",
        "skills": ["Canning & Preserving", "Seed Saving", "Animal Husbandry", "Cheese Making", "Herbalism"],
        "goods_offering": ["Fresh Eggs", "Heirloom Seeds", "Laying Hens", "Honey", "Jams & Preserves"],
        "goods_wanted": ["Raw Milk", "Beef", "Firewood", "Lumber"],
        "services_offering": ["Canning Workshops", "Homesteading Classes", "One-on-One Training"],
        "services_wanted": ["Tractor Services", "Fence Building"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "jake.blackwood@example.com",
        "password": "homestead123",
        "name": "Jake Blackwood",
        "location": "Austin, TX",
        "bio": "Blacksmith and metalworker. I forge custom tools, knives, and farm equipment. Also raise beef cattle on 50 acres.",
        "skills": ["Blacksmithing", "Welding", "Knife Making", "Carpentry", "Mechanic"],
        "goods_offering": ["Custom Knives", "Beef", "Hand Saws", "Axes", "Hatchets"],
        "goods_wanted": ["Fresh Eggs", "Honey", "Vegetables", "Cheese"],
        "services_offering": ["Custom Metalwork", "Forged Items", "Tool Rental", "Tractor Services"],
        "services_wanted": ["Canning Workshops", "Herbal Consultations"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "sarah.willow@example.com",
        "password": "homestead123",
        "name": "Sarah Willow",
        "location": "Portland, OR",
        "bio": "Herbalist and natural healer. Growing medicinal herbs and making tinctures, salves, and natural remedies for 20 years.",
        "skills": ["Herbalism", "Foraging", "Soap Making", "Candle Making", "First Aid"],
        "goods_offering": ["Herbs & Spices", "Tinctures", "Soaps", "Candles", "Salves"],
        "goods_wanted": ["Beeswax", "Raw Milk", "Wool", "Hides"],
        "services_offering": ["Herbal Consultations", "Natural Health", "Workshops"],
        "services_wanted": ["Shearing", "Leather Working"],
        "is_verified": False,
        "avatar": ""
    },
    {
        "email": "tom.ridgeback@example.com",
        "password": "homestead123",
        "name": "Tom Ridgeback",
        "location": "Denver, CO",
        "bio": "Off-grid solar expert and general contractor. Helping homesteaders achieve energy independence for 12 years.",
        "skills": ["Solar Installation", "Electrical", "Carpentry", "Plumbing", "Generator Repair"],
        "goods_offering": ["Solar Panels", "Batteries", "Inverters", "Lumber", "Building Materials"],
        "goods_wanted": ["Beef", "Pork", "Firewood", "Hay"],
        "services_offering": ["Solar Installation", "Off-Grid Systems", "Electrical", "Consulting"],
        "services_wanted": ["Farm Labor", "Animal Care", "Butchering Services"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "grace.shepherd@example.com",
        "password": "homestead123",
        "name": "Grace Shepherd",
        "location": "Nashville, TN",
        "bio": "Fiber artist raising Angora goats and sheep. Spinning, weaving, and creating beautiful textiles from my own flocks.",
        "skills": ["Spinning", "Weaving", "Knitting", "Dyeing", "Animal Husbandry"],
        "goods_offering": ["Wool", "Yarn", "Knitwear", "Sweaters", "Blankets", "Fiber Goats"],
        "goods_wanted": ["Fresh Vegetables", "Canned Goods", "Tools", "Fencing Materials"],
        "services_offering": ["Fiber Arts Classes", "Shearing", "Custom Clothing"],
        "services_wanted": ["Fence Building", "Barn Chores"],
        "is_verified": False,
        "avatar": ""
    },
    {
        "email": "marcus.stone@example.com",
        "password": "homestead123",
        "name": "Marcus Stone",
        "location": "Austin, TX",
        "bio": "Master woodworker and furniture maker. I build everything from rustic tables to fine cabinetry using reclaimed lumber.",
        "skills": ["Woodworking", "Furniture Making", "Cabinetry", "Carving", "Finish Carpentry"],
        "goods_offering": ["Handmade Furniture", "Cutting Boards", "Wooden Bowls", "Shelves", "Bed Frames"],
        "goods_wanted": ["Leather Goods", "Metalwork", "Fresh Eggs", "Honey"],
        "services_offering": ["Custom Furniture", "Built-to-Order", "Woodworking Classes"],
        "services_wanted": ["Blacksmithing Services", "Leathercraft"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "elena.rivers@example.com",
        "password": "homestead123",
        "name": "Elena Rivers",
        "location": "Portland, OR",
        "bio": "Beekeeper with 50 hives. Producing raw honey, beeswax products, and offering pollination services to local farms.",
        "skills": ["Beekeeping", "Hive Management", "Honey Extraction", "Candle Making", "Herbalism"],
        "goods_offering": ["Honey", "Beeswax", "Beeswax Candles", "Propolis", "Bee Colonies"],
        "goods_wanted": ["Fresh Vegetables", "Fruit Trees", "Berry Bushes", "Seeds"],
        "services_offering": ["Beekeeping Classes", "Hive Inspection", "Pollination Services"],
        "services_wanted": ["Tree Trimming", "Landscaping"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "hank.trapper@example.com",
        "password": "homestead123",
        "name": "Hank Trapper",
        "location": "Denver, CO",
        "bio": "Wilderness survival instructor and hunting guide. Teaching self-reliance skills to those preparing for uncertain times.",
        "skills": ["Hunting", "Trapping", "Wilderness Survival", "Fire Starting", "Marksmanship"],
        "goods_offering": ["Venison", "Rabbit Meat", "Hides", "Fur", "Jerky"],
        "goods_wanted": ["Ammunition", "Camping Gear", "Preserved Foods", "Medical Supplies"],
        "services_offering": ["Survival Skills Training", "Hunting Guide", "Firearms Training"],
        "services_wanted": ["First Aid Training", "Radio Communications"],
        "is_verified": False,
        "avatar": ""
    },
    {
        "email": "lily.greenthumb@example.com",
        "password": "homestead123",
        "name": "Lily Greenthumb",
        "location": "Nashville, TN",
        "bio": "Permaculture designer transforming properties into food forests. Passionate about sustainable living and soil regeneration.",
        "skills": ["Permaculture Design", "Food Forest Design", "Composting", "Vermiculture", "Garden Planning"],
        "goods_offering": ["Plant Starts", "Seedlings", "Compost", "Mulch", "Fruit Trees"],
        "goods_wanted": ["Chicken Manure", "Wood Chips", "Rain Barrels", "Irrigation Supplies"],
        "services_offering": ["Farm Planning", "Consulting", "Permaculture Design", "Garden Maintenance"],
        "services_wanted": ["Heavy Lifting", "Land Clearing"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "ruth.dairy@example.com",
        "password": "homestead123",
        "name": "Ruth Dairyfield",
        "location": "Austin, TX",
        "bio": "Small dairy farmer with Jersey cows. Making artisan cheese, butter, and yogurt. All grass-fed and chemical-free.",
        "skills": ["Cheese Making", "Butter Making", "Yogurt Making", "Milking", "Animal Husbandry"],
        "goods_offering": ["Raw Milk", "Cheese", "Butter", "Yogurt", "Dairy Cows", "Calves"],
        "goods_wanted": ["Hay", "Alfalfa", "Fencing Materials", "Veterinary Supplies"],
        "services_offering": ["Cheese Making Workshops", "Milking Equipment Rental"],
        "services_wanted": ["Veterinary Services", "Fence Repair", "Hay Baling"],
        "is_verified": True,
        "avatar": ""
    },
    {
        "email": "demo@rebeltrade.net",
        "password": "demo123",
        "name": "Demo Trader",
        "location": "Austin, TX",
        "bio": "Demo account to explore Rebel Trade Network features. Feel free to browse around!",
        "skills": ["Homesteading", "Gardening", "Basic Carpentry"],
        "goods_offering": ["Fresh Vegetables", "Herbs"],
        "goods_wanted": ["Tools", "Seeds"],
        "services_offering": ["Garden Help"],
        "services_wanted": ["Advice", "Mentoring"],
        "is_verified": False,
        "avatar": ""
    }
]

# Sample posts showcasing different categories
SEED_POSTS = [
    {
        "user_email": "martha.fields@example.com",
        "title": "Fresh Heritage Chicken Eggs Available",
        "description": "I have surplus eggs from my heritage breed chickens - Ameraucanas (blue eggs), Marans (dark brown), and Barred Rocks. These girls are free-range and fed organic. Looking to trade for raw milk, cheese, or beef. Located in Austin, pickup only.",
        "category": "goods",
        "offering": ["Fresh Eggs", "Laying Hens"],
        "looking_for": ["Raw Milk", "Cheese", "Beef"]
    },
    {
        "user_email": "jake.blackwood@example.com",
        "title": "Custom Forged Tools & Knives",
        "description": "Hand-forged kitchen knives, hunting knives, and farm tools. Each piece is made to order with high-carbon steel. I also repair old tools and can restore antique implements. Will trade for quality meat, eggs, or honey.",
        "category": "services",
        "offering": ["Custom Knives", "Custom Tools", "Forged Items"],
        "looking_for": ["Fresh Eggs", "Honey", "Beef", "Pork"]
    },
    {
        "user_email": "sarah.willow@example.com",
        "title": "Herbal Medicine Workshop - Trade Welcome",
        "description": "Offering my spring workshop series on herbal medicine making. Learn to identify medicinal plants, make tinctures, salves, and teas. Will accept trade for wool, fiber, leather goods, or quality seeds.",
        "category": "services",
        "offering": ["Herbal Consultations", "Workshops", "Natural Health"],
        "looking_for": ["Wool", "Yarn", "Leather Goods", "Seeds"]
    },
    {
        "user_email": "tom.ridgeback@example.com",
        "title": "Off-Grid Solar Installation Services",
        "description": "Complete off-grid solar systems designed and installed. I handle everything from site assessment to final commissioning. Have extra panels and batteries available for trade. Looking for quality meat and firewood.",
        "category": "services",
        "offering": ["Solar Installation", "Off-Grid Systems", "Consulting"],
        "looking_for": ["Beef", "Pork", "Firewood", "Hay"]
    },
    {
        "user_email": "grace.shepherd@example.com",
        "title": "Hand-Spun Yarn & Wool Products",
        "description": "Beautiful yarn from my Angora goats and Merino sheep. Natural and plant-dyed colors available. Also have raw fleece for spinners. Looking to trade for preserved foods, tools, or fencing supplies.",
        "category": "goods",
        "offering": ["Wool", "Yarn", "Knitwear"],
        "looking_for": ["Canned Goods", "Tools", "Fencing Materials"]
    },
    {
        "user_email": "marcus.stone@example.com",
        "title": "Custom Farmhouse Furniture",
        "description": "Building a new farmhouse table? Need a custom cabinet or shelving unit? I work with reclaimed barn wood and sustainably harvested lumber. Each piece is one-of-a-kind. Trade for quality leather goods, metalwork, or farm products.",
        "category": "goods",
        "offering": ["Handmade Furniture", "Cutting Boards", "Custom Woodwork"],
        "looking_for": ["Leather Goods", "Custom Knives", "Fresh Eggs"]
    },
    {
        "user_email": "elena.rivers@example.com",
        "title": "Raw Honey & Bee Supplies",
        "description": "Pure, unfiltered honey from my apiaries. Also have beeswax for candles and cosmetics, and propolis for health products. Can provide nucs and queen bees for aspiring beekeepers. Looking for fruit trees and berry plants.",
        "category": "goods",
        "offering": ["Honey", "Beeswax", "Bee Colonies", "Queen Bees"],
        "looking_for": ["Fruit Trees", "Berry Bushes", "Plant Starts"]
    },
    {
        "user_email": "hank.trapper@example.com",
        "title": "Wilderness Survival Training",
        "description": "Learn to survive and thrive in the wilderness. Courses cover shelter building, fire starting, water procurement, wild edibles, and hunting/trapping. Weekend and week-long intensives available. Trade for preserved foods or medical supplies.",
        "category": "services",
        "offering": ["Survival Skills Training", "Hunting Guide", "Wilderness Classes"],
        "looking_for": ["Canned Goods", "Jerky", "Medical Supplies", "First Aid Training"]
    },
    {
        "user_email": "lily.greenthumb@example.com",
        "title": "Permaculture Design Consultation",
        "description": "Transform your land into a productive food forest! I design sustainable systems that work with nature, not against it. Services include site analysis, water management, and long-term planting plans. Will trade for labor or materials.",
        "category": "services",
        "offering": ["Permaculture Design", "Consulting", "Farm Planning"],
        "looking_for": ["Farm Labor", "Compost", "Mulch", "Rain Barrels"]
    },
    {
        "user_email": "ruth.dairy@example.com",
        "title": "Artisan Raw Milk Cheese",
        "description": "Small-batch aged cheeses from my grass-fed Jersey cows. Cheddar, gouda, and fresh mozzarella available. Also have raw milk, butter, and cream. Looking to trade for quality hay and fencing help.",
        "category": "goods",
        "offering": ["Cheese", "Raw Milk", "Butter", "Yogurt"],
        "looking_for": ["Hay", "Alfalfa", "Fence Building", "Fence Repair"]
    }
]

# Define network connections (bidirectional)
NETWORK_CONNECTIONS = [
    ("martha.fields@example.com", "jake.blackwood@example.com"),
    ("martha.fields@example.com", "marcus.stone@example.com"),
    ("martha.fields@example.com", "ruth.dairy@example.com"),
    ("jake.blackwood@example.com", "marcus.stone@example.com"),
    ("sarah.willow@example.com", "elena.rivers@example.com"),
    ("sarah.willow@example.com", "grace.shepherd@example.com"),
    ("tom.ridgeback@example.com", "hank.trapper@example.com"),
    ("lily.greenthumb@example.com", "elena.rivers@example.com"),
    ("lily.greenthumb@example.com", "ruth.dairy@example.com"),
    ("grace.shepherd@example.com", "ruth.dairy@example.com"),
]

# Sample messages between connected users
SEED_MESSAGES = [
    {
        "from": "jake.blackwood@example.com",
        "to": "martha.fields@example.com",
        "messages": [
            ("jake.blackwood@example.com", "Hey Martha! I saw your post about the heritage eggs. I'd love to trade some of my beef for a few dozen. What do you think?"),
            ("martha.fields@example.com", "Hi Jake! That sounds great. How about 3 dozen eggs for 5 lbs of ground beef?"),
            ("jake.blackwood@example.com", "Deal! Can I swing by Saturday morning?"),
            ("martha.fields@example.com", "Perfect. I'll have them ready. See you around 9am?"),
        ]
    },
    {
        "from": "sarah.willow@example.com",
        "to": "elena.rivers@example.com",
        "messages": [
            ("sarah.willow@example.com", "Elena, I'm running low on beeswax for my salves. Do you have any available?"),
            ("elena.rivers@example.com", "I do! Just processed a bunch. I could use some of your elderberry tincture if you have it."),
            ("sarah.willow@example.com", "I have plenty! How about 2 lbs of beeswax for a quart of elderberry tincture?"),
            ("elena.rivers@example.com", "That works perfectly. I can bring it to the farmers market this weekend."),
        ]
    },
    {
        "from": "tom.ridgeback@example.com",
        "to": "hank.trapper@example.com",
        "messages": [
            ("hank.trapper@example.com", "Tom, thinking about adding solar to my cabin. You got time for a consultation?"),
            ("tom.ridgeback@example.com", "Absolutely! Your place is pretty remote - would be a great off-grid setup. Free this Thursday?"),
            ("hank.trapper@example.com", "Thursday works. I'll have some elk jerky ready as a thank you."),
            ("tom.ridgeback@example.com", "Now that's a trade I can get behind! See you Thursday."),
        ]
    }
]

# Sample comments on posts
SEED_COMMENTS = [
    {
        "post_title": "Fresh Heritage Chicken Eggs Available",
        "comments": [
            ("jake.blackwood@example.com", "Those Maran eggs are beautiful! The dark brown shells are amazing."),
            ("ruth.dairy@example.com", "I'd love to trade some cheese for eggs if you're interested!"),
            ("marcus.stone@example.com", "Do you have any Ameraucanas available for sale? Looking to start a small flock."),
        ]
    },
    {
        "post_title": "Custom Forged Tools & Knives",
        "comments": [
            ("martha.fields@example.com", "Jake's knives are incredible - I use mine daily in the kitchen!"),
            ("tom.ridgeback@example.com", "Can you make a custom hatchet? Need something for kindling."),
        ]
    },
    {
        "post_title": "Raw Honey & Bee Supplies",
        "comments": [
            ("sarah.willow@example.com", "Elena's honey is the best I've ever had. Pure liquid gold!"),
            ("lily.greenthumb@example.com", "Would love to get some nucs this spring. My fruit trees need pollinators."),
        ]
    },
    {
        "post_title": "Artisan Raw Milk Cheese",
        "comments": [
            ("martha.fields@example.com", "Ruth's aged cheddar is life-changing. Seriously."),
            ("grace.shepherd@example.com", "Do you ever make feta? I'd trade yarn for some!"),
        ]
    }
]


async def seed_database():
    """Main seeding function"""
    print("Starting database seed...")
    
    # Create user ID mapping
    user_id_map = {}
    
    # 1. Create users
    print("\n1. Creating users...")
    for user_data in SEED_USERS:
        # Check if user already exists
        existing = await db.users.find_one({"email": user_data["email"]})
        if existing:
            user_id_map[user_data["email"]] = str(existing["_id"])
            print(f"  - User {user_data['name']} already exists")
            continue
        
        user_doc = {
            "email": user_data["email"],
            "password_hash": hash_password(user_data["password"]),
            "name": user_data["name"],
            "location": encrypt_data(user_data["location"]),
            "bio": encrypt_data(user_data["bio"]),
            "skills": user_data["skills"],
            "goods_offering": user_data["goods_offering"],
            "goods_wanted": user_data["goods_wanted"],
            "services_offering": user_data["services_offering"],
            "services_wanted": user_data["services_wanted"],
            "avatar": user_data["avatar"],
            "role": "user",
            "is_verified": user_data["is_verified"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(30, 180))).isoformat()
        }
        result = await db.users.insert_one(user_doc)
        user_id_map[user_data["email"]] = str(result.inserted_id)
        verified_status = " [VERIFIED]" if user_data["is_verified"] else ""
        print(f"  + Created user: {user_data['name']} ({user_data['location']}){verified_status}")
    
    # 2. Create posts
    print("\n2. Creating posts...")
    post_id_map = {}
    for post_data in SEED_POSTS:
        user_id = user_id_map.get(post_data["user_email"])
        if not user_id:
            print(f"  - Skipping post: user {post_data['user_email']} not found")
            continue
        
        # Check if post already exists
        existing = await db.posts.find_one({"user_id": user_id, "title": post_data["title"]})
        if existing:
            post_id_map[post_data["title"]] = str(existing["_id"])
            print(f"  - Post '{post_data['title'][:40]}...' already exists")
            continue
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        post_doc = {
            "user_id": user_id,
            "user_name": user.get("name", "Anonymous"),
            "user_avatar": user.get("avatar", ""),
            "title": post_data["title"],
            "description": encrypt_data(post_data["description"]),
            "category": post_data["category"],
            "offering": post_data["offering"],
            "looking_for": post_data["looking_for"],
            "images": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))).isoformat(),
            "likes": [],
            "comments": []
        }
        result = await db.posts.insert_one(post_doc)
        post_id_map[post_data["title"]] = str(result.inserted_id)
        print(f"  + Created post: '{post_data['title'][:50]}...'")
    
    # 3. Create network connections
    print("\n3. Creating network connections...")
    for email1, email2 in NETWORK_CONNECTIONS:
        user1_id = user_id_map.get(email1)
        user2_id = user_id_map.get(email2)
        
        if not user1_id or not user2_id:
            continue
        
        # Check if connection exists
        existing = await db.network_connections.find_one({
            "$or": [
                {"user_id": user1_id, "connected_user_id": user2_id},
                {"user_id": user2_id, "connected_user_id": user1_id}
            ]
        })
        
        if existing:
            print(f"  - Connection between {email1.split('@')[0]} and {email2.split('@')[0]} exists")
            continue
        
        connection_doc = {
            "user_id": user1_id,
            "connected_user_id": user2_id,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(7, 60))).isoformat()
        }
        await db.network_connections.insert_one(connection_doc)
        print(f"  + Connected: {email1.split('@')[0]} <-> {email2.split('@')[0]}")
    
    # 4. Create messages
    print("\n4. Creating messages...")
    for msg_thread in SEED_MESSAGES:
        for sender_email, content in msg_thread["messages"]:
            sender_id = user_id_map.get(sender_email)
            receiver_email = msg_thread["to"] if sender_email == msg_thread["from"] else msg_thread["from"]
            receiver_id = user_id_map.get(receiver_email)
            
            if not sender_id or not receiver_id:
                continue
            
            # Check if message exists (by content hash)
            existing = await db.messages.find_one({
                "sender_id": sender_id,
                "receiver_id": receiver_id,
            })
            
            if existing:
                continue
            
            msg_doc = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": encrypt_data(content),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14), hours=random.randint(0, 23))).isoformat(),
                "read": random.choice([True, False])
            }
            await db.messages.insert_one(msg_doc)
        
        print(f"  + Created message thread: {msg_thread['from'].split('@')[0]} <-> {msg_thread['to'].split('@')[0]}")
    
    # 5. Add comments to posts
    print("\n5. Adding comments to posts...")
    for comment_data in SEED_COMMENTS:
        post_id = post_id_map.get(comment_data["post_title"])
        if not post_id:
            print(f"  - Post '{comment_data['post_title'][:30]}...' not found")
            continue
        
        # Get existing comments count
        post = await db.posts.find_one({"_id": ObjectId(post_id)})
        if post and len(post.get("comments", [])) >= len(comment_data["comments"]):
            print(f"  - Comments already exist on '{comment_data['post_title'][:30]}...'")
            continue
        
        for commenter_email, content in comment_data["comments"]:
            commenter_id = user_id_map.get(commenter_email)
            if not commenter_id:
                continue
            
            commenter = await db.users.find_one({"_id": ObjectId(commenter_id)})
            comment_doc = {
                "id": str(ObjectId()),
                "user_id": commenter_id,
                "user_name": commenter.get("name", "Anonymous"),
                "user_avatar": commenter.get("avatar", ""),
                "content": encrypt_data(content),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))).isoformat()
            }
            
            await db.posts.update_one(
                {"_id": ObjectId(post_id)},
                {"$push": {"comments": comment_doc}}
            )
        
        print(f"  + Added {len(comment_data['comments'])} comments to: '{comment_data['post_title'][:40]}...'")
    
    # 6. Add some likes to posts
    print("\n6. Adding likes to posts...")
    all_user_ids = list(user_id_map.values())
    for post_title, post_id in post_id_map.items():
        # Random users like each post
        num_likes = random.randint(2, 6)
        likers = random.sample(all_user_ids, min(num_likes, len(all_user_ids)))
        
        await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"likes": likers}}
        )
        print(f"  + Added {len(likers)} likes to: '{post_title[:40]}...'")
    
    print("\n" + "="*50)
    print("DATABASE SEEDING COMPLETE!")
    print("="*50)
    print(f"\nCreated/verified:")
    print(f"  - {len(SEED_USERS)} users")
    print(f"  - {len(SEED_POSTS)} posts")
    print(f"  - {len(NETWORK_CONNECTIONS)} network connections")
    print(f"  - {len(SEED_MESSAGES)} message threads")
    print(f"  - Comments on {len(SEED_COMMENTS)} posts")
    print(f"\nDemo account: demo@rebeltrade.net / demo123")
    print(f"Admin account: admin@homesteadhub.com / admin123")


if __name__ == "__main__":
    asyncio.run(seed_database())
