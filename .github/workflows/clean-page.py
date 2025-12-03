import sys
import time
from playwright.sync_api import sync_playwright, Page
import os
import argparse
from bs4 import BeautifulSoup
from copy import deepcopy

def fetch_with_retry(page: Page, url: str, max_retries=2, retry_delay=1):
    for attempt in range(max_retries + 1):
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            content = page.content()
            return content
        except Exception as e:
            if attempt < max_retries:
                print(f"fetch_with_retry: Attempt {attempt + 1} failed: "
                      f"{str(e)}. "
                      f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"fetch_with_retry: "
                                f"Failed after {max_retries + 1} attempts: "
                                f"{str(e)}")

def clean_html(page: Page, url: str, output_path: str, save_orig: bool):
    try:
        repo = 'bigbrotherju.github.io'
        user_repo = 'BigBrotherJu/' + repo

        start_time = time.monotonic()
        html_content = fetch_with_retry(page, url)
        end_time = time.monotonic()
        print(f"Fetched in {end_time - start_time:.2f} seconds")

        if save_orig:
            base_path = os.path.splitext(output_path)[0]  # 去掉 .html 后缀
            orig_path = f"{base_path}_orig.html"
            with open(orig_path, 'w', encoding="utf-8") as f:
                f.write(html_content)

        soup = BeautifulSoup(html_content, 'html.parser')

        # orig_path = f"{base_path}_souporig.html"
        # with open(orig_path, 'w', encoding="utf-8") as f:
        #     f.write(str(soup))

        # ================== 删除所有 rel="icon" 的链接 ==================
        for link in soup.find_all('link', rel="icon"):
            print(f"正在删除 icon link: {link}\n")
            link.decompose()

        # ================== 处理 title 元素 ==================
        title_element = soup.find('title')
        if title_element:
            print("正在处理 title 元素")
            original_title = title_element.get_text()
            if (user_repo in original_title and '.md' in original_title):
                # 定位 .md 位置
                md_index = original_title.find('.md')

                # 向前查找最近的 /
                slash_index = original_title.rfind('/', 0, md_index)

                if slash_index != -1:
                    new_title = original_title[slash_index+1:md_index]
                else:
                    # 如果没有 / 则取开头到 .md 的部分
                    new_title = original_title[:md_index]

                title_element.string = new_title
                print(f"title 更新: [ {original_title} ] → [ {new_title} ]")
            else:
                print(f"title 中未包含 .md 和 '{user_repo}'，无需修改")
        else:
            print("警告: 未找到 title 元素")

        # ================== 处理 article 元素 ==================
        print()
        article_element = soup.find('article')

        if article_element is not None:
            print("正在处理 article 元素:")
            print(f"    标签类型: {article_element.name}")
            print(f"    ID 属性: {article_element.get('id', '无')}")
            print(f"    class 属性: {article_element.get('class', '无')}")
            print(f"    子元素数量: {len(article_element.find_all())}")
            parent_clone = deepcopy(article_element.parent)

            parent_clone['style'] = 'padding: 32px'

            is_readme = url.lower().endswith('readme.md')
            if is_readme:
                print("正在处理 README 中的链接：")
                md_links = parent_clone.find_all('a',
                    href=lambda x: x and x.endswith('.md'))
                print(f"找到 {len(md_links)} 个 .md 结尾的链接")

                for link in md_links:
                    original_href = link['href']
                    new_href = original_href[:-3] + '.html'  # 替换 .md 为 .html

                    if repo + '/blob/main/' in new_href:
                        prefix = repo + '/blob/main/'
                        start_index = new_href.find(prefix) + len(prefix)
                        new_href = new_href[start_index:]

                    link['href'] = new_href
                    print(f"已修改链接: {original_href} → {new_href}")

            else:
                print("正在处理非 README 页面的链接和图片链接：")

                search_prefix = f"/{user_repo}/raw/main/"

                # 处理所有 <a> 标签
                target_links = parent_clone.find_all('a',
                    href=lambda x: x and x.startswith(search_prefix))
                print(f"找到 {len(target_links)} 个需要处理的链接")
                for link in target_links:
                    original_href = link['href']
                    new_href = original_href[len(search_prefix)-1:] # Keep the /
                    link['href'] = new_href
                    print(f"链接更新: {original_href} → {new_href}")

                # 处理所有 <img> 标签
                target_images = parent_clone.find_all('img',
                    src=lambda x: x and x.startswith(search_prefix))
                print(f"找到 {len(target_images)} 个需要处理的图片")
                for img in target_images:
                    original_src = img['src']
                    new_src = original_src[len(search_prefix)-1:] # Keep the /
                    img['src'] = new_src
                    print(f"图片更新: {original_src} → {new_src}")

            print()

            body = soup.body
            if body:
                body.insert(0, parent_clone)
                print("已插入 article 父元素副本到 body 开头")
            else:
                print("警告: 未找到 body 元素")
        else:
            print("未找到 article 元素")

        # ======== 删除带 data-turbo-body 属性的元素
        print()
        turbo_elements = soup.select('[data-turbo-body]')
        print(f"找到 {len(turbo_elements)} 个带 data-turbo-body 属性的元素")

        for idx, element in enumerate(turbo_elements, 1):
            print(f"正在删除第 {idx} 个 turbo-body 元素:")
            print(f"    标签名: {element.name}")
            print(f"    全部属性: {dict(element.attrs)}")

            # element['hidden'] = None
            # print("已添加 hidden 属性")
            element.decompose()

        # ========== 删除 footer 元素 ==============
        print()
        footer_element = soup.find('footer')

        if footer_element is not None:
            print("正在删除 footer 元素")
            footer_element.decompose()
        else:
            print("未找到 footer 元素，跳过删除")

        # ========== 写入文件 =====================
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    except Exception as e:
        print(f"clean_html: "
              f"Error processing {url}: {str(e)}")
        raise e  # Raise exception to allow retry in main

def main():
    parser = argparse.ArgumentParser(description='Clean HTML pages from GitHub')
    parser.add_argument('url_output_pairs', nargs='+',
                        help='Pairs of GitHub URL and output file path, '
                              'e.g., url1 output1 url2 output2 ...')
    parser.add_argument('--orig', action='store_true',
                        help='Save original HTML file')

    args = parser.parse_args()

    if len(args.url_output_pairs) % 2 != 0:
        print("Error: URLs and output paths must be provided in pairs.")
        sys.exit(1)

    url_outputs = []
    for i in range(0, len(args.url_output_pairs), 2):
        url_outputs.append((args.url_output_pairs[i],
                            args.url_output_pairs[i+1]))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url, output_path in url_outputs:
            print("="*100)
            print(f"Processing {url} -> {output_path}")

            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    clean_html(page, url, output_path, args.orig)
                    break  # Success, move to next URL
                except Exception as e:
                    if attempt < max_retries:
                        print(f"main: Attempt {attempt + 1} failed: {str(e)}. "
                              f"Recreating page and retrying...")
                        try:
                            page.close()
                        except:
                            pass
                        page = browser.new_page()
                    else:
                        print(f"main: Failed to process {url} after "
                              f"{max_retries + 1} attempts: {str(e)}")
                        sys.exit(1)

        browser.close()

if __name__ == "__main__":
    main()
