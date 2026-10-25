"""
Mock and Seed Data for SlothFeed
Realistic unread tabs hoarded by developers and engineers for instant evaluation.
"""

from typing import List, Dict, Any

SEED_ARTICLES: List[Dict[str, Any]] = [
    {
        "id": "tab-gemma-2-launch",
        "title": "Google DeepMind Unveils Gemma 2: High Efficiency Open Weights with 2B and 9B Architectures",
        "url": "https://deepmind.google/technologies/gemma/gemma-2-announcement",
        "category": "AI & Models",
        "author": "Google DeepMind Team",
        "raw_content": """
        Today, we are thrilled to release Gemma 2, the next generation of our open model family built from the same research and technology used to create the Gemini models. Available in both 9B and 27B parameter sizes, along with a lightweight 2B parameter version engineered specifically for on-device and edge deployment, Gemma 2 delivers industry-leading performance per parameter.

        Key Architectural Innovations:
        1. Sliding Window Attention: We alternate between local sliding window attention (window size of 4096 tokens) and global attention across layers. This dramatically reduces memory overhead for long context windows while preserving associative reasoning.
        2. Knowledge Distillation: Instead of training from scratch on next-token prediction alone, smaller models like the 2B and 9B variants are distilled from larger teacher models, resulting in exceptional reasoning capabilities that punch significantly above their weight class.
        3. Grouped-Query Attention (GQA): Both the 9B and 2B variants employ GQA with 8 key-value heads, allowing high-throughput inference on modest hardware, including cloud containers with limited VRAM or pure CPU environments.
        4. Safety and Responsibility: Pre-trained with extensive data filtering and fine-tuned using RLHF and Constitutional AI principles to minimize toxicity and hallucinations.

        For developers building autonomous agents, summarization daemons, and low-latency APIs, Gemma 2 2B can run comfortably in less than 2GB of RAM when quantized to 4-bit or 8-bit precision. It is compatible with Hugging Face transformers, llama.cpp, vLLM, and Ollama out of the box.
        """,
        "tags": ["AI", "Gemma", "DeepMind", "OpenSource"]
    },
    {
        "id": "tab-rust-rewrite-hype",
        "title": "Why Our Team Decided to Rewrite Our Entire Microservices Stack in Rust (Again) in 2026",
        "url": "https://medium.com/overengineered-tech/rewrite-everything-in-rust-again-2026",
        "category": "Tech Opinion",
        "author": "The Over-Optimizing Architect",
        "raw_content": """
        It all started on a lazy Tuesday afternoon during a sprint retrospective. Our Go microservices were running at 15 milliseconds latency, our AWS bill was well within budget, and our uptime was 99.98%. But something felt wrong: the memory usage of our CRUD microservice hovered around 48 megabytes. 

        Why settle for 48 megabytes when Rust could do it in 6 megabytes? 

        Over the past 14 months, our seven-person senior engineering squad spent 3,200 billable engineering hours converting 42 Go repositories into pristine, zero-cost abstraction Rust crates. We battled the borrow checker daily. We wrote 400 lines of trait implementations just to parse a nullable JSON timestamp. We dealt with 45-minute compile times on GitHub Actions.

        The results? Our latency dropped from 15ms to 12ms. Our cloud bill dropped by $38 a month. Meanwhile, we missed our Q2 product roadmap, delayed our Series B customer features, and two frontend engineers quit because our backends took so long to compile locally during end-to-end testing. But our binaries are statically linked and memory safe!
        """,
        "tags": ["Rust", "Hype", "Architecture", "Engineering"]
    },
    {
        "id": "tab-render-blueprints",
        "title": "Mastering Render Blueprints: Multi-Service Infrastructure-as-Code for Production",
        "url": "https://render.com/docs/blueprint-spec-iac-guide",
        "category": "Cloud Infra",
        "author": "Render DevRel Team",
        "raw_content": """
        Render Blueprints allow engineering teams to define their complete infrastructure stack—web services, background workers, cron jobs, managed Redis instances, and PostgreSQL databases—declaratively inside a single `render.yaml` file located in the root of their Git repository.

        Core Advantages of the Blueprint Specification:
        1. Unified Monorepo & Polyrepo Support: You can spin up both a public-facing API web service and an asynchronous queue-draining background worker from the same container image or distinct directories.
        2. Automatic Environment Variable Sync: Pass dynamic database connection strings (`fromDatabase: { name: my-db, property: connectionString }`) or inter-service secrets across containers without manual copy-pasting.
        3. Native Health Checks: Define `healthCheckPath: /health` so Render ensures zero-downtime rolling deploys and automatic traffic rollback if a service fails during startup.
        4. Disk Persistence & Static Hosting: Mount persistent disks for model weight caches or SQLite storage, and define CDN-backed static sites alongside Docker runtimes.

        With Render's free and starter tiers, developers can deploy full-stack AI pipelines—combining a frontend UI with a lightweight quantized LLM backend—with zero configuration drift.
        """,
        "tags": ["Render", "DevOps", "Infrastructure", "Docker"]
    },
    {
        "id": "tab-10x-productivity-hacks",
        "title": "12 Ultra-Hyper Morning Habits of 100x Engineers That Will Change Your Life Before 6 AM",
        "url": "https://lifehacker-tech-guru.blog/12-habits-of-100x-engineers",
        "category": "Productivity Clickbait",
        "author": "Grindset Guru",
        "raw_content": """
        Are you waking up at 7:30 AM like an ordinary developer? If so, you are already falling behind. The most elite 100x software engineers start their day at 3:45 AM with an ice bath followed by 45 minutes of cold-pressed celery juice and binaural beats.

        Habit 1: Never check Slack before writing 1,000 lines of assembly code.
        Habit 2: Stand on a balance board while reviewing PRs to engage your core stabilizing muscles.
        Habit 3: Use an ergonomic mechanical keyboard with 80-gram tactile springs to burn calories while typing variable names.
        Habit 4: Drink 3 liters of matcha tea infused with lion's mane mushroom extracts to stimulate dopamine neurogenesis.
        Habit 5: Fast for 22 hours every single day and only eat fermented kale chips.
        Habit 6: Color code your IDE theme according to the circadian rhythm of your local time zone.

        By incorporating these 12 revolutionary lifestyle adjustments into your daily routine, you will instantly double your salary, eliminate all syntax errors, and achieve peak cognitive flow.
        """,
        "tags": ["Productivity", "Clickbait", "Lifestyle"]
    },
    {
        "id": "tab-distributed-raft-paxos",
        "title": "Distributed Consensus in Practice: What Real Production Outages Taught Us About Raft",
        "url": "https://systems-internals.dev/raft-vs-paxos-lessons-from-the-trenches",
        "category": "Systems & Reliability",
        "author": "Distributed Systems Group",
        "raw_content": """
        While academic literature presents the Raft consensus algorithm as 'understandable Paxos', operating Raft clusters under partition turbulence, asymmetric packet loss, and disk stalls reveals subtle operational landmines.

        Key findings from 5 years of running 3-node and 5-node Raft state machines:
        1. Pre-Vote Protocol is Essential: Without the Pre-Vote phase, a network-partitioned node whose term increments continuously during isolation will disrupt the healthy cluster upon reconnection by forcing a cluster-wide leader election.
        2. Disk Fsync Latency Spikes: Raft requires persisting state (`currentTerm` and `votedFor`) before replying to RequestVote RPCs. Cloud SSD p99 write stalls can easily exceed heartbeat election timeouts, triggering phantom split-brain elections.
        3. Joint Consensus for Membership Changes: Simple single-server additions are safe, but multi-node cluster reconfigurations require 2-phase joint consensus to prevent overlapping quorums from electing dual leaders.
        4. Log Compaction Backpressure: Taking snapshots must be asynchronous and throttled; snapshotting directly on the log replication thread blocks the leader from acknowledging in-flight client writes.

        If you are evaluating consensus implementations, ensure your engine supports pre-vote and pipelined log append entries to avoid cascade election storms.
        """,
        "tags": ["Distributed Systems", "Raft", "Database", "SRE"]
    },
    {
        "id": "tab-css-subgrid-2026",
        "title": "CSS Subgrid Is Everywhere Now: Fixing Nested Grid Alignment Without Javascript Hacks",
        "url": "https://webstandards.org/articles/css-subgrid-practical-guide",
        "category": "Frontend & CSS",
        "author": "Web Layout Specialist",
        "raw_content": """
        For years, CSS Grid users faced a common pain point: nested child elements could not participate in the grid tracks defined by their outer parent container. Developers resorted to fixed heights, flexbox workarounds, or messy JavaScript resize observers just to keep card titles and buttons aligned across multiple columns.

        With baseline cross-browser support across Chrome, Firefox, Safari, and Edge, CSS Subgrid solves this natively with one property: `grid-template-rows: subgrid;` or `grid-template-columns: subgrid;`.

        How it works:
        - When a child element specifies `display: grid; grid-template-rows: subgrid;`, it inherits the exact row sizing and gap rules of the parent container.
        - Card headers, body text, and footers align perfectly across all cards in a grid row regardless of differing content lengths.
        - Reduces layout shift (CLS) and removes thousands of lines of fragile flex alignment hacks.
        
        Recommended action: If your project still uses JavaScript height equalization libraries or awkward padding shims for cards, migrate them to `subgrid` today.
        """,
        "tags": ["CSS", "WebDev", "Frontend", "Standards"]
    }
]


def get_mock_articles() -> List[Dict[str, Any]]:
    """Returns a fresh copy of the seed articles."""
    import copy
    return copy.deepcopy(SEED_ARTICLES)
