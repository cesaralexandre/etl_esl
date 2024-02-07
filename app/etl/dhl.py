import pandas as pd
from app.libs.utils import validacao, ibge, to_csv, gerar_cpf, definir_caminho, formatar_codigo_postal, padrao


def dhl_entrega(dhl: str, arquivo: str, caminho_diretorio: str) -> None:
    """
    Processa os dados de entrega da DHL e gera um arquivo CSV padronizado.

    Parâmetros:
    - dhl (str): O código de localização da DHL ('POA', 'BNU', 'CWB', etc.).
    - arquivo (str): O nome do arquivo Excel de entrada contendo dados de remessa e peça.
    - caminho_diretorio (str): O caminho do diretório onde os arquivos de entrada e saída estão localizados.

    Retorna:
    None

    A função lê os dados de remessa e peça do arquivo Excel de entrada, realiza validação,
    limpeza e padronização dos dados. Em seguida, gera um arquivo CSV com dados padronizados para uso futuro.

    Observação:
    - A função utiliza funções utilitárias externas do módulo 'app.libs.utils'.
    - O arquivo CSV é salvo no diretório 'app/data/download/'.

    Exemplo:
        dhl_entrega('POA', 'dados_remessa.xlsx', '/caminho/do/diretorio')
    """

    try:
        if dhl=='POA':
            dhl = ['58.890.252/0005-47', '0962474932', '90200290', 'AV DAS INDUSTRIAS', '', '1270', 'ANCHIETA', '4314902']
        elif dhl=='BNU':
            dhl = ['58.890.252/0001-13', '109746831115', '05317020', 'AVENIDA MANUEL BANDEIRA', '', '291', 'VILA LEOPOLDINA', '3550308']
        elif dhl=='CWB':
            dhl = ['58.890.252/0014-38', '9016480778', '80000001', 'RUA DOUTOR REYNALDO MACHADO', '', '1469', 'REBOUCAS', '4106902']
        else:
            print('DHL não encontrada')
            return
        
        #Importando relatorio 455 SSW
        relatorio = validacao(pd.read_excel(definir_caminho(f'{caminho_diretorio}/app/data/upload/{arquivo}'), dtype=str, sheet_name='Shipment'))
        relatorio2 = validacao(pd.read_excel(definir_caminho(f'{caminho_diretorio}/app/data/upload/{arquivo}'), dtype=str, sheet_name='Piece'))

        relatorio = relatorio.drop_duplicates(subset='HWB No')
        relatorio2 = relatorio2.drop_duplicates(subset='HWB No')
        
        relatorio = relatorio.dropna(subset=['Clock Start'])


        #incluindo nro pedido relatorio
        relatorio = relatorio.merge(relatorio2[['HWB No', 'Piece ID']], on='HWB No', how='left')

        #Corrigindo campo Municipio
        relatorio['Rcvr City'] = relatorio['Rcvr State'] + '_' + relatorio['Rcvr City'].str.replace(' ', '_')
        municipio = ibge(definir_caminho(f'{caminho_diretorio}/app/libs/'))
        relatorio = relatorio.merge(municipio[['Municipio', 'ibge']], left_on='Rcvr City', right_on='Municipio', how='left')

        #corrigindo o peso
        relatorio['Weight'] = relatorio['Weight'].apply(lambda x: 1 if float(x) == 0 else float(x))

        #corrigindo o Vlr Mercadoria
        relatorio['Value'] = relatorio['Value'].apply(lambda x: 1 if float(x) == 0 else float(x))
        
        #Dados Mercadoria'
        padrao['Nota Fiscal'] = relatorio['HWB No'].str[-6:]
        padrao['Série NF'] = 1
        padrao['Data Emissão NF'] = relatorio['Clock Start']    
        padrao['Nº Pedido'] = relatorio['HWB No']
        padrao['Valor NF'] = relatorio['Value']
        padrao['Peso'] = relatorio['Weight']
        padrao['Qtd Volumes'] = relatorio['Piece No']
        padrao['CFOP'] = '5353'
        padrao['Operação'] = 'SAIDA'
        padrao['Pagador do frete'] = 'EMITENTE'
        
        #Dados Pagador
        padrao['Nome do Emitente'] = 'DHL EXPRESS (BRAZIL) LTDA'
        padrao['CNPJ/CPF Emitente'] = dhl[0]
        padrao['IE Emitente'] = dhl[1]
        padrao['CEP Emitente'] = dhl[2]
        padrao['Rua Emitente'] = dhl[3]
        padrao['Complemento Emitente'] = dhl[4]
        padrao['Numero Emitente'] = dhl[5]
        padrao['Bairro'] = dhl[6]
        padrao['Ciadade(IBGE)'] = dhl[7]
        
        #Dados Destinatário
        padrao['Nome do Destinatario'] = relatorio['Receiver Name']
        padrao['CNPJ/CPF do destinatário'] = relatorio['Receiver Name'].apply(lambda x: gerar_cpf())
        padrao['CEP Destinatario'] = relatorio['Rcvr Postcode'].apply(lambda x: formatar_codigo_postal(x))
        padrao['Rua Destinatario'] = relatorio['Rcvr Addr 1']
        padrao['Bairo Destinatario'] = ''
        padrao['Cidade (IBGE) Destinatario'] = relatorio['ibge']
        
        #Dados Recebedor
        padrao['Nome do Recebedor'] = padrao['Nome do Destinatario']
        padrao['CNPJ/CPF do Recebedor'] = padrao['CNPJ/CPF do destinatário']
        padrao['CEP Recebedor'] = padrao['CEP Destinatario']
        padrao['Rua Recebedor'] = padrao['Rua Destinatario']
        padrao['Bairo Recebedor'] = padrao['Bairo Destinatario']
        padrao['Cidade (IBGE) Recebedor'] = padrao['Cidade (IBGE) Destinatario']

        to_csv(padrao, arquivo, definir_caminho(f'{caminho_diretorio}/app/data/download/'))

    except Exception as e:
        print(f"Erro durante a execução: {e}")
