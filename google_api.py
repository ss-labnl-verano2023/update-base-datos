from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from api_keys import KEY_FILE, SHEET_ID
from datetime import date, datetime


"""
Aparentemente la API OFICIAL de GOOGLE SHEETS
no permite recuperar los datos filtrando por un ID
Se intento con el método batchGetByDataFilter
pero los filtros están muy limitados

Se puede realizar pero por partes, 
primero buscas IDs luego lo demás
justo lo que se hace en este módulo
"""

try:
    # Cargar Credenciales/Autentificador para API de GOOGLE medinate una SERVICE ACCOUNT
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=['https://www.googleapis.com'
                                                                                          '/auth/spreadsheets'])
    # Crear objeto de interacción con API de GOOGLE SHEETS
    service = build('sheets', 'v4', credentials=credentials)
except (FileNotFoundError, ValueError, HttpError) as error:
    raise Exception(f'Error cargando credenciales o el objeto de interacción con API: {error}')


# Checar optimización usando otros métodos de la API
# Posiblemente requiere reescribir varias funciones
def get_id_index(id_persona):
    try:
        # GET IDs con la API
        request = service.spreadsheets().values().get(spreadsheetId=SHEET_ID,
                                                      range='prueba!A:A',
                                                      valueRenderOption='FORMATTED_VALUE')
        response = request.execute()
    except HttpError:
        print(f'Error en comunicación con la API: {error}')
        response = {}

    # Recuperar solo los valores IDs del JSON
    ids = []
    if len(response) != 0:
        for sublist in response.get('values'):
            if sublist:
                ids.append(sublist[0])
            else:
                ids.append(None)

    # Encontrar el indice en donde esta el ID
    index = -1
    if ids:
        for iteration, each_id in enumerate(reversed(ids)):
            if each_id == str(id_persona):
                index = len(ids) - iteration
                break
    else:
        print('No hay Info')

    return index


# Para mayor generalización del código/ Disminuir el hardcoding de ciertos datos
# TODO: get column name where data is needed
def _get_column_data(header):
    pass


def is_expired(id_index):
    index = id_index

    try:
        # GET EXPIRE DATES con la API
        request = service.spreadsheets().values().get(spreadsheetId=SHEET_ID,
                                                      range=f'prueba!Q{index}',
                                                      )
        response = request.execute()
    except HttpError:
        print(f'Error en comunicación con la API/ID no encontrado: {error}')
        response = {}

    # Recuperar solo FECHA de EXPIRACION del JSON
    expire_date = response.get('values')

    if expire_date:
        # Convertir en formato comparable FECHA de EXPIRACION
        expire_date = datetime.strptime(expire_date[0][0], "%d/%m/%Y")
        expire_date = expire_date.date()

        # FECHA ACTUAL
        today = date.today()

        if expire_date >= today:
            return False
        else:
            return True
    else:
        # El main, quien use el módulo tendra que validar para no detener el programa
        raise Exception('No hay fecha de expiración')


def update_static_data(id_index):
    index = id_index

    # GET static data
    try:
        request = service.spreadsheets().values().get(spreadsheetId=SHEET_ID,
                                                      range=f'prueba!{index}:{index}',)
        response = request.execute()
    except HttpError:
        print(f'Error en comunicación con la API/ID no encontrado: {error}')
        response = {}

    data = response.get('values')

    if data:
        indices = [0, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16]
        static_data = []
        for element in range(len(data[0])):
            if element in indices:
                static_data.append(data[0][element])
            else:
                static_data.append(None)

        # UPDATE static data en el siguiente RENGLÓN LIBRE
        value_range_body = {
            'majorDimension': 'ROWS',
            'values': [static_data]
        }

        try:
            request = service.spreadsheets().values().append(spreadsheetId=SHEET_ID,
                                                             range='prueba!A1',
                                                             valueInputOption='USER_ENTERED',
                                                             insertDataOption='INSERT_ROWS',
                                                             body=value_range_body
                                                             )
            request.execute()
        except HttpError:
            print(f'Error en comunicación con la API. No se pudo realizar la actualización: {error}')
    else:
        raise Exception('No hay informacion para ser copiada')


def update_dynamic_data():
    # GET  CATALOGOS de Información DINAMICA
    try:
        request = service.spreadsheets().values().get(spreadsheetId=SHEET_ID,
                                                      range=f'C_proyectos!A:A', )
        response = request.execute()

        second_request = service.spreadsheets().values().get(spreadsheetId=SHEET_ID,
                                                             range=f'C_actividades!A:A', )
        second_response = second_request.execute()
    except HttpError:
        print(f'Error en comunicación con la API/ID no encontrado: {error}')
        response = {}
        second_response = {}

    project_data = response.get('values')
    activities_data = second_response.get('values')

    if project_data and activities_data:
        # Conocer el INDICE del último renglón
        row_number = service.spreadsheets().values().get(spreadsheetId=SHEET_ID,
                                                         range=f'prueba!A:A')
        row_number = row_number.execute()
        last_row = len(row_number.get('values'))

        project_selection = input('Proyecto: ')
        activity_selection = input('Actividad: ')
        current_date_hour = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # UPDATE DYNAMIC data en el ÚLTIMO RENGLÓN del ID de la persona
        batch_update_values_request_body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [
                {
                    'majorDimension': 'ROWS',
                    'range': f'prueba!K{last_row}',
                    'values': [[project_selection]]
                },
                {
                    'majorDimension': 'ROWS',
                    'range': f'prueba!J{last_row}',
                    'values': [[activity_selection]]
                },
                {
                    'majorDimension': 'ROWS',
                    'range': f'prueba!B{last_row}',
                    'values': [[current_date_hour]]
                }
            ]
        }

        try:
            request = service.spreadsheets().values().batchUpdate(spreadsheetId=SHEET_ID,
                                                                  body=batch_update_values_request_body
                                                                  )
            request.execute()
        except HttpError:
            print(f'Error en comunicación con la API. No se pudo realizar la actualización: {error}')
    else:
        raise Exception('No hay informacion para ser copiada')
