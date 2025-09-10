import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import collections
import os 


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m' 


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def extract_all_links(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_links = set() 

        # Find all <a> tags
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            full_url = urljoin(url, href)
            if full_url.startswith('http'): 
                all_links.add(full_url)
        

        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            full_url = urljoin(url, src)
            if full_url.startswith('http'):
                all_links.add(full_url)


        for link_tag in soup.find_all('link', href=True):
            href = link_tag['href']
            full_url = urljoin(url, href)
            if full_url.startswith('http'):
                all_links.add(full_url)

        
        for script_tag in soup.find_all('script', src=True):
            src = script_tag['src']
            full_url = urljoin(url, src)
            if full_url.startswith('http'):
                all_links.add(full_url)
        
        
        
        return sorted(list(all_links)) # Return as sorted list
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error fetching {url}: {e}{Colors.ENDC}")
        return []


def find_admin_panel(url):
    admin_paths = [
        "/admin", "/login", "/wp-admin", "/administrator", "/dashboard",
        "/panel", "/cpanel", "/webadmin", "/adminpanel", "/controlpanel",
        "/user/login", "/wp-login.php", "/admin.php", "/backend", "/login.php",
        "/manage", "/secure", "/siteadmin", "/webmaster", "/cp", "/control",
        "/site/login", "/access", "/web/admin", "/admin/login", "/cp-login",
        "/admin-login", "/adminarea", "/webmaster/login", "/member/login",
        "/portal", "/staff", "/superadmin" 
    ]
    
   
    base_url = url.rstrip('/')

    found_panels = []
    print(f"\n{Colors.YELLOW}--- Initiating Admin Panel Scan for {base_url} ---{Colors.ENDC}")
    for path in admin_paths:
        full_url = f"{base_url}{path}"
        try:
            print(f"Testing: {full_url} ... ", end='')
            response = requests.head(full_url, allow_redirects=True, timeout=5) 
            
            if response.status_code == 200:
                print(f"{Colors.GREEN}TRUE (200 OK){Colors.ENDC}")
                found_panels.append(full_url)
            elif 300 <= response.status_code < 400: 
                print(f"{Colors.YELLOW}TRUE (Redirect {response.status_code}){Colors.ENDC}")
                found_panels.append(full_url)
            else:
                print(f"{Colors.RED}FALSE ({response.status_code}){Colors.ENDC}")
        except requests.exceptions.RequestException:
            print(f"{Colors.RED}FALSE (Connection Error){Colors.ENDC}")
            pass 
    
    if not found_panels:
        print(f"\n{Colors.BLUE}No common admin panels found for {base_url}.{Colors.ENDC}")
    return found_panels

# Web Crawler function
def web_crawler(start_url, max_depth=2):
    """
    Crawls a website to extract all internal links up to a specified depth.
    """
    queue = collections.deque([(start_url, 0)]) 
    visited_urls = set()
    internal_links_found = set()

    print(f"\n{Colors.YELLOW}--- Starting Web Crawl for {start_url} ---{Colors.ENDC}")
    print(f"Maximum Depth: {max_depth}")

    while queue:
        current_url, depth = queue.popleft()

        if current_url in visited_urls:
            continue
        if depth > max_depth:
            continue
        
        
        if urlparse(current_url).netloc != urlparse(start_url).netloc:
            continue

        visited_urls.add(current_url)
        internal_links_found.add(current_url)
        print(f"{Colors.CYAN}Crawling: {current_url} (Depth: {depth}){Colors.ENDC}")

        
        links_on_page = extract_all_links(current_url)
        for link in links_on_page:
            if link not in visited_urls:
                
                if urlparse(link).netloc == urlparse(start_url).netloc:
                    queue.append((link, depth + 1))
                else:
                    
                    internal_links_found.add(link) 

    print(f"\n{Colors.YELLOW}--- Web Crawl Finished ---{Colors.ENDC}")
    print(f"{Colors.BLUE}Total internal and external links found during crawl: {len(internal_links_found)}{Colors.ENDC}")
    
    print("\n")
    for link in sorted(list(internal_links_found)):
        print(f"{Colors.WHITE}- {link}{Colors.ENDC}")
    
    return sorted(list(internal_links_found)) 


def main():
    clear_screen()
    print(f"{Colors.CYAN}======================================={Colors.ENDC}")
    print(f"{Colors.CYAN}          {Colors.YELLOW}Web Reconnaissance Tool{Colors.ENDC}{Colors.CYAN}    {Colors.ENDC}")
    print(f"{Colors.CYAN}======================================={Colors.ENDC}")
    print(f"{Colors.BLUE}Telegram: @silent_mimi{Colors.ENDC}\n")

    target_url = input(f"{Colors.YELLOW}Enter the target URL (e.g., https://example.com): {Colors.ENDC}").strip()

    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        print(f"{Colors.RED}Invalid URL. Please include 'http://' or 'https://'. Exiting.{Colors.ENDC}")
        sys.exit(1)

    while True:
        print(f"\n{Colors.CYAN}--- Choose an Option ---{Colors.ENDC}")
        print(f"{Colors.GREEN}1. Extract all links (including images, CSS, JS, etc.) and crawl website{Colors.ENDC}")
        print(f"{Colors.GREEN}2. Find Admin Panel{Colors.ENDC}")
        print(f"{Colors.RED}3. Exit{Colors.ENDC}")

        choice = input(f"{Colors.YELLOW}Enter your choice (1, 2, or 3): {Colors.ENDC}").strip()

        if choice == '1':
            try:
                max_depth_input = int(input(f"{Colors.YELLOW}Enter maximum crawl depth (e.g., 2 for shallow, 5 for deeper): {Colors.ENDC}").strip())
                if max_depth_input < 0:
                    print(f"{Colors.RED}Depth cannot be negative. Setting to default (2).{Colors.ENDC}")
                    max_depth_input = 2
            except ValueError:
                print(f"{Colors.RED}Invalid depth. Setting to default (2).{Colors.ENDC}")
                max_depth_input = 2
            
            clear_screen()
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.CYAN}          {Colors.YELLOW}Web Reconnaissance Tool{Colors.ENDC}{Colors.CYAN}    {Colors.ENDC}")
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.BLUE}Telegram: @silent_mimi{Colors.ENDC}\n")
            print(f"{Colors.WHITE}Target URL: {target_url}{Colors.ENDC}")
            print(f"{Colors.WHITE}Max Depth: {max_depth_input}{Colors.ENDC}")
            
            web_crawler(target_url, max_depth=max_depth_input)
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}") 
            clear_screen()
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.CYAN}          {Colors.YELLOW}Web Reconnaissance Tool{Colors.ENDC}{Colors.CYAN}    {Colors.ENDC}")
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.BLUE}Telegram: @silent_mimi{Colors.ENDC}\n")


        elif choice == '2':
            clear_screen()
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.CYAN}          {Colors.YELLOW}Web Reconnaissance Tool{Colors.ENDC}{Colors.CYAN}    {Colors.ENDC}")
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.BLUE}Telegram: @silent_mimi{Colors.ENDC}\n")
            print(f"{Colors.WHITE}Target URL: {target_url}{Colors.ENDC}")
            
            found_panels = find_admin_panel(target_url)
            if found_panels:
                print(f"\n{Colors.GREEN}--- Found Admin Panel Links ---{Colors.ENDC}")
                for panel_url in found_panels:
                    print(f"{Colors.GREEN}+ {panel_url}{Colors.ENDC}")
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}") 
            clear_screen()
            print(f"{Colors.CYAN}======================================={Colors.ENDC}")
            print(f"{Colors.CYAN}          {Colors.YELLOW}Web Reconnaissance Tool{Colors.ENDC}{Colors.CYAN}    {Colors.ENDC}")
            print(f"{Colors.BLUE}Telegram: @silent_mimi{Colors.ENDC}\n")

        elif choice == '3':
            print(f"{Colors.BLUE}Exiting the tool. Goodbye!{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.ENDC}")

if __name__ == "__main__":
    main()

