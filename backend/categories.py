"""
Predefined categories for goods, skills, and services.
"""

GOODS_CATEGORIES = {
    "food": {
        "name": "Food",
        "icon": "carrot",
        "items": [
            "Fresh Eggs", "Honey", "Raw Milk", "Cheese", "Butter", "Yogurt",
            "Fresh Vegetables", "Root Vegetables", "Leafy Greens", "Tomatoes", "Peppers",
            "Fresh Fruits", "Berries", "Apples", "Citrus", "Stone Fruits",
            "Beef", "Pork", "Chicken", "Turkey", "Lamb", "Goat Meat", "Venison", "Rabbit Meat", "Fish",
            "Canned Goods", "Pickles", "Jams & Preserves", "Sauces", "Dried Herbs", "Dried Fruits",
            "Maple Syrup", "Sorghum", "Molasses",
            "Flour", "Cornmeal", "Oats", "Rice", "Wheat Berries", "Barley",
            "Nuts", "Seeds for Eating", "Nut Butters",
            "Baked Goods", "Bread", "Pastries",
            "Fermented Foods", "Sauerkraut", "Kimchi", "Kombucha",
            "Herbs & Spices", "Tea Blends", "Coffee",
            "Bone Broth", "Lard", "Tallow", "Bacon", "Sausage", "Jerky"
        ]
    },
    "tools": {
        "name": "Tools",
        "icon": "wrench",
        "items": [
            "Hand Saws", "Axes", "Hatchets", "Machetes", "Shovels", "Spades",
            "Rakes", "Hoes", "Pitchforks", "Wheelbarrows", "Garden Carts",
            "Hammers", "Wrenches", "Screwdrivers", "Pliers", "Socket Sets",
            "Power Drills", "Circular Saws", "Chainsaws", "Angle Grinders",
            "Welding Equipment", "Soldering Irons", "Multimeters",
            "Ladders", "Scaffolding", "Sawhorses",
            "Canning Equipment", "Pressure Canners", "Water Bath Canners",
            "Dehydrators", "Meat Grinders", "Sausage Stuffers",
            "Milking Equipment", "Cream Separators", "Cheese Presses",
            "Bee Keeping Equipment", "Hive Tools", "Smokers", "Extractors",
            "Fencing Tools", "Post Hole Diggers", "Wire Stretchers",
            "Irrigation Supplies", "Drip Systems", "Pumps",
            "Blacksmithing Tools", "Anvils", "Forges", "Tongs",
            "Woodworking Tools", "Chisels", "Planes", "Clamps",
            "Hunting Equipment", "Traps", "Fishing Gear"
        ]
    },
    "crafts": {
        "name": "Crafts",
        "icon": "scissors",
        "items": [
            "Handmade Furniture", "Chairs", "Tables", "Shelves", "Bed Frames", "Cabinets",
            "Wooden Bowls", "Cutting Boards", "Spoons & Utensils",
            "Quilts", "Blankets", "Afghans", "Throws",
            "Clothing", "Shirts", "Pants", "Dresses", "Aprons",
            "Knitwear", "Sweaters", "Hats", "Scarves", "Mittens", "Socks",
            "Leather Goods", "Belts", "Bags", "Wallets", "Holsters", "Sheaths",
            "Pottery", "Bowls", "Mugs", "Plates", "Vases",
            "Baskets", "Woven Goods",
            "Candles", "Beeswax Candles", "Soy Candles",
            "Soaps", "Body Care Products", "Lotions", "Salves", "Lip Balms",
            "Herbal Products", "Tinctures", "Oils", "Balms",
            "Jewelry", "Metalwork", "Beadwork",
            "Art & Paintings", "Prints", "Sculptures",
            "Toys", "Wooden Toys", "Stuffed Animals", "Dolls",
            "Rugs", "Tapestries", "Macrame",
            "Knives", "Custom Knives", "Knife Sheaths",
            "Musical Instruments", "Drums", "Flutes", "Stringed Instruments"
        ]
    },
    "livestock": {
        "name": "Livestock",
        "icon": "cow",
        "items": [
            "Laying Hens", "Meat Chickens", "Roosters", "Chicks",
            "Ducks", "Ducklings", "Geese", "Turkeys", "Guinea Fowl", "Quail",
            "Dairy Goats", "Meat Goats", "Fiber Goats", "Kids (Baby Goats)",
            "Dairy Cows", "Beef Cattle", "Calves",
            "Pigs", "Piglets", "Breeding Sows", "Boars",
            "Sheep", "Lambs", "Breeding Ewes", "Rams",
            "Rabbits", "Breeding Stock", "Meat Rabbits", "Fiber Rabbits",
            "Bees", "Bee Colonies", "Nucs", "Queen Bees",
            "Horses", "Ponies", "Donkeys", "Mules",
            "Llamas", "Alpacas",
            "Guard Dogs", "Herding Dogs", "Working Dogs",
            "Cats", "Barn Cats",
            "Fish (Aquaponics)", "Tilapia", "Catfish", "Trout",
            "Hatching Eggs", "Fertilized Eggs"
        ]
    },
    "miscellaneous": {
        "name": "Miscellaneous",
        "icon": "package",
        "items": [
            "Seeds", "Heirloom Seeds", "Seed Potatoes", "Seed Garlic",
            "Plant Starts", "Seedlings", "Transplants",
            "Fruit Trees", "Nut Trees", "Berry Bushes",
            "Firewood", "Kindling", "Logs",
            "Lumber", "Boards", "Beams", "Plywood",
            "Building Materials", "Bricks", "Stones", "Gravel",
            "Fencing Materials", "Wire", "Posts", "Gates",
            "Hay", "Straw", "Alfalfa", "Feed",
            "Compost", "Manure", "Mulch", "Soil",
            "Rainwater Collection", "Barrels", "Tanks",
            "Solar Panels", "Batteries", "Inverters",
            "Fuel", "Propane", "Diesel", "Gasoline",
            "Wool", "Raw Fleece", "Roving", "Yarn",
            "Hides", "Leather", "Fur",
            "Feathers", "Down",
            "Antlers", "Bones", "Horns",
            "Beeswax", "Propolis", "Pollen",
            "Vehicles", "Tractors", "ATVs", "Trailers",
            "Books", "Magazines", "Educational Materials"
        ]
    }
}

