import json
from collections import Counter, defaultdict

with open("decrypted_records.json", "r") as f:
    records = [json.loads(r) for r in json.load(f)]

sorted_records = sorted(records, key=lambda x: x["timestamp"])

# ── Error rate by endpoint ────────────────────────────────────
print("=== Error rate by endpoint ===")
ep_total = Counter(r["endpoint"] for r in records)
ep_errors = Counter(r["endpoint"] for r in records if r["status_code"] >= 400)
for ep in sorted(ep_total):
    total = ep_total[ep]
    errors = ep_errors.get(ep, 0)
    rate = errors/total*100
    print(f"  {ep:30s} total={total:3d} errors={errors:3d} error_rate={rate:.1f}%")

# ── Avg latency by endpoint ───────────────────────────────────
print("\n=== Avg latency by endpoint ===")
ep_latency = defaultdict(list)
for r in records:
    ep_latency[r["endpoint"]].append(r["latency_ms"])
for ep in sorted(ep_latency):
    lats = ep_latency[ep]
    print(f"  {ep:30s} avg={sum(lats)/len(lats):8.1f}ms  min={min(lats):5d}  max={max(lats):5d}")

# ── Error rate by user_segment ────────────────────────────────
print("\n=== Error rate by user_segment ===")
seg_total = Counter(r["user_segment"] for r in records)
seg_errors = Counter(r["user_segment"] for r in records if r["status_code"] >= 400)
for seg in sorted(seg_total):
    total = seg_total[seg]
    errors = seg_errors.get(seg, 0)
    rate = errors/total*100
    print(f"  {seg:15s} total={total:3d} errors={errors:3d} error_rate={rate:.1f}%")

# ── Traffic volume over time (by week) ────────────────────────
print("\n=== Weekly traffic ===")
from collections import OrderedDict
weekly = defaultdict(int)
for r in sorted_records:
    week = r["timestamp"][:7]
    weekly[week] += 1
for month, count in sorted(weekly.items()):
    print(f"  {month}: {'#'*count} ({count})")

# ── 429 rate limit hits by segment ───────────────────────────
print("\n=== Rate limit (429) hits by segment ===")
r429 = Counter(r["user_segment"] for r in records if r["status_code"]==429)
for seg, count in r429.most_common():
    print(f"  {seg:15s}: {count}")

# ── Top error combos ─────────────────────────────────────────
print("\n=== Top error endpoint+method combos ===")
error_combos = Counter((r["endpoint"],r["method"]) for r in records if r["status_code"]>=400)
for combo, count in error_combos.most_common(10):
    print(f"  {combo[1]:6s} {combo[0]:30s}: {count}")

# ── High latency records (>4000ms) ───────────────────────────
print("\n=== High latency records (>4000ms) ===")
high_lat = sorted([r for r in records if r["latency_ms"]>4000], key=lambda x: x["latency_ms"], reverse=True)
print(f"  Count: {len(high_lat)}")
for r in high_lat[:10]:
    print(f"  {r['latency_ms']}ms | {r['endpoint']} | {r['method']} | {r['status_code']} | {r['user_segment']}")
    
