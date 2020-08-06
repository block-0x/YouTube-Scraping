#!/usr/bin/env python
# coding:utf-8

from apiclient import discovery
import oauth2client
import httplib2
import argparse

SPREADSHEET_ID = '1Estx9Wr_8RX-1wz7rvNO9VHItoevR3Gf6cvgmgFMaAE'
SHEET_ID = 'シート1'
CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIAL_FILE = '/Users/jun/Downloads/useful-approach-285606-6d6b6033ca4e.json'
APPLICATION_NAME = 'YouTube-Scraping'

store = oauth2client.file.Storage(CREDENTIAL_FILE)
credentials = store.get()
if not credentials or credentials.invalid:
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    credentials = oauth2client.tools.run_flow(flow, store)

http = credentials.authorize(httplib2.Http())
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')
service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

requests = {
    'pasteData': {
        # coordinate https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#GridCoordinate
        'coordinate':{
          'sheetId': SHEET_ID,
          'rowIndex': 0,
          'columnIndex': 0
        },
        'data':'1,2,3\n"a,b",c,d\n',
        # PasteType https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#PasteType
        'type':'PASTE_VALUES',
        'delimiter': ',',
    }
}

body = {
    'requests': requests
}

response = service.spreadsheets().batchUpdate(
  spreadsheetId=SPREADSHEET_ID,
  body=body).execute()