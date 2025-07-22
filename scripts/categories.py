REGION_TYPES = ["O", "P", "H", "B"]
SETTLEMENT_TYPES = ["K", "M", "X", "C"]
ALL_TYPES = REGION_TYPES + SETTLEMENT_TYPES

TYPE_MAPPING = {
    "С": "село","C": "село",
    "X": "селище","X": "селище", "Щ": "селище", "Т": "селище","T": "селище", 
    "М": "місто", "К": "місто","M": "місто", "K": "місто",
    "O":"область","О":"область",
    "Р":"район","P":"район",
    "H":"громада","Н":"громада",
    "B":"район міста","В":"район міста"
    }


ADMINISTRATIVE_LEVELS = {
    "O": 1,  # Oblast
    "P": 2,  # District
    "H": 3,  # Community
    "B": 5,  # City district
    "K": 1,  # Special City level (capital, Kyiv, Sevastopol)
    "M": 4,  # Town
    "X": 4,  # Village
    "C": 4,  # Rural settlement
}

def get_admin_level(settlement):
    """Returns the administrative level of a settlement."""
    category = settlement.get("category")
    return ADMINISTRATIVE_LEVELS.get(category, 0)

def get_settlement_category(settlement):
    """Returns the category of a settlement based on its properties."""
    return settlement.get("category")

def get_settlement_level(settlement):
    """Returns the administrative level of a settlement."""
    category = get_settlement_category(settlement)
    return ADMINISTRATIVE_LEVELS.get(category, 0)

def is_area_type(settlement):
    """Returns True if the settlement is a region."""
    return get_settlement_category(settlement) in REGION_TYPES

def is_point_type(settlement):
    """Returns True if the settlement is a settlement."""
    return get_settlement_category(settlement) in SETTLEMENT_TYPES

def get_category_name(category):
    """Returns the human-readable name of a settlement category."""

    return TYPE_MAPPING.get(category, "Невідомий тип")