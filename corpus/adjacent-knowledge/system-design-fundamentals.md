---
title: "System design fundamentals: load balancing, caching, sharding, consistent hashing"
pillar: adjacent-knowledge
method: deep-research
date: 2026-07-01
sources: 15
confidence: high
---

## What it is

These four concepts are one stack, not four topics. They exist to spread traffic and state across many machines when one can no longer hold it, and they share a single enemy: naive `hash(key) mod N` placement, which reshuffles almost everything the moment `N` changes. Load balancing distributes requests across replicas; caching keeps hot data close to avoid recomputation; sharding partitions data so no single node owns all of it; and consistent hashing is the connective tissue that lets the other three grow and shrink their node sets without a mass remap.

Read them as a layered defense against the same failure — *correlated load concentration under topology change*. A cache node dies, a shard splits, a backend is added: in each case the question is "how many keys just moved, and did they all pile onto one survivor?" Consistent hashing, cache leases, and bounded-load variants are all answers to that one question, attacked at different layers.

## When to reach for it

Load balancing is unavoidable the instant you run more than one replica. The real decision is L4 versus L7. Reach for **L4** (transport-layer, routing opaque TCP/UDP flows by their 5-tuple) when you need raw connection throughput, DDoS absorption, or protocol-agnostic forwarding, and you don't need to route on request content [1]. Reach for **L7** (application-layer, terminating the connection and parsing HTTP/gRPC) when routing must depend on URL path, headers, cookies, or method — canary routing, per-tenant routing, or per-request balancing of multiplexed HTTP/2 streams [1]. The common production shape is both: an L4 edge tier for volume, an L7 tier behind it for content routing.

Reach for **caching** when reads dominate and recomputation or a round-trip to the store is the bottleneck — but only when a slightly stale answer is acceptable, because the cost of caching is invalidation, not the cache itself. Reach for **sharding** when a single node can no longer hold the data or serve the write volume — capacity, not just read latency. And reach for **consistent hashing** whenever the set of nodes behind a cache or shard tier changes at runtime and you cannot afford to invalidate or move everything on each change [7][12].

## How it works

**L4 versus L7, precisely.** An L4 balancer forwards packets by the connection 5-tuple (protocol, source IP, source port, destination IP, destination port) without inspecting payload. It is fast and connection-oriented, but it cannot see requests: multiple gRPC or HTTP/2 requests multiplexed over one TCP connection are one unit to it, so it physically cannot load-balance per request [1]. An L7 balancer terminates the connection, parses the application protocol, and routes each request independently — which is why per-request balancing, path routing, and header routing all live at L7 [1].

**The balancing algorithm underneath.** Given a chosen backend set, how do you pick one? Round-robin is the floor. Envoy's **least-request** balancer is more interesting: rather than scan every host for the global minimum active-request count — which causes herding, since every balancer instant-piles onto the same "least loaded" host — it uses **power-of-two-choices (P2C)**: pick 2 random hosts (the default) and route to whichever has fewer active requests. This is O(1) and, because the two samples are independent per decision, it avoids the synchronized herd a global-minimum pick creates [2].

**Hash-based (sticky) balancing** is where consistent hashing enters the load balancer. Envoy's **ring hash** (also known as **ketama**) maps hosts onto a circle so that adding or removing one host of `N` disturbs only about `1/N` of requests [2]. Envoy's **Maglev** uses a fixed lookup table of size 65537; against a large 256K-entry ring it builds tables ~10x faster and selects hosts ~5x faster, but it is *less stable* — on host removal roughly double the keys move compared to ring hash [2]. Those speedup multiples are specific to that 256K-entry ring comparison, not a universal law.

**Cache invalidation is the whole game.** The hit path is trivial; the strategies differ entirely on what happens on a write [3]:

- **Cache-aside (lazy loading):** the app reads the cache, falls through to the DB on a miss, and populates the cache; on a write it updates the DB and *evicts* the key. Simple, resilient, but every miss pays a DB round-trip and there's a window where the cache holds stale data.
- **Write-through:** write cache and DB synchronously. Always fresh, at the cost of higher write latency.
- **Write-back (write-behind):** write the cache and flush to the DB asynchronously. Lowest write latency, but data is lost if the cache node dies before the flush.

