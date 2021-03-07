import pandas as pd
import numpy as np
import json
import requests
from pandas.io.json import json_normalize
from tqdm import tqdm_notebook


class TranscriptsLoader:
    def __init__(self, deputy_id:int, date_from:str, date_to:str, api_token:str):
        self.deputy_id = deputy_id
        self.date_from = date_from
        self.date_to = date_to
        self.api_token = api_token
        
    def _load_transcripts_data(self, page:int):
        transcripts_url = "http://api.duma.gov.ru/api/{api_token}/"
        transcripts_url += "transcriptDeputy/{deputy_id}.json?page={page}"
        transcripts_url += "&limit=20&dateFrom={date_from}&dateTo={date_to}"

        transcripts_response = requests.get(
            transcripts_url.format(
                api_token=self.api_token,
                deputy_id=self.deputy_id,
                page=page,
                date_from=self.date_from,
                date_to=self.date_to
                ),
            headers={'REFERER':"https://github.com/DmitrySerg"})
        if transcripts_response.ok:
            transcripts_response = json.loads(transcripts_response.content)
            transcripts_response['deputy_id'] = self.deputy_id
            self.pages = self._get_pages(transcripts_response)
        else:
            transcripts_response = []
        return transcripts_response
    
    @staticmethod
    def _get_pages(transcripts_response:json):
        pages = transcripts_response.get('totalCount', 20)
        pages = int(pages) if pages is not None else 20  
        pages = int(np.ceil(pages/20))
        return pages
    
    @staticmethod
    def _process_transcripts_data(transcripts_response):
        """"""

        transcripts_columns = [
            'start_line', 'end_line', 'type', 'lines', 
            'votes', 'deputy_name', 'meeting_date', 'deputy_id'
        ]

        transcripts_data = json_normalize(
            transcripts_response,
            ['meetings', 'questions', 'parts' ],  
            ['name', ['meetings','date'], 'deputy_id'], 
            record_prefix='_'
        )
        
        if not transcripts_data.empty:
            transcripts_data.columns = transcripts_columns
        return transcripts_data
    
    def _get_single_page_data(self, page=1):
        transcripts_response = self._load_transcripts_data(page)
        transcripts_data = self._process_transcripts_data(transcripts_response)
        return transcripts_data
    
    def get_transcripts_data(self):
        transcripts_data = [self._get_single_page_data()]
        if self.pages > 1:
            for page in tqdm_notebook(range(2, self.pages+1), desc='page', leave=False):        
                transcripts_data.append(self._get_single_page_data(page))
        transcripts_data = pd.concat(transcripts_data, ignore_index=True)
        return transcripts_data