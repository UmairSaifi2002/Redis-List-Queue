"""
Shared utilities for the List Queue demo.
"""
import json
import redis

QUEUE_NAME = "order_queue"
PROCESSING_QUEUE = "order_processing" # Backup queue for processing orders
RESULT_KEY = "order_results"

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def enqueue_order(order_data: dict):
    """Order ko queue ke left mein daalo (LPUSH)."""
    message = json.dumps(order_data)
    length_after = r.lpush(QUEUE_NAME, message)
    return length_after


def queue_length() -> int:
    """Queue mein kitne messages hain."""
    return r.llen(QUEUE_NAME)