SKILLS_CATEGORIES = {
    "homestead": {
        "name": "Homestead Skills",
        "icon": "house",
        "items": [
            "Canning & Preserving", "Water Bath Canning", "Pressure Canning",
            "Fermenting", "Lacto-Fermentation", "Alcohol Fermentation",
            "Cheese Making", "Butter Making", "Yogurt Making",
            "Soap Making", "Cold Process Soap", "Hot Process Soap",
            "Candle Making", "Beeswax Candles", "Dipped Candles",
            "Butchering", "Meat Processing", "Smoking & Curing",
            "Sausage Making", "Jerky Making",
            "Beekeeping", "Hive Management", "Honey Extraction",
            "Animal Husbandry", "Breeding", "Birthing Assistance",
            "Milking", "Hand Milking", "Machine Milking",
            "Egg Incubation", "Chick Brooding",
            "Seed Saving", "Seed Starting",
            "Foraging", "Wild Edibles", "Mushroom Identification",
            "Herbalism", "Herbal Medicine", "Tincture Making",
            "Fiber Arts", "Spinning", "Weaving", "Dyeing",
            "Tanning", "Hide Processing", "Leather Working",
            "Food Dehydration", "Freeze Drying",
            "Root Cellaring", "Food Storage",
            "Wine Making", "Beer Brewing", "Cider Making", "Mead Making"
        ]
    },
    "landscape": {
        "name": "Landscape & Land Skills",
        "icon": "tree",
        "items": [
            "Permaculture Design", "Food Forest Design",
            "Garden Planning", "Raised Bed Construction",
            "Irrigation Systems", "Drip Irrigation", "Swales",
            "Fencing", "Wood Fencing", "Wire Fencing", "Electric Fencing",
            "Land Clearing", "Brush Removal", "Stump Removal",
            "Pond Building", "Dam Construction", "Water Features",
            "Tree Grafting", "Fruit Tree Pruning", "Espalier",
            "Composting", "Vermiculture", "Bokashi",
            "Soil Building", "Cover Cropping", "No-Till Gardening",
            "Greenhouse Construction", "Hoop House Building",
            "Barn Building", "Shed Construction", "Coop Building",
            "Earthworks", "Terracing", "Berms",
            "Forestry", "Timber Harvesting", "Coppicing", "Pollarding",
            "Pasture Management", "Rotational Grazing",
            "Orchard Management", "Vineyard Management",
            "Landscaping", "Hardscaping", "Retaining Walls",
            "Trail Building", "Road Maintenance",
            "Erosion Control", "Water Management"
        ]
    },
    "trade": {
        "name": "Trade & Technical Skills",
        "icon": "hammer",
        "items": [
            "Carpentry", "Finish Carpentry", "Framing",
            "Welding", "MIG Welding", "TIG Welding", "Stick Welding",
            "Plumbing", "Pipe Fitting", "Drain Cleaning",
            "Electrical", "Wiring", "Panel Installation",
            "Masonry", "Brick Laying", "Stone Work", "Concrete Work",
            "Roofing", "Metal Roofing", "Shingle Roofing",
            "Solar Installation", "Off-Grid Systems", "Grid-Tie Systems",
            "Generator Repair", "Small Engine Repair",
            "Well Drilling", "Well Pump Repair",
            "Septic Systems", "Composting Toilet Installation",
            "HVAC", "Wood Stove Installation", "Chimney Work",
            "Mechanic", "Auto Repair", "Diesel Mechanic", "Tractor Repair",
            "Gunsmithing", "Firearms Repair", "Custom Builds",
            "Knife Making", "Bladesmithing",
            "Blacksmithing", "Forging", "Metal Fabrication",
            "Machining", "Lathe Work", "Mill Work",
            "Electronics Repair", "Computer Repair",
            "Appliance Repair", "Water Heater Repair",
            "Painting", "Staining", "Finishing",
            "Upholstery", "Furniture Repair", "Refinishing"
        ]
    },
    "creative": {
        "name": "Creative & Artisan Skills",
        "icon": "palette",
        "items": [
            "Woodworking", "Furniture Making", "Cabinetry", "Carving",
            "Pottery", "Wheel Throwing", "Hand Building", "Glazing",
            "Sewing", "Quilting", "Pattern Making", "Tailoring",
            "Knitting", "Crocheting", "Macrame",
            "Basket Weaving", "Chair Caning",
            "Jewelry Making", "Silversmithing", "Beading",
            "Leathercraft", "Saddle Making", "Harness Making",
            "Musical Instrument Building", "Instrument Repair",
            "Bow Making", "Arrow Fletching",
            "Photography", "Videography",
            "Graphic Design", "Web Design",
            "Writing", "Editing", "Publishing",
            "Painting", "Drawing", "Illustration",
            "Sculpture", "Woodcarving", "Stone Carving",
            "Printmaking", "Screen Printing",
            "Calligraphy", "Sign Painting"
        ]
    },
    "life": {
        "name": "Life & Survival Skills",
        "icon": "first-aid",
        "items": [
            "First Aid", "Emergency Medicine", "CPR",
            "Midwifery", "Doula Services", "Lactation Consulting",
            "Herbalism", "Natural Remedies", "Essential Oils",
            "Veterinary Care", "Animal First Aid",
            "Hunting", "Tracking", "Trapping",
            "Fishing", "Fly Fishing", "Netting",
            "Archery", "Marksmanship", "Firearms Training",
            "Self-Defense", "Martial Arts",
            "Navigation", "Map Reading", "Orienteering",
            "Wilderness Survival", "Shelter Building", "Fire Starting",
            "Water Purification", "Well Water Testing",
            "Radio Communications", "HAM Radio",
            "Teaching", "Tutoring", "Homeschool Curriculum",
            "Childcare", "Eldercare",
            "Cooking", "Baking", "Meal Planning",
            "Nutrition", "Diet Planning",
            "Financial Planning", "Bookkeeping", "Tax Preparation",
            "Legal Knowledge", "Contract Writing",
            "Project Management", "Community Organizing"
        ]
    }
}