**TTL** rides underneath these as a safety net: short TTLs are fresher but miss more; long TTLs raise hit rate but serve staler data. Layered under cache-aside or write-through, TTL auto-expires anything a targeted invalidation missed [3].

**The herd is the failure mode caching creates.** When a hot key expires, every concurrent reader misses at once and stampedes the DB. Facebook's memcache **leases** solve this and stale sets with one mechanism: on a miss, the server hands the client a 64-bit token bound to the key, and the client must present that token to set the value. The server issues a lease at most once every 10 seconds per key, so concurrent missers wait rather than all recomputing. On a delete, outstanding lease tokens for that key are invalidated, which prevents an out-of-order (stale) set from persisting [4][5].

**Sharding and the hot-key wall.** Horizontal sharding partitions rows across nodes. **Range partitioning** (contiguous key ranges) gives efficient range scans but hot-spots on sequential or skewed keys — timestamps, or many customers whose surnames start with the same letter [8]. **Hash partitioning** spreads load evenly but destroys efficient range queries [8]. **Hash-range sharding** is the adaptive middle: assign ranges of *hash* values to shards and split a shard only when it grows hot [9]. But no scheme auto-fixes a single hot key — the **celebrity problem**. One account with millions of followers concentrates all its traffic on one partition no matter how you hash. DDIA's mitigation is *application-level*: prefix the hot key with a small random number (e.g. 2 digits) to spread it across ~100 keys, accepting that reads must now fan out to all 100 and recombine [10].

**Consistent hashing, the connective tissue.** Introduced by Karger et al. in 1997 to relieve web hot spots, a consistent hash function is one that changes minimally as its output range (the server set) changes [11]. With `hash mod N`, changing `N` remaps nearly every key. With consistent hashing, only about `K/N` keys (of `K` keys over `N` servers) remap when a node joins or leaves — an average-case bound, not an absolute guarantee [11][12]. Because placing nodes randomly on the ring produces uneven load, real systems add **virtual nodes**: multiple ring positions per physical server, which cut load variance and let capacity be tuned per node. Dynamo does exactly this — a consistent-hashing ring, each physical node mapped to multiple virtual nodes whose count scales with its capacity, plus quorum replication and gossip membership [13].

## Trade-offs

The contradiction map here is sharp, because "consistent hashing" names a family with real internal tension, not a single best choice.

**Uniformity versus stability, inside hash-based balancing.** Envoy documents this as a live decision, not a recommendation: **Maglev** optimizes build/lookup speed and table uniformity but is less stable — ~2x more keys move on membership change; **ring/ketama** is more stable but slower to build [2]. You pick based on whether your churn cost (connection resets, cache misses on remap) or your build/lookup cost dominates.

**Minimal remapping does not mean even load.** This is the subtler tension. Karger's ring *minimizes remapping* but *tolerates load skew* — it says nothing about balance [11]. **Consistent Hashing with Bounded Loads** (Mirrokni, Thorup et al., 2016) closes exactly that gap: for any `ε`, each server's load is capped at `(1+ε)` times the average. And `ε` is itself a tradeoff dial — lower `ε` improves uniformity but forces more client migrations on topology change; higher `ε` improves stability at the cost of uniformity [15]. So you are never buying "consistent hashing"; you are choosing a point on a uniformity–stability curve.

**Caching's dangerous trade is availability for a hidden coupling.** Amazon's Builders' Library warns a service can become "addicted to its cache," where the cache is inadvertently elevated "from a helpful addition to the service to a necessary and critical part of its ability to operate" [7]. The root risk is **modal behavior** — different behavior on hit versus miss — so an unanticipated shift in hit-rate distribution (a cold cache after a node comes up empty) can overload the backing store and "lead to disaster" [7]. A cache sized to hide the DB's true load is a latent outage.

