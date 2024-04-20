import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'bot/core/test-sheets-418005-441dc454af2d.json'

class GoogleSheetsAPI:
    def __init__(self, spreadsheetId: str = ""):
        self.selectedSheet = 0
        self.spreadsheet = None
        self.spreadsheetId = spreadsheetId
        self.service = None
        self.sheets = None
        self.__configure()

    def __configure(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
        driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
        results = driveService.files().list(q="mimeType='application/vnd.google-apps.spreadsheet'").execute()
        items = results.get('files', [])

        if not items:
            self.spreadsheet = self.service.spreadsheets().create(body={
                'properties': {'title': 'Первый тестовый документ', 'locale': 'ru_RU'},
                'sheets': [{'properties': {'sheetType': 'GRID',
                                           'sheetId': 0,
                                           'title': 'Лист номер один',
                                           'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
            }).execute()
        else:
            items_copy = list(filter(lambda x: x['id'] == self.spreadsheetId, items))
            if len(items_copy) == 0:
                self.spreadsheet = items[-1]
            else:
                self.spreadsheet = items_copy[0]
        self.spreadsheetId = self.spreadsheet['id']

        access = driveService.permissions().create(
            fileId = self.spreadsheetId,
            body = {'type': 'user', 'role': 'writer',
                'emailAddress': 'nightburgerus@gmail.com'},
            fields = 'id',
            sendNotificationEmail=False
        ).execute()
        print('https://docs.google.com/spreadsheets/d/' + self.spreadsheetId)

    def getSheets(self):
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        self.sheets = spreadsheet.get('sheets')
        for sheet in self.sheets:
            print(sheet['properties']['sheetId'], sheet['properties']['title'])

    def get(self, sheetName = '', rows = -1, columns = 1, start_row = 1, start_column = -1):
        if self.sheets == None:
            self.getSheets()

        sheetId = list(filter(lambda x: x['properties']['title'] == sheetName, self.sheets))
        sheetId = 0 if len(sheetId) == 0 else int(sheetId[0]['properties']['sheetId'])

        s_column = self.__get_column(start_column)
        s_row = start_row
        e_column = self.__get_column(start_column + columns)
        e_row = start_row + rows
        sheet_name = f"{sheetName}{'!' if len(sheetName) > 0 else ''}"
        range = f"{sheet_name}{s_column}{s_row}:{e_column}{e_row if rows != -1 else ''}"

        res = self.service.spreadsheets().values().get(
            spreadsheetId = self.spreadsheetId,
            range = range,
            majorDimension="ROWS"
        ).execute()
        print(res)
        return res['values']

    # При start_row == -1 и start_column == -1, то добавление происходит в конец таблицы
    def post(self, sheetName, data, start_column = -1, start_row = -1):
        if start_row == -1 and start_column == -1:
            res = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheetId,
                range=f"{sheetName}!{self.__get_column(start_column)}1:{self.__get_column(start_column + len(data[0]))}1",
                valueInputOption="USER_ENTERED",
                body={
                    "values": data
                }
            ).execute()
            updates = res['updates']['updatedCells']
            summ = 0
            for row in data:
                summ += len(row)
            return summ == updates

        s_column = self.__get_column(start_column)
        s_row = start_row
        e_column = self.__get_column(start_column + len(data[0]))
        e_row = len(data) + start_row

        res = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId = self.spreadsheetId,
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": {
                    "range": f"{sheetName}!{s_column}{s_row}:{e_column}{e_row}",
                    "majorDimension": "ROWS",
                    "values": data
                }
            }
        ).execute()
        updates = res['totalUpdatedCells']
        summ = 0
        for row in data:
            summ += len(row)
        return summ == updates

    def clear_cells(self, sheetName, rows: int, columns: int, start_row: int, start_column):
        data = []
        for i in range(0, rows):
            data.append(['' for _ in range(0, columns)])
        return self.post(sheetName=sheetName, data=data, start_column=start_column, start_row=start_row)

    def __get_column(self, index: int):
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        indexes = []
        while index > 0:
            i = index % len(columns) - 1
            indexes.append(columns[i])
            index //= len(columns)
        return ''.join(reversed(indexes))
