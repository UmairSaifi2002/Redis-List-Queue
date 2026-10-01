"""
Producer script. Order service simulate karta hai.
Har 3 second mein ek naya order queue mein daalta hai.
"""
import time
import random
import json
from queue_utils import r, enqueue_order, queue_length, QUEUE_NAME


def make_order(order_id: int) -> dict:
    """Ek random order banao."""
    return {
        "order_id": order_id,
        "user_id": random.randint(1, 100),
        "items": random.randint(1, 5),
        "total": round(random.uniform(100, 2000), 2),
    }


if __name__ == "__main__":
    try:
        r.ping()
    except Exception:
        raise SystemExit("Start Redis first: sudo systemctl start redis-server")

    # Purani queue clear karo — fresh demo ke liye
    r.delete(QUEUE_NAME)
    r.delete("order_processing")

    print("🏭 Producer started. Enqueueing orders every 3 seconds...")
    print("   (Ctrl+C to stop)\n")

    order_id = 5000

    try:
        while True:
            order = make_order(order_id)
            length = enqueue_order(order)

            print(f"📥 [ENQUEUED] order #{order_id}  "
                  f"user={order['user_id']}  total=${order['total']:.0f}  "
                  f"→ queue length now: {length}")

            order_id += 1
            time.sleep(3)

    except KeyboardInterrupt:
        print(f"\n👋 Producer stopped. Final queue length: {queue_length()}")



        