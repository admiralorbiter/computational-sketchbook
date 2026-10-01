import asyncio
import sys
from observatory.collectors.youtube import YouTubeCollector

sys.stdout.reconfigure(encoding='utf-8')

video_ids = [
    ('NDGvQIAENPs', 'FOX4: Independence 4-Day Week Parents Voice Concerns'),
    ('dlQqImDEyC8', 'KMBC: Independence Voters to Decide 4-Day Week'),
    ('8b-JNBiT9C0', 'KC Star: Shawnee Mission Teachers Demand Lighter Workload'),
    ('7_s-hplSHH0', 'FOX4: Hickman Mills Cuts 70+ Jobs & Closes Schools'),
    ('hmCvEDEBc7A', 'FOX4: Shawnee Mission North Student Walkout Protest')
]

async def harvest():
    yt = YouTubeCollector()
    for vid, title in video_ids:
        print(f"=== HARVESTING COMMENTS FOR: {title} ({vid}) ===")
        try:
            comments, raw = await yt.fetch_comments(vid, max_comments=30)
            print(f"Found {len(comments)} comments:")
            for c in comments[:10]:
                text_clean = ' '.join(c.text.split())
                print(f"  * @{c.author_handle}: \"{text_clean}\"")
        except Exception as e:
            print(f"Error fetching comments: {e}")
        print()

asyncio.run(harvest())
