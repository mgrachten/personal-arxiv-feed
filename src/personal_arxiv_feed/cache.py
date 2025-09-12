"""
This module holds the in-memory cache for the application.
"""

# A cache to hold the entry_ids of articles seen in the last query.
# This is cleared when interests are updated to allow for re-classification.
LAST_QUERY_ENTRY_IDS: set[str] = set()
