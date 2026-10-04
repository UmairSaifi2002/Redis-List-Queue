"""
Basic worker. BRPOP use karta hai — simple but at-most-once semantics.
Worker crash ho jaaye toh message kho jaayega.
"""
import time
import json
import sys
import random
from queue_utils import r, QUEUE_NAME


def process_order(order: dict, worker_id: str):
    """
    Order ko "process" karo. Real duniya mein yeh DB update, email,
    inventory check, etc. hoga.
    """
    print(f"  [{worker_id}] Processing order #{order['order_id']} "
          f"(user={order['user_id']}, ${order['total']:.0f})")

    # Simulate processing time
    time.sleep(random.uniform(0.5, 1.5))

    # Simulate occasional failure (10% chance)
    if random.random() < 0.1:
        raise RuntimeError(f"Simulated failure on order {order['order_id']}")

    print(f"  [{worker_id}] ✅ Order #{order['order_id']} done")


def main():
    if len(sys.argv) < 2:
        worker_id = "W1"
    else:
        worker_id = sys.argv[1]

    print(f"👷 [{worker_id}] Worker started. Waiting for orders...")
    print(f"   (Ctrl+C to stop)\n")

    try:
        while True:
            # BRPOP blocks until a message arrives.
            # Returns tuple (queue_name, message) or None on timeout.
            result = r.brpop(QUEUE_NAME, timeout=0)

            if result is None:
                continue   # shouldn't happen with timeout=0, but safe

            # Tuple unpacking: _, raw_message = result — pehla element (queue name) ignore kar diya, dusra (message) le liya
            _, raw_message = result
            order = json.loads(raw_message)

            try:
                process_order(order, worker_id)
            except Exception as e:
                # ⚠️ Message is LOST here — it was already popped from queue
                print(f"  [{worker_id}] ❌ FAILED: {e}  (message LOST)")

    except KeyboardInterrupt:
        print(f"\n👋 [{worker_id}] Worker stopped.")


if __name__ == "__main__":
    try:
        r.ping()
    except Exception:
        raise SystemExit("Start Redis first: sudo systemctl start redis-server")
    main()


    