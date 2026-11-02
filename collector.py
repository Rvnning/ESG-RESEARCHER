import feedparser
import urllib.parse
from datetime import datetime, timezone, timedelta
import os
import re

# 한국 시간(KST) 설정
KST = timezone(timedelta(hours=9))
today = datetime.now(KST).strftime('%Y-%m-%d')

# 검색 키워드 설정 (원하는 키워드로 자유롭게 수정 가능)
QUERY = 'ESG OR "탄소중립" OR "재생에너지 규제" OR "RE100"'
encoded_query = urllib.parse.quote(QUERY)
RSS_URL = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

def clean_html(raw_html):
    """요약문에 포함된 불필요한 HTML 태그 제거"""
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    return re.sub(cleanr, '', raw_html).strip()

def fetch_esg_news(max_items=5):
    feed = feedparser.parse(RSS_URL)
    articles = []
    for entry in feed.entries[:max_items]:
        title = entry.title
        link = entry.link
        pub_date = entry.get('published', '')
        summary = clean_html(entry.get('summary', ''))
        
        articles.append({
            'title': title,
            'link': link,
            'pub_date': pub_date,
            'summary': summary
        })
    return articles

def update_markdown(articles, filename="esg_archive.md"):
    if not articles:
        print("수집된 기사가 없습니다.")
        return

    # 오늘 날짜의 마크다운 블록 생성
    new_section = f"## 📅 {today} ESG 및 규제 동향\n\n"
    for idx, art in enumerate(articles, 1):
        new_section += f"### {idx}. [{art['title']}]({art['link']})\n"
        new_section += f"- **발행일:** {art['pub_date']}\n"
        new_section += f"- **요약:** {art['summary']}\n\n"
    new_section += "---\n\n"

    # 기존 파일이 있으면 오늘 내용을 맨 위에 추가 (최신순 정렬)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_content = f.read()
        
        # 헤더 이후에 새로운 섹션 삽입
        header = "# 🌱 ESG 및 규제 일일 아카이브\n\n"
        if existing_content.startswith(header):
            body = existing_content[len(header):]
            updated_content = header + new_section + body
        else:
            updated_content = header + new_section + existing_content
    else:
        updated_content = "# 🌱 ESG 및 규제 일일 아카이브\n\n" + new_section

    with open(filename, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    news_list = fetch_esg_news(max_items=5)
    update_markdown(news_list)
    print(f"[{today}] ESG 뉴스 아카이빙 완료 ({len(news_list)}건)")
