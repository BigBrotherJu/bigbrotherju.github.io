import sys
import os
import time
import requests
from bs4 import BeautifulSoup

def fetch_with_retry(url, max_retries=2, retry_delay=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'text/html'
    }

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed after {max_retries + 1} attempts: {str(e)}")

def clean_html(url, output_path):
    try:
        response = fetch_with_retry(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        base_path = os.path.splitext(output_path)[0]  # 去掉 .html 后缀
        orig_path = f"{base_path}_orig.html"

        with open(orig_path, 'w') as f:
            f.write(str(soup))

        elements_to_hide = [
            'header',
            'div#repository-container-header'
            'div#StickyHeader',
            'div.react-code-view-bottom-padding'
            'div.pl-1', # todo
            'div#repos-sticky-header',
            'div#repos-file-tree'
        ]

        for selector in elements_to_hide:
            for element in soup.select(selector):

                print(f"element: [name] {element.name}")
                print(f"         [ID] {element.get('id', 'none')}")
                print(f"         [class] {element.get('class', 'none')}")
                print(f"         [selector] {selector}")
                print("-" * 40)

                element['hidden'] = None

        clean_html = str(soup)

        with open(output_path, 'w') as f:
            f.write(clean_html)

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        sys.exit(1)  # 非零退出码触发 Actions 重试

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_page.py <github_url> <output_path>")
        sys.exit(1)

    clean_html(sys.argv[1], sys.argv[2])
