from app.etl.dhl import dhl_entrega
import os


directory_path = os.getcwd()

dhl_entrega('BNU', 'dhl.xlsx', directory_path)
