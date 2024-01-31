from app.etl.dhl import dhl_entrega
import os


directory_path = os.getcwd()

dhl_entrega('POA', 'dhl.xlsx', directory_path)
