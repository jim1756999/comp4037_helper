import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_table(url):
    # 发送请求获取网页内容
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 确保请求成功
    
    # 解析 HTML 内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找目标表格
    table = soup.find('table', {'id': 'ctl00_ctl00_PageContent_ctl87'})
    if not table:
        print("未找到表格！")
        return None
    
    # 提取表头
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
    
    # 提取表格数据
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        if tr.find('th'):
            continue  # 跳过分类标题行
        
        cells = []
        for td in tr.find_all('td'):
            link = td.find('a', href=True)
            if link:
                cells.append(link['href'])  # 提取 href 链接
            else:
                cells.append(td.text.strip())
        
        if len(cells) == len(headers):
            rows.append(cells)
    
    # 创建 DataFrame
    df = pd.DataFrame(rows, columns=headers)
    return df

# 示例 URL
url = "https://www.nottingham.ac.uk/computerscience/people/index.aspx"
df = scrape_table(url)

# print(df.head())

name_list = df['Name'].tolist()
# print(name_list)

publications = []



for i in name_list:
    url = "https://www.nottingham.ac.uk/computerscience/people/" + i+ "#lookup-publications"
    print(url)
    # 发送请求获取网页内容
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 确保请求成功

    soup = BeautifulSoup(response.text, 'html.parser')
    for item in soup.find_all('li'):
        citation = item.find('div', class_='conferenceContributionCitation')
        if citation:
            authors = citation.find('span', class_='citationConferenceContributionAuthors')
            year = citation.find('span', class_='citationConferenceYear')
            title = citation.find('span', class_='citationConferenceContributionTitle')
            conference = citation.find('span', class_='citationConferenceTitle')
            pages = citation.find('span', class_='citationConferencePages')
            
            doi_link = citation.find('a')  # 检查是否有 DOI 相关的链接
            doi = doi_link['href'] if doi_link else 'No DOI'
            
            publications.append({
                'authors': authors.get_text(strip=True) if authors else '',
                'year': year.get_text(strip=True) if year else '',
                'title': title.get_text(strip=True) if title else '',
                'conference': conference.get_text(strip=True) if conference else '',
                'pages': pages.get_text(strip=True) if pages else '',
                'doi': doi
            })

#print(publications)

df = pd.DataFrame(publications)

# Saving to an Excel file
file_path = "research_paper.xlsx"
df.to_excel(file_path, index=False)