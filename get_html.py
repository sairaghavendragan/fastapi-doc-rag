import requests
from bs4 import BeautifulSoup
import os
def save_html (url, output_dir):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    os.makedirs(output_dir, exist_ok=True)
    raw_path = os.path.join(output_dir, 'raw.html')
    with open(raw_path, 'w',encoding='utf-8') as f:
        f.write(response.text)

    clean_path = os.path.join(output_dir, 'clean.html')
    with open(clean_path, 'w',encoding='utf-8') as f:
        f.write(soup.prettify())

if __name__ == '__main__':
    
    url = 'https://fastapi.tiangolo.com/tutorial/query-param-models/'
    output_dir = 'output'
    save_html(url, output_dir)        

    