from typing import Literal

DEFAULT_MODEL_ENCODING = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 4000

# UTF-8 content normalization settings
DEFAULT_NORMALIZE_CONTENT_ENCODING = True

# Create a type that represents all allowed categories
AllowedCategory = Literal[
    "Documentation", "Blog", "Blogs", "Community", "About", "Contact", 
    "Privacy", "Terms", "Status", "Pricing", "Enterprise", "Careers", 
    "E-Commerce", "Authentication", "Developer", "Developers", "Solutions", 
    "Partners", "Downloads", "Media", "Events", "People"
]
