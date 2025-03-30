import requests 
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from typing import List,Dict

non_english_paths = ['/az/', '/bn/', '/de/', '/es/', '/fa/', '/fr/', 
                        '/he/', '/hu/', '/id/', '/it/', '/ja/', '/ko/', 
                        '/nl/', '/pl/', '/pt/', '/ru/', '/tr/', '/uk/', 
                        '/ur/', '/vi/', '/yo/', '/zh/', '/zh-hant/', '/em/']

def save_batch_file (docs:List[Dict],batch_number:int,output_directory:str):

    """
    Save a batch of documents to a file.

    Args:
        docs (List[Dict]): A list of dictionaries, where each dictionary represents a document with 'title' and 'content' keys.
        batch_number (int): The batch number to be included in the filename.
        output_directory (str): The directory where the batch file will be saved.
        """
    filename = os.path.join(output_directory,f'fastapi_docs_batch_{batch_number}.txt')
    with open(filename,'w',encoding='utf-8') as file:
            for doc in docs:
                file.write(f"url: {doc['url']}\n")
                file.write(f"title: {doc['title']}\n")
                file.write(f"content: {doc['content']}\n")
                file.write("---\n")
                file.write("\n\n" + "="*80 + "\n\n")

def extract_content(soup):
    article = soup.find('article')
    if not article:
        return None       
    content = {'text':[],'code_blocks':[]}   
    for element in article.find_all(['p','h1','h2','h3','h4','h5','h6','li']):
        content['text'].append(element.get_text(strip=True))
    for pre in soup.find_all('pre'):
        code = pre.get_text( ) 
        code_element = pre.find('code') 
        language =''  
        if code_element and code_element.has_attr('class'):
            language = code_element['class'][0] 
            if language.startswith('language-'):
                language = language[9:]
        content['code_blocks'].append({'language':language,'code':code})
    return content 

def get_all_pages(base_url:str,output_dir):
    visited = set()
    to_visit = {base_url}
    current_batch = []
    batch_num = 1

    os.makedirs(output_dir,exist_ok=True)
    while to_visit:
        url = to_visit.pop()
        if url in visited or not url.startswith(base_url) or any(path in url for path in non_english_paths)  :
            continue 
        print(f"visiting {url}")
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text,'html.parser')
             
            main_content = extract_content(soup)
            if main_content:
                content = main_content 
                current_batch.append({'url':url,'title':soup.title.string if soup.title else url,'content':content})

            if len(current_batch) >= 10:
                save_batch_file(current_batch,batch_num,output_dir)
                current_batch = []
                batch_num += 1

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url,href)
                    if absolute_url.startswith(base_url) and '#' not in absolute_url:

                        to_visit.add(absolute_url)
            visited.add(url)        
        except Exception as e:
         print(f"error visiting {url}: {e}")
    if current_batch:
        save_batch_file(current_batch,batch_num,output_dir)    

if __name__ == '__main__':
    base_url = "https://fastapi.tiangolo.com"
    output_dir = os.path.join(os.getcwd () ,'docs')
    get_all_pages(base_url,output_dir)
    print("done")
             