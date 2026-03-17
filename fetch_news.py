import feedparser
import requests
from datetime import datetime, timedelta

# 设置代理
proxies = {
    'http': 'http://sys-proxy-rd-relay.byted.org:8118',
    'https': 'http://sys-proxy-rd-relay.byted.org:8118'
}

def fetch_ai_news():
    # 可靠的AI新闻RSS源
    rss_urls = [
        'https://feeds.feedburner.com/TechCrunch/',
        'https://www.wired.com/feed/category/ai/latest/rss',
        'https://www.technologyreview.com/feed/',
        'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml'
    ]
    
    news = []
    two_days_ago = datetime.now() - timedelta(days=2)
    
    for url in rss_urls:
        try:
            # 使用代理获取RSS
            response = requests.get(url, proxies=proxies, timeout=10)
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:5]:  # 每个源取5条最新新闻
                # 检查发布时间
                try:
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6])
                        if pub_date < two_days_ago:
                            continue
                except:
                    pass
                
                news.append({
                    'title': entry.title,
                    'source': feed.feed.get('title', 'Unknown'),
                    'link': entry.link
                })
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    # 去重并按相关性排序
    seen = set()
    unique_news = []
    for item in news:
        if item['title'] not in seen:
            seen.add(item['title'])
            # 优先显示包含AI相关关键词的新闻
            ai_keywords = ['AI', 'artificial intelligence', 'machine learning', 'LLM', 'generative AI']
            score = sum(1 for keyword in ai_keywords if keyword.lower() in item['title'].lower())
            unique_news.append((-score, item))  # 负分以便升序排序
    
    # 按相关性排序
    unique_news.sort()
    return [item for (score, item) in unique_news][:10]  # 返回前10条

if __name__ == '__main__':
    news = fetch_ai_news()
    print("📰 最近两天AI行业关键新闻:")
    print("="*60)
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")
        print(f"   来源: {item['source']}")
        print(f"   链接: {item['link']}")
        print()