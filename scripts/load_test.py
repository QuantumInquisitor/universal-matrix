import asyncio
import time
import argparse
from urllib.parse import urlparse
import http.client

DEFAULT_TARGET_URL = "http://127.0.0.1:8000/api/v1/telemetry/stream"

async def simulate_sse_client(client_id: int, duration_sec: int, url: str, stats: dict):
    """Simulates an active SSE subscriber listening to the telemetry stream."""
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 80
    path = parsed.path

    try:
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("GET", path, headers={"Accept": "text/event-stream"})
        response = conn.getresponse()

        if response.status != 200:
            stats["errors"] += 1
            return

        stats["active_connections"] += 1
        start_time = time.time()

        # Read streaming lines
        while time.time() - start_time < duration_sec:
            line = response.fp.readline()
            if not line:
                break
            if line.startswith(b"data:"):
                stats["messages_received"] += 1
                stats["bytes_received"] += len(line)
            await asyncio.sleep(0.01)

    except Exception:
        stats["errors"] += 1
    finally:
        stats["active_connections"] -= 1

async def run_load_test(clients: int, duration: int, url: str):
    """Orchestrates concurrent SSE clients and calculates throughput metrics."""
    print(f"==================================================")
    print(f"🌌 UNIVERSAL MATRIX ENGINE - SYNTHETIC LOAD TEST")
    print(f"==================================================")
    print(f"Target Endpoint : {url}")
    print(f"Concurrent Users: {clients}")
    print(f"Test Duration   : {duration} seconds\n")

    stats = {
        "active_connections": 0,
        "messages_received": 0,
        "bytes_received": 0,
        "errors": 0
    }

    start_wall_time = time.time()
    tasks = [
        asyncio.create_task(simulate_sse_client(i, duration, url, stats))
        for i in range(clients)
    ]

    # Monitor status periodically while workers run
    while any(not t.done() for t in tasks):
        elapsed = time.time() - start_wall_time
        print(f"[{elapsed:05.2f}s] Active SSE Clients: {stats['active_connections']}/{clients} | Messages: {stats['messages_received']} | Errors: {stats['errors']}", end="\r")
        await asyncio.sleep(1.0)

    await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_wall_time

    print("\n\n--------------------------------------------------")
    print("LOAD TEST RESULTS SUMMARY")
    print("--------------------------------------------------")
    print(f"Total Duration          : {total_time:.2f} s")
    print(f"Messages Delivered      : {stats['messages_received']}")
    print(f"Data Transferred        : {stats['bytes_received'] / 1024:.2f} KB")
    print(f"Message Throughput      : {stats['messages_received'] / total_time:.2f} msgs/sec")
    print(f"Total Failed Connections: {stats['errors']}")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic SSE Load Generator for Universal Matrix Engine")
    parser.add_argument("--clients", type=int, default=10, help="Number of concurrent SSE subscribers")
    parser.add_argument("--duration", type=int, default=10, help="Duration of load test in seconds")
    parser.add_argument("--url", type=str, default=DEFAULT_TARGET_URL, help="Target SSE stream URL")
    args = parser.parse_args()

    asyncio.run(run_load_test(args.clients, args.duration, args.url))