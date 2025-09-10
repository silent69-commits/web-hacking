import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import collections


def extract_links(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set() 
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            full_url = urljoin(url, href) 

           
            if full_url.startswith('http') and not full_url.endswith(('.pdf', '.jpg', '.png', '.css', '.js', '.zip', '.rar', '.exe', '.mp3', '.mp4')):
                links.add(full_url)
        return list(links)
    except requests.exceptions.RequestException as e:
        
        return []


def find_admin_panel(url):
    admin_paths = [
        "/admin", "/login", "/wp-admin", "/administrator", "/dashboard",
        "/panel", "/cpanel", "/webadmin", "/adminpanel", "/controlpanel",
        "/user/login", "/wp-login.php", "/admin.php", "/backend", "/login.php",
        "/manage", "/secure", "/siteadmin", "/webmaster", "/cp", "/control",
        "/site/login", "/access", "/web/admin" 
    ]
    
    
    base_url = url.rstrip('/')

    for path in admin_paths:
        full_url = f"{base_url}{path}"
        try:
            response = requests.head(full_url, allow_redirects=True, timeout=3)
            if response.status_code == 200:
                print(f"[+] پنل ادمین یافت شد: {full_url}")
                return full_url
            elif response.status_code == 301 or response.status_code == 302:
                print(f"[~] ریدایرکت یافت شد، احتمالاً پنل ادمین: {full_url} (کد {response.status_code})")
                return full_url
        except requests.exceptions.RequestException:
            pass
    return None

def web_crawler(start_url, max_depth=2, find_admin=True):
    """
    این تابع به عنوان یک خزنده وب عمل می‌کند و لینک‌ها را استخراج می‌کند.
    همچنین در حین خزیدن، تلاش می‌کند پنل ادمین را نیز پیدا کند.
    """
    queue = collections.deque([(start_url, 0)]) 
    visited_urls = set()
    internal_links = set()
    admin_panel_found = None

    print(f"شروع خزیدن از: {start_url}")
    print(f"حداکثر عمق: {max_depth}")

    while queue and admin_panel_found is None:
        current_url, depth = queue.popleft()

        if current_url in visited_urls:
            continue

        if depth > max_depth:
            continue

       
        if urlparse(current_url).netloc != urlparse(start_url).netloc:
            continue

        visited_urls.add(current_url)
        internal_links.add(current_url)
        print(f"خزیدن: {current_url} (عمق: {depth})")

        
        if find_admin:
            print(f"  تلاش برای یافتن پنل ادمین در: {current_url}")
            panel = find_admin_panel(current_url)
            if panel:
                admin_panel_found = panel
                break 

        links_on_page = extract_links(current_url)
        for link in links_on_page:
            if link not in visited_urls:
               
                if urlparse(link).netloc == urlparse(start_url).netloc:
                    queue.append((link, depth + 1))

    print("\n--- پایان خزیدن ---")
    if admin_panel_found:
        print(f"*** پنل ادمین نهایی یافت شده: {admin_panel_found} ***")
    else:
        print("پنل ادمین با آدرس‌های رایج در طول خزیدن پیدا نشد.")
    
    print("\nلینک‌های داخلی کشف شده:")
    for link in sorted(list(internal_links)):
        print(link)
    
    return internal_links, admin_panel_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("طرز استفاده: python web_crawler.py <URL> [max_depth]")
        print("مثال: python web_crawler.py https://example.com")
        print("مثال با عمق: python web_crawler.py https://example.com 3")
        sys.exit(1)

    target_url = sys.argv[1]
    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        print("لطفاً یک URL معتبر با 'http://' یا 'https://' وارد کنید.")
        sys.exit(1)

    max_depth_input = 2 
    if len(sys.argv) > 2:
        try:
            max_depth_input = int(sys.argv[2])
            if max_depth_input < 0:
                print("عمق نباید منفی باشد. از عمق پیش‌فرض 2 استفاده می‌شود.")
                max_depth_input = 2
        except ValueError:
            print("عمق نامعتبر است. از عمق پیش‌فرض 2 استفاده می‌شود.")
            max_depth_input = 2
    
    web_crawler(target_url, max_depth=max_depth_input, find_admin=True)

