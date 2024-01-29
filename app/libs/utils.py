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

def ibge(directory_path: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV contendo dados IBGE.

    Parâmetros:
    - directory_path (str): O caminho do diretório onde o arquivo CSV está localizado.

    Retorna:
    pd.DataFrame: DataFrame contendo dados IBGE.
    """
    csv = pd.read_csv(f'{directory_path}municipio.csv', delimiter=';', dtype=str, encoding='utf-8')
    return csv

def inscricao(directory_path: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV contendo dados de inscrição estadual.

    Parâmetros:
    - directory_path (str): O caminho do diretório onde o arquivo CSV está localizado.

    Retorna:
    pd.DataFrame: DataFrame contendo dados de inscrição estadual.
    """
    csv = pd.read_csv(f'{directory_path}ie.csv', delimiter=';', dtype=str, encoding='utf-8')
    return csv

def validacao(relatorio: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza a validação dos dados no DataFrame.

    Parâmetros:
    - relatorio (pd.DataFrame): DataFrame contendo os dados a serem validados.

    Retorna:
    pd.DataFrame: DataFrame validado.
    """   
    relatorio = relatorio.applymap(lambda x: x.upper() if isinstance(x, str) else x) # Transforma todo dataframe em maiuscula
    relatorio = relatorio.applymap(lambda texto: unidecode(texto) if isinstance(texto, str) else texto) # Transforma todo datraframe sem acentuacao
    return relatorio

def to_csv(relatorio: pd.DataFrame, name: str, directory_path: str) -> None:
    """
    Converte e salva um DataFrame em arquivos CSV.

    Parâmetros:
    - relatorio (pd.DataFrame): DataFrame a ser convertido e salvo.
    - name (str): Nome do arquivo CSV a ser salvo.
    - directory_path (str): O caminho do diretório onde os arquivos CSV serão salvos.

    Retorna:
    None
    """
    name = os.path.splitext(name)[0]

    csv = f'{directory_path}{name}.csv'
    erro_csv = f'{directory_path}erro_{name}.csv'
    
    relatorio['Data Emissão NF'] = relatorio['Data Emissão NF'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y'))
    relatorio['Valor NF'] = relatorio['Valor NF'].apply(lambda x: '{:04.2f}'.format(float(x)).replace('.', ','))
    relatorio['Peso'] = relatorio['Peso'].apply(lambda x: '{:04.2f}'.format(float(x)).replace('.', ','))

    com_ibge = relatorio[relatorio['Cidade (IBGE) Destinatario'].notna()]
    sem_ibge = relatorio[relatorio['Cidade (IBGE) Destinatario'].isna()]

    com_ibge.to_csv(csv, index=False, sep=';', encoding='utf-8-sig')
    sem_ibge.to_csv(erro_csv, index=False, sep=';', encoding='utf-8-sig')

    zip(csv, erro_csv, name, directory_path)

def gerar_cpf() -> str:
    """
    Gera um número de CPF válido aleatoriamente.

    Retorna:
    str: Número de CPF gerado.
    """
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

def zip_arquivos(csv: str, erro_csv: str, nome_zip: str, directory_path: str) -> None:
    """
    Compacta arquivos CSV em um arquivo ZIP.

    Parâmetros:
    - csv (str): Caminho para o primeiro arquivo CSV.
    - erro_csv (str): Caminho para o segundo arquivo CSV.
    - nome_zip (str): Nome do arquivo ZIP a ser criado.
    - directory_path (str): O caminho do diretório onde o arquivo ZIP será salvo.

    Retorna:
    None
    """
    zip = f'{directory_path}{zip}.zip'
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

def definir_caminho(caminho: str) -> str:
    """
    Adapta o caminho do diretório conforme o sistema operacional.

    Parâmetros:
    - caminho (str): Caminho do diretório a ser adaptado.

    Retorna:
    str: Caminho adaptado ao sistema operacional.
    """
    sistema_operacional = os.name  # Obtém o nome do sistema operacional ('posix' para Linux/Unix, 'nt' para Windows)

    if sistema_operacional == 'posix':  # Se for Linux/Unix
        return caminho
    elif sistema_operacional == 'nt':  # Se for Windows
        return caminho.replace('/', '\\\\')
    else:
        raise OSError("Sistema operacional não suportado")
