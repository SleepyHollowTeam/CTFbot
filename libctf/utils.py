import feedparser
from datetime import datetime

def get_next_ctfs(l):
    feeds = feedparser.parse("https://ctftime.org/event/list/upcoming/rss/")['entries']
    print(f"[^] Got {len(feeds)} entries.")
    msg = ""
    for i in range(int(l)):
        if "On-line" in feeds[i]['summary']:
            date_start = datetime.fromisoformat(feeds[i]['start_date'])
            date_end = datetime.fromisoformat(feeds[i]['finish_date'])
            msg += f"{feeds[i]['title']} => {feeds[i]['weight']}\n - {feeds[i]['link']} ({feeds[i]['format_text']})\n - starts: {date_start}\n - ends:   {date_end}\n\n"
    return msg

