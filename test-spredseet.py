import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
json_file = '/Users/jun/Downloads/useful-approach-285606-6d6b6033ca4e.json'
sheet_id = '1Estx9Wr_8RX-1wz7rvNO9VHItoevR3Gf6cvgmgFMaAE'
sheet_name = 'シート1'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
gc = gspread.authorize(credentials)
sp = gc.open_by_key(sheet_id)
wks = sp.worksheet(sheet_name)

wks.update_acell('A1', "A1セルに書き込みます。")
print('書き込み完了')
