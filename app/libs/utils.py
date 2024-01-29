import os
import random
import zipfile
import pandas as pd
from unidecode import unidecode


padrao = pd.DataFrame({
    'Nota Fiscal': [],
    'Série NF': [],
    'Chave NF': [],
    'Data Emissão NF': [],
    'Nº Pedido': [],
    'Valor NF': [],
    'Peso': [],
    'Qtd Volumes': [],
    'Metro Cubico': [],
    'Codigo de Volumes': [],
    'CFOP': [],
    'Operação': [],
    'Codigo Tabela Preço': [],
    'Pagador do frete': [],
    'NCM': [],
    'PIN(Suframa)': [],
    'Observações da NF': [],
    'Nome do Emitente': [],
    'CNPJ/CPF Emitente': [],
    'IE Emitente': [],
    'CEP Emitente': [],
    'Rua Emitente': [],
    'Complemento Emitente': [],
    'Numero Emitente': [],
    'Bairro': [],
    'Ciadade(IBGE)': [],
    'Nome do Destinatario': [],
    'CNPJ/CPF do destinatário': [],
    'IE do Destinatario': [],
    'RG Destinatario': [],
    'CEP Destinatario': [],
    'Rua Destinatario': [],
    'Complemento Destinatario': [],
    'Nº Destinatario': [],
    'Bairo Destinatario': [],
    'Cidade (IBGE) Destinatario': [],
    'Nome do Recebedor': [],
    'CNPJ/CPF do Recebedor': [],
    'IE do Recebedor': [],
    'RG Recebedor': [],
    'CEP Recebedor': [],
    'Rua Recebedor': [],
    'Complemento Recebedor': [],
    'Nº Recebedor': [],
    'Bairo Recebedor': [],
    'Cidade (IBGE) Recebedor': []
})

def ibge(directory_path):
    csv = pd.read_csv(f'{directory_path}/app/libs/municipio.csv', delimiter=';', dtype=str, encoding='utf-8')
    return csv

def inscricao(directory_path):
    csv = pd.read_csv(f'{directory_path}/app/libs/ie.csv', delimiter=';', dtype=str, encoding='utf-8')
    return csv

def validacao(relatorio):    
    relatorio = relatorio.applymap(lambda x: x.upper() if isinstance(x, str) else x) # Transforma todo dataframe em maiuscula
    relatorio = relatorio.applymap(lambda texto: unidecode(texto) if isinstance(texto, str) else texto) # Transforma todo datraframe sem acentuacao
    return relatorio

def to_csv(relatorio, name, directory_path):
    name = os.path.splitext(name)[0]

    csv = f'{directory_path}/app/data/download/{name}.csv'
    erro_csv = f'{directory_path}/app/data/download/erro_{name}.csv'
    
    relatorio['Data Emissão NF'] = relatorio['Data Emissão NF'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y'))
    relatorio['Valor NF'] = relatorio['Valor NF'].apply(lambda x: '{:04.2f}'.format(float(x)).replace('.', ','))
    relatorio['Peso'] = relatorio['Peso'].apply(lambda x: '{:04.2f}'.format(float(x)).replace('.', ','))

    com_ibge = relatorio[relatorio['Cidade (IBGE) Destinatario'].notna()]
    sem_ibge = relatorio[relatorio['Cidade (IBGE) Destinatario'].isna()]

    com_ibge.to_csv(csv, index=False, sep=';', encoding='utf-8-sig')
    sem_ibge.to_csv(erro_csv, index=False, sep=';', encoding='utf-8-sig')

    zip(csv, erro_csv, name, directory_path)

def gerar_cpf():
    # Gera os oito primeiros dígitos aleatórios
    oito_digitos = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    # Adiciona o nono dígito como '2'
    nove_digitos = oito_digitos + '2'

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(nove_digitos[i]) * (10 - i)
    
    digito_1 = 11 - (soma % 11)
    digito_1 = digito_1 if digito_1 <= 9 else 0

    # Adiciona o primeiro dígito verificador aos nove dígitos
    dez_digitos = nove_digitos + str(digito_1)

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(dez_digitos[i]) * (11 - i)
    
    digito_2 = 11 - (soma % 11)
    digito_2 = digito_2 if digito_2 <= 9 else 0

    # Gera o CPF completo
    cpf_calculado = f'{nove_digitos}{digito_1}{digito_2}'
    
    return cpf_calculado

def zip(csv, erro_csv, zip, directory_path):
    zip = f'{directory_path}/app/data/download/{zip}.zip'
    try:
        # Criar um arquivo ZIP
        with zipfile.ZipFile(zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Adicionar o primeiro arquivo CSV ao ZIP
            zipf.write(csv, arcname=os.path.basename(csv))

            # Adicionar o segundo arquivo CSV ao ZIP
            zipf.write(erro_csv, arcname=os.path.basename(erro_csv))

        # Excluir os arquivos originais
        os.remove(csv)
        os.remove(erro_csv)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
