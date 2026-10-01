import sys
from observatory.store.corpus import CorpusStore
from observatory.models import Artifact, Platform, ContentType, DiscoveryMethod

sys.stdout.reconfigure(encoding='utf-8')
corpus = CorpusStore()

RUN_ID = "run_2026-10-kumed-grants-townhalls"

artifacts_data = [
    {
        "url": "https://www.wsj.com/opinion/federal-research-funding-nih-delays-universities-girod-daniels-2026",
        "title": "Wall Street Journal Op-Ed: The Looming Collapse of American Biomedical Research Funding",
        "body": "Chancellor Douglas Girod (KU) and President Ron Daniels (Johns Hopkins) warn that halfway through FY2026, the NIH has disbursed only 33% of its typical $26 billion in awards. At KU, new research awards plunged by $182 million year-over-year by Q3 FY2026, stranding clinical trials and postdoctoral positions.",
        "platform": Platform.WEB,
        "author": "chancellor_douglas_girod"
    },
    {
        "url": "https://davids.house.gov/media/press-releases/davids-leads-bipartisan-push-to-unfreeze-nih-grants-ku",
        "title": "Rep. Sharice Davids Leads 39-Member Congressional Inquiry to HHS Secretary RFK Jr. on NIH Funding Bottleneck",
        "body": "U.S. Rep. Sharice Davids and 38 congressional colleagues demand answers regarding administrative staffing shortages and policy freezes at HHS/NIH that caused a $182M deficit in expected grant funding at the University of Kansas Medical Center and Lawrence campuses.",
        "platform": Platform.WEB,
        "author": "rep_sharice_davids"
    },
    {
        "url": "https://news.ku.edu/news/article/nsf-awards-26m-for-earth-engineering-research-center",
        "title": "NSF Awards $26 Million to KU to Launch EARTH Gen-4 Engineering Research Center",
        "body": "The National Science Foundation awards $26 million (renewable up to $52M over 10 years) to establish the Environmentally Applied Refrigerant Technology Hub (EARTH) led by Professor Mark Shiflett at KU Lawrence, partnering with Notre Dame, Maryland, Hawaii, and South Dakota.",
        "platform": Platform.WEB,
        "author": "ku_news_service"
    },
    {
        "url": "https://provost.ku.edu/virtual-town-halls-spring-2026-one-ku-framework",
        "title": "Provost Arash Mafi Hosts Spring 2026 Monthly Virtual Town Halls on One KU Strategic Framework",
        "body": "From January to May 2026, Provost Arash Mafi and Chief Strategy Officer Corinne Bannon host monthly campus town halls to present the draft One KU Strategic Framework. Faculty raise pointed concerns over indirect cost cuts, shared governance erosion, and administrative centralization.",
        "platform": Platform.WEB,
        "author": "office_of_the_provost"
    },
    {
        "url": "https://uaku.org/updates/uaku-ratifies-historic-first-contract-april-2026",
        "title": "United Academics of KU (UAKU) Ratifies First Collective Bargaining Agreement",
        "body": "In April 2026, KU faculty and academic staff ratify their first contract, setting a $70,000 salary floor for assistant professors. Union leadership highlights that administration cited constrained budgets and federal indirect cost threats while funding a $400M+ stadium renovation.",
        "platform": Platform.WEB,
        "author": "united_academics_ku"
    },
    {
        "url": "https://graduate.ku.edu/funding-stipends-gta-gra-rates-2025-2026",
        "title": "KU Graduate Studies 2025-2026 Academic Year GRA and GTA Base Stipend Schedule",
        "body": "KU sets minimum 0.50 FTE GRA/GTA salary at $20,084.01 per academic year. Graduate researchers on NSF and NIH grants report severe cost-of-living strain as rent in Lawrence and Kansas City surges, contrasting with unionized GTA protections under GTAC/AFT-KS.",
        "platform": Platform.WEB,
        "author": "ku_graduate_studies"
    }
]

arts = []
for d in artifacts_data:
    art = Artifact(
        native_id=d["url"],
        platform=d["platform"],
        content_type=ContentType.POST,
        author_handle=d["author"],
        published_at="2026-10-01T12:00:00Z",
        text=f"{d['title']}\n\n{d['body']}",
        canonical_url=d["url"],
        discovery_method=DiscoveryMethod.SEARCH,
        run_id=RUN_ID,
    )
    arts.append(art)

saved = corpus.store_artifacts(arts)
print(f"Successfully stored {saved} high-precision grant and town hall artifacts in corpus!")
