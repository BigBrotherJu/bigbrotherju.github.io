import sys
import time
import requests
from bs4 import BeautifulSoup
from copy import deepcopy

def fetch_with_retry(url, max_retries=2, retry_delay=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
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

        # base_path = os.path.splitext(output_path)[0]  # 去掉 .html 后缀
        # orig_path = f"{base_path}_orig.html"
        # with open(orig_path, 'w', encoding="utf-8") as f:
        #     f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # orig_path = f"{base_path}_souporig.html"
        # with open(orig_path, 'w', encoding="utf-8") as f:
        #     f.write(str(soup))

        # =============== 处理 title ================

        title_element = soup.find('title')
        if title_element:
            original_title = title_element.get_text()
            print(f"\n原始标题: {original_title}")

            # 查找 _posts/ 位置
            posts_index = original_title.find('_posts/')
            if posts_index != -1:
                # 计算截取起始位置（跳过 _posts/ 本身）
                start_index = posts_index + len('_posts/')
                remaining_text = original_title[start_index:]

                # 查找空格截止位置
                space_index = remaining_text.find(' ')
                new_title = remaining_text[:space_index] if space_index != -1 else remaining_text

                title_element.string = new_title
                print(f"新标题: {new_title}")
            else:
                print("标题中未包含 _posts/ 路径")
        else:
            print("警告: 未找到 <title> 元素")

        # ================== 处理 article 元素 ==================
        article_element = soup.find('article')

        if article_element is not None:
            print("\n发现 article 元素:")
            print(f"标签类型: {article_element.name}")
            print(f"ID 属性: {article_element.get('id', '无')}")
            print(f"class 属性: {article_element.get('class', '无')}")
            print(f"子元素数量: {len(article_element.find_all())}")
            parent_clone = deepcopy(article_element.parent)

            parent_clone['style'] = 'padding: 32px'

            is_readme = 'readme' in url.lower()
            if is_readme:
                print("正在处理 article 内的链接：")
                md_links = parent_clone.find_all('a', href=lambda x: x and x.endswith('.md'))
                print(f"找到 {len(md_links)} 个 .md 结尾的链接")

                for link in md_links:
                    original_href = link['href']
                    new_href = original_href[:-3] + '.html'  # 替换 .md 为 .html

                    if '_posts/' in new_href:
                        posts_index = new_href.find('/_posts')
                        new_href = new_href[posts_index:]

                    link['href'] = new_href
                    print(f"已修改链接: {original_href} → {new_href}")

            body = soup.body
            if body:
                body.insert(0, parent_clone)
                print("\n已插入 article 父元素副本到 body 开头")
            else:
                print("\n警告: 未找到 body 元素")
        else:
            print("\n未找到 article 元素")

        # ======== 处理带 data-turbo-body 属性的元素
        turbo_elements = soup.select('[data-turbo-body]')
        print(f"找到 {len(turbo_elements)} 个带 data-turbo-body 属性的元素")

        for idx, element in enumerate(turbo_elements, 1):
            print(f"\n正在处理第 {idx} 个 turbo-body 元素:")
            print(f"标签名: {element.name}")
            print(f"全部属性: {dict(element.attrs)}")

            # element['hidden'] = None
            # print("已添加 hidden 属性")
            element.decompose()

        # ========== 处理 footer 元素 ==============
        footer_element = soup.find('footer')

        if footer_element is not None:
            print("\n发现 footer 元素")
            footer_element.decompose()

        # ========== 写入文件 =====================
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        sys.exit(1)  # 非零退出码触发 Actions 重试

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_page.py <github_url> <output_path>")
        sys.exit(1)

    clean_html(sys.argv[1], sys.argv[2])
