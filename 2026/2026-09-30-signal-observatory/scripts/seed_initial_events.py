import sys
sys.stdout.reconfigure(encoding="utf-8")
from observatory.events import EventLedger, EventMilestone

ledger = EventLedger("data/events")

# 1. Event: Dodge City ICE Operations
ev1 = ledger.create_event(
    event_id="2026-09-dodge-city-ice-operations",
    title="Southwest Kansas ICE Operations & Meatpacking Town Resistance",
    category="civil_action",
    location="Dodge City & Garden City, KS",
    summary=(
        "Late September 2026 federal immigration enforcement deployment in Dodge City and Garden City, KS. "
        "Triggered widespread commercial walkouts, residential vehicle tracking via citizen video, and town-hall protests "
        "highlighting meatpacking industry disruption and community mutual aid."
    ),
    date_start="2026-09-24",
)
ev1.add_milestone(EventMilestone(
    timestamp="2026-09-24 10:15",
    headline="Citizen Alerts on Residential ICE Patrols",
    description="TikTok and Facebook users begin live-documenting unmarked federal law enforcement vehicles roaming neighborhood streets.",
    author="catrachito-mena",
    platform="facebook",
    source_url="https://www.facebook.com/catrachito.mena/videos/202000821203",
    media_path="C:/Users/admir/Desktop/videos/2026-09-24_facebook_catrachito-mena_el-ice-llego-al-suroeste-de-kansas_202000821203.mp4",
))
ev1.add_milestone(EventMilestone(
    timestamp="2026-09-24 14:30",
    headline="Dodge City Town Square Mass Demonstration",
    description="Hundreds of residents gather in central Dodge City holding Mexican and American flags, protesting workplace detentions.",
    author="alexander-hernandez",
    platform="facebook",
    source_url="https://www.facebook.com/alexander.hernandez/videos/218939161532",
    media_path="C:/Users/admir/Desktop/videos/2026-09-24_facebook_alexander-hernandez_dodge-city-protesting-against-ice_218939161532.mp4",
))
ev1.add_milestone(EventMilestone(
    timestamp="2026-09-25 11:00",
    headline="Local Business Shutdowns & Meatpacking Labor Friction",
    description="Local broadcast affiliate KSN-TV reports widespread grocery and restaurant closures as workforce stays home in solidarity.",
    author="ksn-tv",
    platform="youtube",
    source_url="https://www.youtube.com/watch?v=g_aaa83Cr1g",
    media_path="C:/Users/admir/Desktop/videos/2026-09-24_youtube_ksn-tv_ice-presence-in-sw-kansas-prompts-closures_g_aaa83Cr1g.mp4",
))
ev1.add_milestone(EventMilestone(
    timestamp="2026-09-26 16:45",
    headline="Cattle & Meatpacking Supply Chain Warning",
    description="TikTok creator warns that continued agricultural and packing plant raids will trigger regional food distribution crisis.",
    author="doris-medrano40",
    platform="tiktok",
    source_url="https://www.tiktok.com/@doris-medrano40/video/583024160146",
    media_path="C:/Users/admir/Desktop/videos/2026-09-26_tiktok_doris-medrano40_ganaderos-advierten-crisis-alimentaria_583024160146.mp4",
))
ledger.save_event(ev1)

