import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def extrair_folha_para_portal(ano, mes):
    print(f"🚀 Iniciando extração via API - Brás Pires ({mes}/{ano})")
    sessao = requests.Session()
    url_base = "https://pm-braspires.publicacao.siplanweb.com.br/pessoal"
    
    headers_navegador = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    try:
        resposta_site = sessao.get(url_base, headers=headers_navegador)
        soup = BeautifulSoup(resposta_site.text, 'html.parser')
        token_csrf = soup.find('meta', {'name': 'csrf-token'})
        
        if not token_csrf:
            sessao.get("https://pm-braspires.publicacao.siplanweb.com.br/?id=1")
            resposta_site = sessao.get(url_base, headers=headers_navegador)
            soup = BeautifulSoup(resposta_site.text, 'html.parser')
            token_csrf = soup.find('meta', {'name': 'csrf-token'})

        if not token_csrf: return print("❌ Erro: Token não encontrado.")

        url_api = "https://pm-braspires.publicacao.siplanweb.com.br/pessoal/grid-pessoal" 
        headers_api = {
            "User-Agent": headers_navegador["User-Agent"],
            "X-CSRF-TOKEN": token_csrf['content'],
            "X-Requested-With": "XMLHttpRequest",
            "Referer": url_base,
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }

        dados_pedido = {
            "draw": "1", "start": "0", "length": "5000",
            "search[value]": "", "search[regex]": "false",
            "exercicio": ano, "mes": mes, "order[0][column]": "3", "order[0][dir]": "asc"
        }

        colunas_exigidas = ["codi_contr_sequ", "codi_contr", "mes", "nom_pes", "mes_extenso", "nom_ccusto", "nom_funcao", "cargo_efetivo_comiss", "desc_local", "tipo_vinculo", "tipo_calc", "val_a_receber"]
        for i, col in enumerate(colunas_exigidas):
            dados_pedido[f"columns[{i}][data]"] = col
            dados_pedido[f"columns[{i}][name]"] = ""
            dados_pedido[f"columns[{i}][searchable]"] = "true"
            dados_pedido[f"columns[{i}][orderable]"] = "true"
            dados_pedido[f"columns[{i}][search][value]"] = ""
            dados_pedido[f"columns[{i}][search][regex]"] = "false"

        resposta_api = sessao.post(url_api, headers=headers_api, data=dados_pedido)
        dados_json = resposta_api.json()
        lista_funcionarios = dados_json.get('data', dados_json.get('rows', []))
        
        if len(lista_funcionarios) > 0:
            df = pd.DataFrame(lista_funcionarios)
            
            # MAPEAMENTO ATUALIZADO (Inclui Matrícula)
            mapa_colunas = {
                'codi_contr': 'Matricula',
                'nom_pes': 'Nome',
                'nom_funcao': 'Cargo',
                'nom_ccusto': 'Secretaria',
                'val_a_receber': 'Liquido',
                'tot_venc': 'Bruto'
            }
            df_renomeado = df.rename(columns=mapa_colunas)
            
            # ADICIONANDO A DATA PADRÃO
            df_renomeado['Data'] = f"{int(mes):02d}/{ano}"
            
            if 'Bruto' not in df_renomeado.columns: df_renomeado['Bruto'] = df_renomeado['Liquido']
            if 'Matricula' not in df_renomeado.columns: df_renomeado['Matricula'] = df_renomeado.index + 1000
                
            colunas_finais = ['Data', 'Matricula', 'Nome', 'Cargo', 'Secretaria', 'Bruto', 'Liquido']
            df_portal = df_renomeado[[c for c in colunas_finais if c in df_renomeado.columns]]
            
            json_portal = df_portal.to_json(orient='records')
            with open('dados_rh.js', 'w', encoding='utf-8') as f:
                f.write(f"const dataSincronizacaoRH = '{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}';\n")
                f.write(f"const dadosRH = {json_portal};")
            
            print(f"✅ SUCESSO! {len(lista_funcionarios)} funcionários salvos para o Portal.")
            
    except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__":
    extrair_folha_para_portal("2026", "1")