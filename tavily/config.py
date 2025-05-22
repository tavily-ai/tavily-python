"""
Configuration constants and types for the Tavily API client.

This module defines configuration constants and type definitions used throughout
the Tavily API client. These include default values for token limits and model
encodings, as well as type definitions for allowed categories.

Constants:
    DEFAULT_MODEL_ENCODING: The default encoding model used for tokenization
    DEFAULT_MAX_TOKENS: The default maximum number of tokens for API requests

Types:
    AllowedCategory: A Literal type defining all allowed category values for content classification
"""

from typing import Literal

# Default encoding model for tokenization
DEFAULT_MODEL_ENCODING: str = "gpt-3.5-turbo"

# Default maximum number of tokens for API requests
DEFAULT_MAX_TOKENS: int = 4000

# Create a type that represents all allowed categories
AllowedCategory = Literal[
    "About",
    "Authentication",
    "Blog",
    "Blogs",
    "Careers",
    "Community",
    "Contact",
    "Developer",
    "Developers",
    "Documentation",
    "Downloads",
    "E-Commerce",
    "Enterprise",
    "Events",
    "Media",
    "Partners",
    "People",
    "Pricing",
    "Privacy",
    "Solutions",
    "Status",
    "Terms",
]