**The blind spot most sources miss:** caching hot keys and sharding hot ranges get framed as separate problems, but they are the *same* problem — a single hot key or hot range that no hashing scheme can spread. That is why the ultimate mitigation (application-level key splitting [10]) lives *above* the infrastructure layer, not inside any balancer or partitioner. Consistent hashing, leases, and bounded loads all attack correlated load concentration under topology change; none of them can un-concentrate load that is intrinsically concentrated in one key.

## In practice

Two concrete, citable anchors.

**Facebook memcache leases.** Regulating recomputation with leases reportedly dropped peak database load from ~17,000 to ~1,300 queries per second — roughly a 13x reduction [6]. Treat this figure as *medium* confidence: the primary NSDI 2013 PDF returned 403 on fetch, so the numbers come from multiple independent secondary summaries of the paper rather than a verbatim read of the source [6]. The mechanism itself (64-bit token, 10s-per-key rate limit, delete-invalidates-token) is high confidence and confirmed against the paper's summaries [4][5].

**Consistent Hashing with Bounded Loads in production.** The `(1+ε)` bounded-load scheme shipped in Google Cloud Pub/Sub and was adopted by Vimeo in HAProxy, where it cut cache bandwidth by nearly 8x [15]. And **Maglev** — Google's software network load balancer serving production traffic since 2008 — combines consistent hashing with connection tracking to hit two goals at once: fair balancing (near-equal connections per backend) and minimal disruption (when backends change, an existing connection likely still lands on its prior backend) [14]. Maglev is the load-balancer end of the same ring that Dynamo runs at the storage end — the clearest evidence these are one stack, not four topics.

One operational warning worth internalizing from Amazon: not all cache client libraries implement consistent hashing, so a fleet that *looks* horizontally scalable can still mass-invalidate on every node change if the client is doing `mod N` under the hood [7][12]. Check the client, not just the architecture diagram.

## Further reading

1. Networking Essentials for System Design (L4 vs L7 load balancing) — Hello Interview — https://www.hellointerview.com/learn/system-design/core-concepts/networking-essentials
2. Supported load balancers — Envoy proxy documentation — https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers
3. Cache invalidation: TTL, write-through, write-behind, cache-aside — https://www.kunalganglani.com/learning-paths/backend-developer/be-caching-invalidation
4. MIT 6.824 Lecture 16 notes — Scaling Memcache at Facebook (leases) — https://timilearning.com/posts/mit-6.824/lecture-16-memcache-at-facebook/
5. Scaling Memcache at Facebook — paper summary (leases, stale sets) — https://www.micahlerner.com/2021/05/31/scaling-memcache-at-facebook.html
6. Nishtala et al., Scaling Memcache at Facebook, NSDI 2013 (primary; qps figure via summaries) — https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf
7. Caching challenges and strategies — Amazon Builders' Library — https://aws.amazon.com/builders-library/caching-challenges-and-strategies/
8. Database Sharding Explained for Scalable Systems — Aerospike — https://aerospike.com/blog/database-sharding-scalable-systems/
9. From Hot Keys to Rebalancing: A Deep Dive into Sharding — https://medium.com/startlovingyourself/from-hot-keys-to-rebalancing-a-deep-dive-into-sharding-dcb48c69bab7
10. DDIA Chapter 6 — Partitioning notes (celebrity/hot-key problem) — https://github.com/ResidentMario/designing-data-intensive-applications-notes/blob/master/Chapter%206%20---%20Partitioning.ipynb
11. Consistent hashing — Wikipedia (Karger 1997 origin, K/n remapping) — https://en.wikipedia.org/wiki/Consistent_hashing
12. Caching challenges and strategies (PDF) — Amazon Builders' Library — https://d1.awsstatic.com/builderslibrary/pdfs/caching-challenges-and-strategies.pdf
13. DeCandia et al., Dynamo: Amazon's Highly Available Key-value Store, SOSP 2007 — https://www.cs.cornell.edu/courses/cs5414/2017fa/papers/dynamo.pdf
14. Eisenbud et al., Maglev: A Fast and Reliable Software Network Load Balancer, NSDI 2016 — https://www.usenix.org/sites/default/files/nsdi16-paper-eisenbud.pdf
15. Consistent Hashing with Bounded Loads — Google Research blog — https://research.google/blog/consistent-hashing-with-bounded-loads/
