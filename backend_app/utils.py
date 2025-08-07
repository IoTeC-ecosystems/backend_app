"""
Auxiliary functions for the backend
"""
import uuid

def is_valid_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False
