import requests, sys, os
from bs4 import BeautifulSoup
import pandas as pd

def extrair_empenhos(ano, mes):
    sessao = requests.Session()
    url_raiz = "https://pm-braspires.publicacao.siplanweb.com.br/"
    url_base = "https://pm-braspires.publicacao.siplanweb.com.br/empenhos"
    headers_navegador = {"User-Agent": "Mozilla/5.0", "Accept": "application/json, text/javascript, */*; q=0.01"}

    try:
        sessao.get(url_raiz, headers=headers_navegador)
        resposta_site = sessao.get(url_base, headers=headers_navegador)
        soup = BeautifulSoup(resposta_site.text, 'html.parser')
        token_csrf = soup.find('meta', {'name': 'csrf-token'})['content']
        
        url_api = "https://pm-braspires.publicacao.siplanweb.com.br/empenhos/grid-empenhos" 
        headers_api = {"User-Agent": "Mozilla/5.0", "X-CSRF-TOKEN": token_csrf, "X-Requested-With": "XMLHttpRequest", "Referer": url_base, "Accept": "application/json, text/javascript, */*; q=0.01"}

        dados_pedido = {"draw": "1", "start": "0", "length": "5000", "search[value]": "", "search[regex]": "false", "exercicio": ano, "mes_ini": mes, "mes_fim": mes, "unidade": "", "sub_unidade": "", "funcao": "", "sub_funcao": "", "elemento": "", "programa": "", "acao": "", "fonte": "", "fornecedor": "", "conta_despesa": "", "tipo_exibicao_despesa": "7", "order[0][column]": "1", "order[0][dir]": "asc"}
        colunas = ["codi_emp_sequ", "codi_emp", "data_emp", "nom_pes", "val_emp", "val_liqu", "val_pagto", "codi_proces_licit", "codi_proces_licit", "nom_unid", "nom_elem"]
        for i, col in enumerate(colunas):
            dados_pedido[f"columns[{i}][data]"] = col
            dados_pedido[f"columns[{i}][name]"] = ""
            dados_pedido[f"columns[{i}][searchable]"] = "true"
            dados_pedido[f"columns[{i}][orderable]"] = "true" if i > 0 else "false"
            dados_pedido[f"columns[{i}][search][value]"] = ""
            dados_pedido[f"columns[{i}][search][regex]"] = "false"

        resposta_api = sessao.post(url_api, headers=headers_api, data=dados_pedido)
        dados_json = resposta_api.json()
        total_encontrado = dados_json.get('recordsTotal', 0)
        
        if total_encontrado > 0:
            df = pd.DataFrame(dados_json['rows'])
            colunas_finais = [c for c in ['codi_emp', 'data_emp', 'nom_pes', 'nom_unid', 'nom_elem', 'val_emp', 'val_liqu', 'val_pagto', 'num_ano_proc', 'num_ano_contr'] if c in df.columns]
            df_limpo = df[colunas_finais]
            df_limpo.columns = ['Num_Empenho', 'Data', 'Credor_Fornecedor', 'Secretaria', 'Descricao_Despesa', 'Valor_Empenhado', 'Valor_Liquidado', 'Valor_Pago', 'Processo_Licitatorio', 'Contrato']
            df_limpo.to_csv(f"empenhos_reais_braspires_{ano}_{mes}.csv", index=False, encoding='utf-8-sig')
            print(f"OK:{total_encontrado}")
        else:
            print("VAZIO:0")
    except Exception as e:
        print("ERRO:0")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        extrair_empenhos(sys.argv[1], sys.argv[2])
