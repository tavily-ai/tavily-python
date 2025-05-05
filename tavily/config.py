from typing import Literal

DEFAULT_MODEL_ENCODING = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 4000

# Create a type that represents all allowed categories
AllowedCategory = Literal[
    "Documentation", "Blog", "Blogs", "Community", "About", "Contact", 
    "Privacy", "Terms", "Status", "Pricing", "Enterprise", "Careers", 
    "E-Commerce", "Authentication", "Developer", "Developers", "Solutions", 
    "Partners", "Downloads", "Media", "Events", "People"
]