# 2. Event: Westport Security Privatization Conflict
ev2 = ledger.create_event(
    event_id="2026-08-westport-security-privatization",
    title="Westport Security Privatization & Weapon Detection Conflict",
    category="public_safety",
    location="Westport, Kansas City, MO",
    summary=(
        "Ongoing tension in Kansas City's historic entertainment district over pedestrian sidewalk privatization, "
        "weapon detection screening gates, cover charges, and violent confrontations between private security guards and patrons."
    ),
    date_start="2021-06-04",
)
ev2.add_milestone(EventMilestone(
    timestamp="2021-06-04 18:00",
    headline="City Approves Weekend Sidewalk Privatization & Metal Detectors",
    description="Westport Community Improvement District institutes perimeter metal detectors on weekend nights from 11 PM to 3 AM.",
    author="andres-gutierrez",
    platform="facebook",
    source_url="https://www.facebook.com/andres.gutierrez/videos/666012690803",
    media_path="C:/Users/admir/Desktop/videos/2021-06-04_facebook_andres-gutierrez_starting-this-weekend-those-who-plan-to-visit_666012690803.mp4",
))
ev2.add_milestone(EventMilestone(
    timestamp="2026-02-21 07:57",
    headline="Morning Westport Corridor Police Shooting",
    description="Early morning gunfire incident along the bar strip documented by local creators.",
    author="cvbudd",
    platform="tiktok",
    source_url="https://www.tiktok.com/@cvbudd/video/7612297628537064735",
))
ev2.add_milestone(EventMilestone(
    timestamp="2026-08-11 02:30",
    headline="Viral 'War Zone' Backlash & Late-Night Disorder",
    description="TikTok creator @kansascitydrill uploads viral video alleging overnight chaos and deteriorating safety within the district.",
    author="kansascitydrill",
    platform="tiktok",
    source_url="https://www.tiktok.com/@kansascitydrill/video/577130163487",
    media_path="C:/Users/admir/Desktop/videos/2026-08-11_tiktok_kansascitydrill_westport-kansas-city-turnt-into-a-warzone-ove_577130163487.mp4",
))
ev2.add_milestone(EventMilestone(
    timestamp="2026-08-28 23:45",
    headline="Private Security Guard Brawls Caught on Camera",
    description="Eyewitness footage surfaces showing physical brawls involving contracted district security guards outside bar entrances.",
    author="Trash Media Group",
    platform="facebook",
    source_url="https://www.facebook.com/TrashMediaGroup/videos/699868198332317",
))
ledger.save_event(ev2)

# 3. Event: KC Underground Rave & Latin EDM Movement
ev3 = ledger.create_event(
    event_id="2026-08-kc-underground-rave-movement",
    title="Kansas City Underground Rave & Latin Electronic Decentralization",
    category="cultural",
    location="West Bottoms & East Crossroads, Kansas City, MO",
    summary=(
        "Following the closure of legacy clubs, KC's underground dance community decentralizes into industrial warehouse raves, "
        "open-air block parties (NOMADA / Barraca), sub-basement DIY spaces (Farewell, Nighthawk), and a surging Latin rave movement."
    ),
    date_start="2025-11-28",
)
ev3.add_milestone(EventMilestone(
    timestamp="2025-11-28 22:00",
    headline="El Desmadre Launches 'Midwest's Biggest Latin Rave' in KC",
    description="Latin EDM and hard reggaeton rave movement packs halls across KC, fusing tech-house and tribal beats.",
    author="eldesmadreparty",
    platform="tiktok",
    source_url="https://www.tiktok.com/@eldesmadreparty/video/7577831125704363319",
    media_path="C:/Users/admir/Desktop/videos/2025-11-28_tiktok_eldesmadreparty_kansas-city-tomorrow-the-midwests-biggest-lat_125704363319.mp4",
))
ev3.add_milestone(EventMilestone(
    timestamp="2026-03-02 21:30",
    headline="Ravers Document Subcultural Surge Post-Riot Room",
    description="Eyewitness raver video confirms booming underground attendance: 'In case u didn't know the rave scene in KC is very much alive.'",
    author="xhvlinax",
    platform="tiktok",
    source_url="https://www.tiktok.com/@xhvlinax/video/7612500426209889566",
    media_path="C:/Users/admir/Desktop/videos/2026-03-02_tiktok_xhvlinax_incase-u-didnt-know-the-rave-scene-in-kc-is-v_426209889566.mp4",
))
ev3.add_milestone(EventMilestone(
    timestamp="2026-07-29 23:00",
    headline="NOMADA Block Party: Azzecca Live Set",
    description="Over 1,000 ravers fill the industrial corridor for a 1-hour underground set by international selector Azzecca.",
    author="NOMADA",
    platform="youtube",
    source_url="https://www.youtube.com/watch?v=uyRJ5L-xIJg",
    media_path="C:/Users/admir/Desktop/videos/2026-07-29_youtube_nomada_azzecca-live-from-the-nomada-block-party-kans_uyRJ5L-xIJg.mp4",
))
ev3.add_milestone(EventMilestone(
    timestamp="2026-08-15 23:30",
    headline="Barraca Recap: Osunlade Industrial Warehouse Set",
    description="Deep house pioneer Osunlade headlines Barraca in KC with full custom sound and visual rigging.",
    author="NOMADA",
    platform="youtube",
    source_url="https://www.youtube.com/watch?v=747X9bVoFys",
    media_path="C:/Users/admir/Desktop/videos/2026-09-09_youtube_nomada_barraca-recap-osunlade-august-2026-kansas-cit_747X9bVoFys.mp4",
))
ledger.save_event(ev3)

print("✓ Successfully initialized 3 real tracked events into data/events/")
