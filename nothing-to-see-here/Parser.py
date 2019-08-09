import pandas as pd
import requests 
import time
import os

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Parser:
    def __init__(self, path='data/'):
        self.path = path
        self.page_url = "https://minjust.ru/ru/extremist-materials?field_extremist_content_value="
        self.main_url = self.page_url + '&page={}'
        self.total_pages = self.__get_total_pages()
        
        
    def __check_existing(self):
        return os.path.isfile(self.path+'data.csv')
    
    def __get_headers(self):
        return {'User-Agent': UserAgent().chrome}
    
    def __get_total_pages(self):
        """Returns total number of pages on the website"""
        page = requests.get(self.page_url, headers=self.__get_headers())
        soup = BeautifulSoup(page.content,'html.parser')
        total_pages = soup.find("li", attrs={'class': 'b-pager-last last'})
        total_pages = int(total_pages.find('a').get('href').split('page=')[1])
        return total_pages
    
    
    def __download_full_data(self):        
        data = []
        for page_number in range(self.total_pages+1):
            data.append(pd.read_html(self.main_url.format(page_number))[0])
            time.sleep(1)
            
        full_data = pd.DataFrame()
        for dataset in data:
            full_data = full_data.append(dataset, ignore_index=True, sort=False)
            
        return full_data
    
    def __download_update_data(self):
        data = pd.read_html(self.main_url.format(self.total_pages))[0]
        return data
    
    def __process_data(self, data):
        data.set_index("#", inplace=True)
        data.columns = ['material', 'date']
        data.date = pd.to_datetime(data.date)
        return data
    
    def __save_data(self, data):
        print("Saving...")
        data.to_csv(self.path+'data.csv')
    
    def get_data(self, need_update=None):
        if need_update is None:
            need_update = self.__check_existing()
            
        if need_update:
            print("Downloading update dataset...")
            data = self.__download_update_data()
        else:
            print("Downloading full dataset...")
            data = self.__download_full_data()
            
        data = self.__process_data(data)
        
        if need_update:
            print("Updating...")
            full_data = pd.read_csv(self.path+'data.csv')
            full_data.update(data)
            self.__save_data(full_data)
        else:
            self.__save_data(data)
        print("Done.")
        
        
def main():
    dataset = Parser()
    dataset.get_data()
    
    
if __name__ == "__main__":
    main()