SERVICES_CATEGORIES = {
    "labor": {
        "name": "Labor & Physical Work",
        "icon": "users",
        "items": [
            "Farm Labor", "Field Work", "Harvesting Help",
            "Barn Chores", "Animal Care", "Feeding",
            "Fence Building", "Fence Repair",
            "Land Clearing", "Brush Cutting",
            "Firewood Cutting", "Firewood Splitting", "Stacking",
            "Construction Labor", "Demolition",
            "Moving Help", "Heavy Lifting",
            "Cleaning", "Deep Cleaning", "Organization",
            "Painting", "Staining", "Pressure Washing",
            "Landscaping", "Lawn Care", "Garden Maintenance",
            "Snow Removal", "Ice Management",
            "Tree Trimming", "Tree Removal",
            "Pond Maintenance", "Ditch Digging"
        ]
    },
    "equipment": {
        "name": "Equipment & Rentals",
        "icon": "tractor",
        "items": [
            "Tractor Rental", "Tractor Services",
            "Truck Rental", "Trailer Rental",
            "Equipment Rental", "Tool Rental",
            "Chainsaw Services", "Stump Grinding",
            "Tilling Services", "Plowing Services",
            "Hay Baling", "Hay Cutting",
            "Excavation", "Backhoe Services",
            "Post Hole Drilling", "Auger Services",
            "Wood Chipping", "Mulching Services",
            "Delivery Services", "Hauling Services",
            "Moving Services", "Freight Hauling"
        ]
    },
    "animal": {
        "name": "Animal Services",
        "icon": "paw",
        "items": [
            "Stud Services", "Breeding Services",
            "Artificial Insemination",
            "Animal Training", "Dog Training", "Horse Training",
            "Farrier Services", "Horse Shoeing", "Hoof Trimming",
            "Shearing", "Wool Processing",
            "Butchering Services", "Mobile Butcher",
            "Veterinary Services", "Animal Wellness",
            "Pet Sitting", "Farm Sitting",
            "Livestock Transport", "Horse Transport",
            "Beekeeping Services", "Hive Inspection",
            "Pest Control", "Predator Control",
            "Poultry Processing", "Egg Washing"
        ]
    },
    "professional": {
        "name": "Professional Services",
        "icon": "briefcase",
        "items": [
            "Consulting", "Farm Planning", "Business Consulting",
            "Land Survey", "Property Assessment",
            "Legal Services", "Contract Review",
            "Accounting", "Bookkeeping", "Tax Preparation",
            "Marketing", "Social Media", "Website Building",
            "Photography", "Drone Photography",
            "Writing", "Content Creation", "Grant Writing",
            "Design Services", "Logo Design",
            "Appraisal Services", "Livestock Appraisal",
            "Insurance Consulting", "Risk Assessment",
            "Real Estate Services", "Land Sales"
        ]
    },
    "education": {
        "name": "Education & Training",
        "icon": "book",
        "items": [
            "Workshops", "Classes", "Seminars",
            "One-on-One Training", "Apprenticeships", "Mentoring",
            "Homesteading Classes", "Gardening Classes",
            "Canning Workshops", "Preservation Classes",
            "Animal Husbandry Training", "Beekeeping Classes",
            "Survival Skills Training", "Wilderness Classes",
            "Firearms Training", "Hunter Safety",
            "First Aid Training", "CPR Classes",
            "Homeschool Tutoring", "Curriculum Consulting",
            "Cooking Classes", "Baking Classes",
            "Crafting Workshops", "Fiber Arts Classes",
            "Woodworking Classes", "Metalworking Classes"
        ]
    },
    "health": {
        "name": "Health & Personal Services",
        "icon": "heart",
        "items": [
            "Midwifery", "Birth Support", "Doula Services",
            "Lactation Consulting", "Postpartum Support",
            "Massage Therapy", "Bodywork",
            "Herbal Consultations", "Natural Health",
            "Childcare", "Babysitting", "Nanny Services",
            "Eldercare", "Companion Care",
            "Meal Prep", "Cooking Services",
            "House Sitting", "Property Management",
            "Errands", "Shopping Services",
            "Transportation", "Medical Transport",
            "Counseling", "Life Coaching",
            "Spiritual Services", "Ceremony Officiating"
        ]
    },
    "custom": {
        "name": "Custom & Made-to-Order",
        "icon": "magic-wand",
        "items": [
            "Custom Furniture", "Built-to-Order",
            "Custom Clothing", "Alterations", "Tailoring",
            "Custom Knives", "Custom Tools",
            "Custom Leatherwork", "Saddle Making",
            "Custom Pottery", "Commissioned Art",
            "Custom Jewelry", "Engraving",
            "Custom Woodwork", "Carving Commissions",
            "Custom Metalwork", "Forged Items",
            "Custom Soap", "Custom Candles",
            "Bespoke Goods", "Special Orders"
        ]
    }
}
