#!/usr/bin/env python3
"""Check CORS settings"""

from app.core.config import settings

print("CORS Origins configured:")
print(settings.cors_origins)
print("\nAPI URL:", settings.api_url)
