"""
Reliable worker using BRPOPLPUSH.
Message pehle 'processing' queue mein jaata hai.
Process hone ke baad hi delete hota hai.
Agar worker crash ho jaaye, message 'processing' queue mein safe rehta hai.
"""
import time
import json
import sys
import random
from queue_utils import r, QUEUE_NAME, PROCESSING_QUEUE


def process_order(order: dict, worker_id: str):
    print(f"  [{worker_id}] Processing order #{order['order_id']} "
          f"(user={order['user_id']}, ${order['total']:.0f})")
    time.sleep(random.uniform(0.5, 1.5))

    if random.random() < 0.1:
        raise RuntimeError(f"Simulated failure on order {order['order_id']}")

    print(f"  [{worker_id}] ✅ Order #{order['order_id']} done")

def recover_stuck_messages(max_age_seconds=60):
    """
    Processing queue mein jo messages purane ho gaye hain,
    unko wapas main queue mein daal do.
    """
    # Ye ek simple version hai. Production mein aap
    # timestamps maintain karte ho taaki pata chale kaunse
    # messages "stuck" hain.
    stuck = r.lrange(PROCESSING_QUEUE, 0, -1)
    for msg in stuck:
        r.lpush(QUEUE_NAME, msg)
        r.lrem(PROCESSING_QUEUE, 1, msg)
        print(f"♻️  Recovered: {msg[:50]}...")

def main():
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "W1"

    print(f"👷 [{worker_id}] RELIABLE worker started.")
    print(f"   Source:      {QUEUE_NAME}")
    print(f"   Processing:  {PROCESSING_QUEUE}")
    print(f"   (Ctrl+C to stop)\n")

    try:
        while True:
            # ⭐ ATOMIC: pop from source AND push to processing in one step
            raw_message = r.brpoplpush(
                QUEUE_NAME,
                PROCESSING_QUEUE,
                timeout=0
            )

            if raw_message is None:
                continue

            order = json.loads(raw_message)

            try:
                process_order(order, worker_id)

                # ✅ Success → remove from processing queue
                removed = r.lrem(PROCESSING_QUEUE, 1, raw_message)
                print(f"  [{worker_id}] 🧹 Removed from processing queue ({removed})")

            except Exception as e:
                # ❌ Failure → message stays in processing queue
                # A recovery process would later move it back or retry
                print(f"  [{worker_id}] ❌ FAILED: {e}  "
                      f"(message SAFE in '{PROCESSING_QUEUE}')")

    except KeyboardInterrupt:
        print(f"\n👋 [{worker_id}] Stopped.")


if __name__ == "__main__":
    try:
        r.ping()
    except Exception:
        raise SystemExit("Start Redis first: sudo systemctl start redis-server")
    main()



    