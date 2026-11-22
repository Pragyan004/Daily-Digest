"""
mock_data.py — Generates realistic mock digest articles for --mock mode.
"""

import hashlib
from datetime import datetime, timedelta, timezone


def _id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def _ts(hours_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def generate_mock_articles() -> list[dict]:
    """Return 14 realistic sample articles across all 4 categories."""

    articles = [
        # ── Cybersecurity (7 articles, some with CVEs, some without images) ──
        {
            "category": "Cybersecurity",
            "source": "The Hacker News",
            "title": "Critical Zero-Day in Palo Alto PAN-OS Exploited in the Wild",
            "hook": "Attackers actively exploit a critical PAN-OS zero-day to compromise enterprise firewalls worldwide.",
            "bullets": [
                "CVSS 10.0 flaw allows unauthenticated remote code execution",
                "Palo Alto urges immediate patching of all affected devices",
            ],
            "why_it_matters": "Thousands of internet-facing firewalls are vulnerable, putting corporate networks at immediate risk.",
            "read_time_sec": 210,
            "image_url": "https://thehackernews.com/images/panos-zero-day-2026.jpg",
            "full_article_url": "https://thehackernews.com/2026/11/panos-zero-day-rce.html",
            "hours_ago": 2.5,
            "cve_ids": ["CVE-2026-47123"],
        },
        {
            "category": "Cybersecurity",
            "source": "Krebs on Security",
            "title": "Ransomware Gang 'BlackStar' Leaks 2TB of Hospital Records",
            "hook": "BlackStar ransomware group publishes millions of patient records after failed negotiations.",
            "bullets": [
                "Three US hospital chains affected across twelve states",
                "FBI and CISA issue joint advisory on healthcare targeting",
            ],
            "why_it_matters": "Healthcare remains the top ransomware target, and this breach exposes deeply sensitive patient data.",
            "read_time_sec": 300,
            "image_url": None,
            "full_article_url": "https://krebsonsecurity.com/2026/11/blackstar-hospital-leak/",
            "hours_ago": 4.0,
            "cve_ids": [],
        },
        {
            "category": "Cybersecurity",
            "source": "SecurityWeek",
            "title": "CISA Adds Three Actively Exploited Vulnerabilities to KEV Catalog",
            "hook": "Federal agencies must patch three new KEV entries within two weeks.",
            "bullets": [
                "Flaws impact Microsoft Exchange, Fortinet, and Apache Struts",
                "Exploitation observed by multiple nation-state threat actors",
            ],
            "why_it_matters": "KEV additions trigger mandatory federal patching deadlines and signal broad exploitation campaigns.",
            "read_time_sec": 180,
            "image_url": "https://www.securityweek.com/wp-content/uploads/2026/11/kev-catalog.png",
            "full_article_url": "https://www.securityweek.com/cisa-kev-three-new-entries-november/",
            "hours_ago": 5.5,
            "cve_ids": ["CVE-2026-41022", "CVE-2026-38910", "CVE-2026-44501"],
        },
        {
            "category": "Cybersecurity",
            "source": "BleepingComputer",
            "title": "New 'PhantomLoader' Malware Hides in Signed Windows Drivers",
            "hook": "PhantomLoader abuses legitimate driver signatures to evade endpoint detection tools.",
            "bullets": [
                "Malware loads second-stage payload entirely in kernel memory",
                "Researchers link campaign to financially motivated threat group",
            ],
            "why_it_matters": "Signed-driver abuse undermines a core Windows trust model, making detection extremely difficult.",
            "read_time_sec": 240,
            "image_url": "https://www.bleepingcomputer.com/wp-content/uploads/2026/11/phantomloader.jpg",
            "full_article_url": "https://www.bleepingcomputer.com/news/security/phantomloader-signed-drivers/",
            "hours_ago": 6.0,
            "cve_ids": [],
        },
        {
            "category": "Cybersecurity",
            "source": "CISA Advisories",
            "title": "ICS Advisory: Siemens SCALANCE Switches Vulnerable to Auth Bypass",
            "hook": "Critical authentication bypass in Siemens industrial switches threatens OT networks.",
            "bullets": [
                "Unauthenticated attackers can reconfigure switch settings remotely",
                "Siemens releases firmware update addressing the vulnerability",
            ],
            "why_it_matters": "Industrial control system flaws can lead to physical safety incidents in critical infrastructure.",
            "read_time_sec": 150,
            "image_url": None,
            "full_article_url": "https://www.cisa.gov/news-events/ics-advisories/icsa-26-327-01",
            "hours_ago": 8.0,
            "cve_ids": ["CVE-2026-50112"],
        },
        {
            "category": "Cybersecurity",
            "source": "The Hacker News",
            "title": "Google Patches Seventh Chrome Zero-Day of 2026",
            "hook": "Google ships emergency Chrome update fixing actively exploited V8 vulnerability.",
            "bullets": [
                "Type-confusion bug in V8 engine allows sandbox escape",
                "Users urged to update Chrome to version 131.0.6778.86 immediately",
            ],
            "why_it_matters": "Browser zero-days remain a primary vector for targeted espionage and drive-by download attacks.",
            "read_time_sec": 160,
            "image_url": "https://thehackernews.com/images/chrome-zeroday-7.png",
            "full_article_url": "https://thehackernews.com/2026/11/chrome-seventh-zero-day-v8.html",
            "hours_ago": 3.0,
            "cve_ids": ["CVE-2026-48877"],
        },
        {
            "category": "Cybersecurity",
            "source": "Krebs on Security",
            "title": "Major US Bank Discloses Supply-Chain Breach via Third-Party Payroll Provider",
            "hook": "A leading bank reveals customer data exposure linked to a compromised payroll vendor.",
            "bullets": [
                "Social security numbers and account details of 1.2M customers exposed",
                "Third-party risk management failures highlighted by regulators",
            ],
            "why_it_matters": "Supply-chain attacks on financial services amplify the blast radius far beyond the initial target.",
            "read_time_sec": 270,
            "image_url": None,
            "full_article_url": "https://krebsonsecurity.com/2026/11/bank-supply-chain-breach/",
            "hours_ago": 7.0,
            "cve_ids": [],
        },
        # ── Technology (3 articles) ──
        {
            "category": "Technology",
            "source": "Currents API",
            "title": "OpenAI Unveils GPT-5 With Native Multimodal Reasoning",
            "hook": "GPT-5 brings real-time video understanding and step-by-step scientific reasoning to ChatGPT.",
            "bullets": [
                "New model scores 92% on graduate-level science benchmarks",
                "Available to Plus subscribers starting next week globally",
            ],
            "why_it_matters": "GPT-5 sets a new bar for AI capability and will accelerate enterprise AI adoption across industries.",
            "read_time_sec": 200,
            "image_url": "https://cdn.currentsapi.services/images/openai-gpt5-launch.jpg",
            "full_article_url": "https://techcrunch.com/2026/11/22/openai-gpt5-multimodal/",
            "hours_ago": 1.5,
            "cve_ids": [],
        },
        {
            "category": "Technology",
            "source": "Currents API",
            "title": "Apple Launches M5 MacBook Pro With 'Liquid Neural Engine'",
            "hook": "Apple's M5 chip doubles AI inference speed with a dedicated on-chip neural accelerator.",
            "bullets": [
                "New 16-core Neural Engine handles 40B-parameter models locally",
                "Battery life reaches 28 hours for the 16-inch model",
            ],
            "why_it_matters": "On-device AI processing reduces cloud dependency and brings powerful ML workflows to every developer.",
            "read_time_sec": 180,
            "image_url": "https://cdn.currentsapi.services/images/apple-m5-macbook.jpg",
            "full_article_url": "https://www.apple.com/newsroom/2026/11/m5-macbook-pro/",
            "hours_ago": 3.5,
            "cve_ids": [],
        },
        {
            "category": "Technology",
            "source": "Currents API",
            "title": "EU Passes Landmark AI Liability Directive Effective January 2027",
            "hook": "The EU finalizes rules making AI providers legally liable for damages caused by their systems.",
            "bullets": [
                "Providers must carry insurance for high-risk AI applications",
                "Non-compliance penalties reach up to 6% of global annual revenue",
            ],
            "why_it_matters": "This directive reshapes AI deployment economics and compliance requirements for global tech companies.",
            "read_time_sec": 220,
            "image_url": None,
            "full_article_url": "https://ec.europa.eu/ai-liability-directive-2026/",
            "hours_ago": 5.0,
            "cve_ids": [],
        },
        # ── Business (2 articles) ──
        {
            "category": "Business",
            "source": "Currents API",
            "title": "NVIDIA Surpasses $5 Trillion Market Cap on Record AI Chip Demand",
            "hook": "NVIDIA becomes the world's most valuable company as data center GPU revenue triples.",
            "bullets": [
                "Q3 earnings beat estimates with $48B in data center revenue",
                "Blackwell GPU architecture drives 90% of new AI cluster orders",
            ],
            "why_it_matters": "NVIDIA's dominance signals that enterprise AI infrastructure spending is still accelerating sharply.",
            "read_time_sec": 190,
            "image_url": "https://cdn.currentsapi.services/images/nvidia-5t-marketcap.jpg",
            "full_article_url": "https://www.reuters.com/business/nvidia-5-trillion-market-cap-2026/",
            "hours_ago": 2.0,
            "cve_ids": [],
        },
        {
            "category": "Business",
            "source": "Currents API",
            "title": "Federal Reserve Signals Pause on Rate Cuts Amid Sticky Inflation Data",
            "hook": "The Fed holds rates steady as November inflation figures come in above expectations.",
            "bullets": [
                "Core CPI rose 0.4% month-over-month versus 0.3% forecast",
                "Markets now price in no further cuts until at least Q2 2027",
            ],
            "why_it_matters": "A prolonged rate pause affects borrowing costs, tech valuations, and startup funding conditions.",
            "read_time_sec": 170,
            "image_url": None,
            "full_article_url": "https://www.bloomberg.com/news/fed-rate-pause-november-2026/",
            "hours_ago": 6.5,
            "cve_ids": [],
        },
        # ── World (2 articles) ──
        {
            "category": "World",
            "source": "Currents API",
            "title": "India and UK Sign Landmark Free Trade Agreement After Three Years of Talks",
            "hook": "India and the UK finalize a comprehensive trade deal covering goods, services, and digital trade.",
            "bullets": [
                "Tariffs eliminated on 95% of bilateral goods over ten years",
                "Digital trade chapter includes data flow and IP protections",
            ],
            "why_it_matters": "The deal opens major market access for tech services and reshapes post-Brexit UK trade strategy.",
            "read_time_sec": 200,
            "image_url": "https://cdn.currentsapi.services/images/india-uk-fta.jpg",
            "full_article_url": "https://www.bbc.com/news/india-uk-free-trade-agreement-2026/",
            "hours_ago": 4.5,
            "cve_ids": [],
        },
        {
            "category": "World",
            "source": "Currents API",
            "title": "COP31 Reaches Historic Deal to Triple Global Renewable Energy by 2035",
            "hook": "Nearly 200 nations agree to binding renewable energy targets at the COP31 climate summit.",
            "bullets": [
                "Agreement includes $300B annual climate finance for developing nations",
                "Fossil fuel phase-down language strengthened from COP28 pledge",
            ],
            "why_it_matters": "Binding targets and increased financing could meaningfully accelerate the global energy transition.",
            "read_time_sec": 250,
            "image_url": "https://cdn.currentsapi.services/images/cop31-renewables.jpg",
            "full_article_url": "https://www.reuters.com/sustainability/cop31-renewable-energy-deal-2026/",
            "hours_ago": 9.0,
            "cve_ids": [],
        },
    ]

    # Build final article dicts matching the output schema
    result = []
    for a in articles:
        url = a["full_article_url"]
        result.append(
            {
                "id": _id(url),
                "category": a["category"],
                "source": a["source"],
                "title": a["title"],
                "hook": a["hook"],
                "bullets": a["bullets"],
                "why_it_matters": a["why_it_matters"],
                "read_time_sec": a["read_time_sec"],
                "image_url": a["image_url"],
                "full_article_url": url,
                "published_at": _ts(a["hours_ago"]),
                "cve_ids": a["cve_ids"],
                "saved": False,
            }
        )
    return result
