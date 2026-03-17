import time
import json
from playwright.sync_api import sync_playwright

with open('/root/.xiaohongshu/cookies.json') as f:
    cookies = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    context.add_cookies(cookies)
    page = context.new_page()
    
    page.goto('https://creator.xiaohongshu.com/publish/publish', wait_until='networkidle', timeout=60000)
    time.sleep(15)
    
    # Try all possible title selectors
    title_selectors = [
        'input[placeholder="输入标题"]',
        'div[title] input',
        '.title-input input',
        'input[class*="title"]',
        '[contenteditable][placeholder*="标题"]',
    ]
    
    title_filled = False
    for selector in title_selectors:
        if page.locator(selector).count() > 0:
            print(f"Found title with selector: {selector}")
            page.locator(selector).first.fill('测评一下开源AI自动化项目openclaw🔥', timeout=10000)
            title_filled = True
            break
    
    if not title_filled:
        # Dump all inputs for debug
        inputs = page.locator('input').all()
        print(f"Total inputs: {len(inputs)}")
        for i, inp in enumerate(inputs[:10]):
            ph = inp.get_attribute('placeholder')
            print(f"  Input {i}, placeholder: {ph}")
    
    time.sleep(3)
    
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
    
    content_selectors = [
        '.ql-editor',
        'div[contenteditable="true"]',
        '.editor-content',
        '.rich-text',
    ]
    
    content_filled = False
    for selector in content_selectors:
        if page.locator(selector).count() > 0:
            print(f"Found content with selector: {selector}")
            page.locator(selector).first.fill(content, timeout=10000)
            content_filled = True
            break
    
    time.sleep(5)
    
    page.screenshot(path='data/debug-filled.png', full_page=True)
    
    # Remove overlays
    page.evaluate('''() => {
        document.querySelectorAll('.mask, .modal, .popup, .van-overlay').forEach(el => el.remove());
    }''');
    time.sleep(2)
    
    # Scroll bottom
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
    time.sleep(2)
    
    print("Taking screenshot before publish...")
    page.screenshot(path='data/before-publish.png', full_page=True)
    
    # Find and click publish
    publish_selectors = [
        'text=发布',
        'button:has-text("发布")',
        '.publishBtn',
        '.publish-button',
    ]
    
    for selector in publish_selectors:
        if page.locator(selector).count() > 0:
            print(f"Clicking publish with {selector}")
            page.locator(selector).first.click(force=True, timeout=10000)
            break
    
    time.sleep(20)
    
    print(f"Final URL: {page.url}")
    page.screenshot(path='data/final-result.png', full_page=True)
    
    # Save cookies
    new_cookies = context.cookies()
    with open('/root/.xiaohongshu/cookies.json', 'w') as f:
        json.dump(new_cookies, f)
    
    browser.close()
    print("Done!")
