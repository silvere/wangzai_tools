import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 设置代理
proxies = {
    'http': 'http://sys-proxy-rd-relay.byted.org:8118',
    'https': 'http://sys-proxy-rd-relay.byted.org:8118'
}

def fetch_techcrunch_ai():
    url = "https://techcrunch.com/category/artificial-intelligence/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, proxies=proxies, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = []
    for article in soup.find_all('article', class_='post-block post-block--image post-block--unread')[:10]:
        try:
            title = article.find('h2', class_='post-block__title').get_text(strip=True)
            link = article.find('a', class_='post-block__title__link')['href']
            date = article.find('time')['datetime']
            
            # 检查是否在最近两天内
            pub_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            if pub_date < datetime.now(tz=pub_date.tzinfo) - timedelta(days=2):
                continue
                
            articles.append({
                'title': title,
                'link': link,
                'date': pub_date.strftime('%Y-%m-%d %H:%M')
            })
        except Exception as e:
            continue
    
    return articles

if __name__ == '__main__':
    print("📰 TechCrunch最近两天AI行业关键新闻:")
    print("="*60)
    
    articles = fetch_techcrunch_ai()
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"📅 {article['date']}")
        print(f"🔗 {article['link']}")
        print()