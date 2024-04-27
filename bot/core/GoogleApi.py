from typing import Dict, Any, List, Union

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
        self.needs_update_sheets = True
        self.spreadsheet_link = ''

    def __configure(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
        driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
        results = driveService.files().list(q="mimeType='application/vnd.google-apps.spreadsheet'").execute()
        items = results.get('files', [])

        if not items:
            self.configure_if_no_spreadsheet(driveService)
        else:
            self.configure_if_exist_spreadsheet(driveService, items)
        self.spreadsheetId = self.spreadsheet['id']

        access = driveService.permissions().create(
            fileId=self.spreadsheetId,
            body={'type': 'user', 'role': 'writer',
                  'emailAddress': 'nightburgerus@gmail.com'},
            fields='id',
            sendNotificationEmail=False
        ).execute()
        self.spreadsheet_link = 'https://docs.google.com/spreadsheets/d/' + self.spreadsheetId
        print(self.spreadsheet_link)

    def configure_if_exist_spreadsheet(self, driveService, items):
        items_copy = list(filter(lambda x: x['id'] == self.spreadsheetId, items))
        if len(items_copy) == 0:
            self.spreadsheet = items[-1]
        else:
            self.spreadsheet = items_copy[0]

    def configure_if_no_spreadsheet(self, driveService):
        self.spreadsheet = self.service.spreadsheets().create(body={
            'properties': {'title': 'Доски дяди Жени', 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                       'sheetId': 0,
                                       'title': 'Лист номер один',
                                       'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
        }).execute()
        self.spreadsheetId = self.spreadsheet['id']
        access = driveService.permissions().create(
            fileId=self.spreadsheetId,
            body={'type': 'user', 'role': 'writer',
                  'emailAddress': 'nightburgerus@gmail.com'},
            fields='id',
            sendNotificationEmail=False
        ).execute()

        self.add_sheet(sheet_id=0, sheet_name='Мероприятия', header=['ID', 'Название', 'Описание', 'Дата'])
        self.add_sheet(sheet_id=1, sheet_name='Администраторы', header=['ID', 'Никнейм'])

    def getSheets(self):
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        self.sheets = spreadsheet.get('sheets')
        self.needs_update_sheets = False

    def get(self, sheetName='', rows=-1, columns=1, start_row=1, start_column=-1):
        if self.sheets == None:
            self.getSheets()

        sheetId = list(filter(lambda x: x['properties']['title'] == sheetName, self.sheets))
        sheetId = 0 if len(sheetId) == 0 else int(sheetId[0]['properties']['sheetId'])

        s_column = self.__get_column(max(start_column, 1))
        s_row = start_row
        e_column = self.__get_column(max(start_column, 1) + columns)
        e_row = start_row + max(rows, 0)
        sheet_name = f"'{sheetName}'{'!' if len(sheetName) > 0 else ''}"
        range = f"{sheet_name}{s_column}{s_row}:{e_column}{e_row if rows != -1 else ''}"

        res = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheetId,
            range=range,
            majorDimension="ROWS"
        ).execute()
        if 'values' in res:
            return res['values']
        return []

    # При start_row == -1 и start_column == -1, то добавление происходит в конец таблицы
    def post(self, sheetName, data, start_column=-1, start_row=-1):
        self.needs_update_sheets = True
        if start_row == -1 and start_column == -1:
            try:
                res = self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheetId,
                    range=f"{sheetName}!A1:{self.__get_column(len(data[0]))}1",
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
            except:
                return False

        s_column = self.__get_column(start_column)
        s_row = start_row
        e_column = self.__get_column(start_column + len(data[0]))
        e_row = len(data) + start_row

        try:
            res = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheetId,
                body={
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
        except:
            return False

    def clear_cells(self, sheetName, rows: int, columns: int, start_row: int, start_column):
        self.needs_update_sheets = True
        data = []
        for i in range(0, rows):
            data.append(['' for _ in range(0, columns)])

        return self.post(sheetName=sheetName, data=data, start_column=start_column, start_row=start_row)

    def add_sheet(self, sheet_id, sheet_name: str, header: list = []):
        self.needs_update_sheets = True
        body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": f"{sheet_name}",
                            "sheetId": sheet_id
                        }
                    },
                }
            ]
        }

        # Добавление хедера
        if len(header) > 0:
            rows = []
            for r in [header]:
                col = []
                for c in r:
                    col.append(
                        {"userEnteredValue": (
                            {"numberValue": c} if str(c).replace('.', '', 1).isdigit() else {"stringValue": c}),
                        }
                    )
                rows.append({"values": col})

            # Добавить хедер в лист
            update_cells_dict: dict[str, dict[str, Union[dict[str, Union[int, Any]], list[
                dict[str, list[dict[str, dict[str, Any] | dict[str, Any]]]]], str]]] = {
                "updateCells": {
                    "start": {
                        "sheetId": sheet_id,
                        "rowIndex": 0,
                        "columnIndex": 0
                    },
                    "rows": rows,
                    "fields": "userEnteredValue"
                }
            }
            body["requests"].append(update_cells_dict)

            # Сделать ячейки жирными
            bold_cells_dict: dict[str, dict[str, Union[
                dict[str, dict[str, dict[str, bool]]], str, dict[str, Union[int, Any]]]]] = {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold"
                }
            }

            body["requests"].append(bold_cells_dict)
        try:
            self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()
            return True
        except:
            return False


    def delete_sheet(self, sheet: Union[int, str]):
        self.needs_update_sheets = True
        if not str(sheet).isdigit():
            self.getSheets()
            id = 0
            for s in self.sheets:
                if str(s['properties']['title']).lower() == str(sheet).lower():
                    id = int(s['properties']['sheetId'])
        else:
            id = sheet

        body = {
            "requests": [
                {
                    "deleteSheet": {
                        "sheetId": id
                    }
                }
            ]
        }
        try:
            self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()
            return True
        except:
            return False

    def rename_sheet(self, sheet_id, new_title):
        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "title": new_title,
                        },
                        "fields": "title",
                    }
                }
            ]
        }
        try:
            self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()
            return True
        except:
            return False

    def cutPasteRow(self, sheet_id: int, source_row_index: int, destination_row_index: int):
        self.needs_update_sheets = True
        body = {
            "requests": [
                {
                    "cutPaste": {
                        "source": {
                            "sheetId": sheet_id,
                            "startRowIndex": source_row_index,
                            "startColumnIndex": 0
                        },
                        "destination": {
                            "sheetId": sheet_id,
                            "rowIndex": destination_row_index
                        },
                        "pasteType": "PASTE_NORMAL"
                    }
                }
            ]
        }
        try:
            self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()
            return True
        except:
            return False

    def __get_column(self, index: int):
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                   'U', 'V', 'W', 'X', 'Y', 'Z']
        indexes = []
        while index > 0:
            i = index % len(columns) - 1
            indexes.append(columns[i])
            index //= len(columns)
        return ''.join(reversed(indexes))
