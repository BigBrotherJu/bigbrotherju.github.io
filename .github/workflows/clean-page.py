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

        # ================== 处理 title 元素 ==================
        title_element = soup.find('title')
        if title_element:
            print("\n发现 title 元素")
            original_title = title_element.get_text()
            if '.md' in original_title:
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
                print(f"\n标题更新: [ {original_title} ] → [ {new_title} ]")
            else:
                print("\n标题中未包含 .md，无需修改")
        else:
            print("\n警告: 未找到 title 元素")

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
                print("正在处理 README 中的链接：")
                md_links = parent_clone.find_all('a', href=lambda x: x and x.endswith('.md'))
                print(f"找到 {len(md_links)} 个 .md 结尾的链接")

                for link in md_links:
                    original_href = link['href']
                    new_href = original_href[:-3] + '.html'  # 替换 .md 为 .html

                    if 'bigbrotherju.github.io/blob/main/' in new_href:
                        prefix = 'bigbrotherju.github.io/blob/main/'
                        start_index = new_href.find(prefix) + len(prefix)
                        new_href = new_href[start_index:]

                    link['href'] = new_href
                    print(f"已修改链接: {original_href} → {new_href}")

            else:
                print("正在处理非 README 页面的链接和图片：")

                # 处理所有 <a> 标签
                target_links = parent_clone.find_all('a', href=lambda x: x and '/BigBrotherJu/bigbrotherju.github.io' in x)
                print(f"找到 {len(target_links)} 个需要处理的链接")
                for link in target_links:
                    original_href = link['href']
                    new_href = f"https://github.com{original_href}"
                    link['href'] = new_href
                    print(f"链接更新: {original_href} → {new_href}")

                # 处理所有 <img> 标签
                target_images = parent_clone.find_all('img', src=lambda x: x and '/BigBrotherJu/bigbrotherju.github.io' in x)
                print(f"找到 {len(target_images)} 个需要处理的图片")
                for img in target_images:
                    original_src = img['src']
                    new_src = f"https://github.com{original_src}"
                    img['src'] = new_src
                    print(f"图片更新: {original_src} → {new_src}")

            body = soup.body
            if body:
                body.insert(0, parent_clone)
                print("\n已插入 article 父元素副本到 body 开头")
            else:
                print("\n警告: 未找到 body 元素")
        else:
            print("\n未找到 article 元素")

        # ======== 删除带 data-turbo-body 属性的元素
        turbo_elements = soup.select('[data-turbo-body]')
        print(f"找到 {len(turbo_elements)} 个带 data-turbo-body 属性的元素")

        for idx, element in enumerate(turbo_elements, 1):
            print(f"\n正在删除第 {idx} 个 turbo-body 元素:")
            print(f"标签名: {element.name}")
            print(f"全部属性: {dict(element.attrs)}")

            # element['hidden'] = None
            # print("已添加 hidden 属性")
            element.decompose()

        # ========== 删除 footer 元素 ==============
        footer_element = soup.find('footer')

        if footer_element is not None:
            print("\n正在删除 footer 元素")
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
