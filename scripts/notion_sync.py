from notion_client import Client
import os

NOTION_API_KEY = os.environ["NOTION_API_KEY"]  # 通过 GitHub Secrets 读取 Key
notion = Client(auth=NOTION_API_KEY)


def fetch_all_pages():
    """使用 Notion API 搜索所有页面"""
    results = []
    # 搜索整个工作区
    response = notion.search(page_size=100)
    results.extend(response['results'])
    
    # 如果有更多页面，继续获取
    while response.get('next_cursor'):
        response = notion.search(start_cursor=response['next_cursor'])
        results.extend(response['results'])

    # 返回页面数据列表
    return results


def fetch_page_content(page_id):
    """获取单个页面的内容"""
    children = notion.blocks.children.list(block_id=page_id)
    content = []
    for block in children['results']:
        if block['type'] == 'paragraph':
            content.append(block['paragraph']['text'][0]['text']['content'])
    return "\n".join(content)


def sync_pages():
    """同步所有页面内容到本地"""
    pages = fetch_all_pages()
    print(f"发现 {len(pages)} 个页面，开始同步...")

    for page in pages:
        page_id = page['id']
        title = page['properties']['title']['title'][0]['plain_text']
        print(f"同步页面：{title}")

        # 获取内容并写入本地文件
        content = fetch_page_content(page_id)
        filename = f"notion_pages/{title.replace(' ', '_')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# " + title + "\n\n" + content)


if __name__ == "__main__":
    sync_pages()
