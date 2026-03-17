import time
import json
from playwright.sync_api import sync_playwright

with open('/root/.xiaohongshu/cookies.json') as f:
    cookies = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    context.add_cookies(cookies)
    page = context.new_page()
    
    page.goto('https://creator.xiaohongshu.com/publish/publish', wait_until='networkidle', timeout=60000)
    time.sleep(10)
    
    # Fill title
    page.locator('[placeholder="输入标题"]').first.fill('测评一下开源AI自动化项目openclaw🔥')
    time.sleep(2)
    
    # Fill content
    content = '''测评一下开源AI自动化项目openclaw🔥

最近看到一个挺有意思的开源项目 openclaw，玩了几天来给大家分享一下体验👇

✅ **优点总结**

▫️完全开源免费，代码都在 GitHub，自己可以改
▫️支持小红书等平台自动化互动，模拟真人行为
▫️本地运行，数据隐私都在自己手里，比闭源安全
▫️有文档，部署对开发者还算友好

⚠️ **不适合小白，要注意**

▫️需要自己有服务器，还要会点代码才能部署
▫️平台都有反机器人机制，账号风险自己承担
▫️作者不鼓励违规操作，只是开源给大家学习

💡 **我的感受**

如果你是开发者想研究一下AI自动化，这个项目还是值得star⭐️的，比闭源透明很多，可以自己审计代码，学习一下别人怎么写浏览器自动化。

#openclaw #AI #自动化 #github #开源项目 #大模型'''
    page.locator('.ql-editor').first.fill(content)
    time.sleep(5)
    
    # Close overlays
    page.evaluate('''() => {
        document.querySelectorAll('.mask, .modal, .popup').forEach(el => el.remove());
    }''');
    time.sleep(3)
    
    # Scroll to bottom to see publish button
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
    time.sleep(2)
    
    # Click publish
    page.click('text=发布', force=True, timeout=10000)
    time.sleep(15)
    
    print("Final URL:", page.url)
    page.screenshot(path='data/after-click-publish.png', full_page=True)
    
    # Save cookies
    new_cookies = context.cookies()
    with open('/root/.xiaohongshu/cookies.json', 'w') as f:
        json.dump(new_cookies, f)
    
    browser.close()
