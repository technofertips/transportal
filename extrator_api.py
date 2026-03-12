import requests
from bs4 import BeautifulSoup
import pandas as pd

def extrair_folha_real(ano, mes):
    print(f"🚀 Iniciando extração via API - Brás Pires ({mes}/{ano})")
    
    sessao = requests.Session()
    url_base = "https://pm-braspires.publicacao.siplanweb.com.br/pessoal"
    
    headers_navegador = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    try:
        print("🔑 Pegando credenciais de segurança (CSRF e Cookies)...")
        resposta_site = sessao.get(url_base, headers=headers_navegador)
        soup = BeautifulSoup(resposta_site.text, 'html.parser')
        token_csrf = soup.find('meta', {'name': 'csrf-token'})
        
        if not token_csrf:
            print("❌ Erro: Token de segurança não encontrado.")
            return

        csrf_token_real = token_csrf['content']
        url_api = "https://pm-braspires.publicacao.siplanweb.com.br/pessoal/grid-pessoal" 
        
        headers_api = {
            "User-Agent": headers_navegador["User-Agent"],
            "X-CSRF-TOKEN": csrf_token_real,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": url_base,
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }

        # O PACOTE BÁSICO
        dados_pedido = {
            "draw": "1",
            "start": "0",
            "length": "1000",
            "search[value]": "",
            "search[regex]": "false",
            "exercicio": ano,
            "mes": mes,
            "tipoCalc": "",
            "centroCusto": "",
            "funcao": "",
            "tipoContrato": "",
            "remuneracaoInicio": "",
            "remuneracaoFim": "",
            "order[0][column]": "1",
            "order[0][dir]": "asc"
        }

        # --- O SEGREDO ANTI-ERRO 500 ---
        # Recriando as colunas exatas que o banco de dados deles exige para não crashar
        colunas_exigidas = ["", "codi_contr", "mes", "nom_pes", "mes_extenso", "nom_ccusto", "nom_funcao", "cargo_efetivo_comiss", "desc_local", "tipo_vinculo", "tipo_calc", "val_a_receber"]
        
        for i, col in enumerate(colunas_exigidas):
            dados_pedido[f"columns[{i}][data]"] = col
            dados_pedido[f"columns[{i}][name]"] = ""
            dados_pedido[f"columns[{i}][searchable]"] = "true"
            dados_pedido[f"columns[{i}][orderable]"] = "true"
            dados_pedido[f"columns[{i}][search][value]"] = ""
            dados_pedido[f"columns[{i}][search][regex]"] = "false"
        # ---------------------------------

        print(f"📥 Baixando dados direto do Banco de Dados...")
        resposta_api = sessao.post(url_api, headers=headers_api, data=dados_pedido)
        
        if resposta_api.status_code == 500:
            print("❌ Erro 500 persistente: O servidor ainda não gostou do nosso formato.")
            return
            
        dados_json = resposta_api.json()
        
        total_encontrado = dados_json.get('recordsTotal', 0)
        
        if total_encontrado == 0:
            print("⚠️ STATUS: DADOS ZERADOS")
        else:
            print(f"✅ SUCESSO! {total_encontrado} funcionários extraídos.")
            
            lista_funcionarios = dados_json['rows']
            df = pd.DataFrame(lista_funcionarios)
            
            colunas_uteis = ['nom_pes', 'nom_funcao', 'tipo_vinculo', 'tot_venc', 'tot_desc', 'val_a_receber']
            colunas_finais = [c for c in colunas_uteis if c in df.columns]
            
            df_limpo = df[colunas_finais]
            df_limpo.columns = ['Nome', 'Cargo', 'Vínculo', 'Salario_Bruto', 'Descontos', 'Salario_Liquido']
            
            nome_arquivo = f"folha_real_braspires_{ano}_{mes}.csv"
            df_limpo.to_csv(nome_arquivo, index=False, encoding='utf-8-sig') # utf-8-sig para o Excel ler acentos direitinho
            print(f"💾 Arquivo salvo com sucesso: {nome_arquivo}")

    except Exception as e:
        print(f"❌ Erro na extração da API: {e}")

extrair_folha_real("2026", "1")
