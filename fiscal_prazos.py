import requests
import datetime
import sys

def verificar_ultima_atualizacao():
    sessao = requests.Session()
    hoje = datetime.datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    
    print(f"🔍 Iniciando varredura de conformidade...")

    # Tenta verificar os últimos 6 meses para encontrar o último lançamento
    for i in range(6):
        mes_busca = mes_atual - i
        ano_busca = ano_atual
        if mes_busca <= 0:
            mes_busca += 12
            ano_busca -= 1
        
        url_api = "https://pm-braspires.publicacao.siplanweb.com.br/empenhos/grid-empenhos"
        # Payload simplificado só para checar existência
        dados = {
            "draw": "1", "start": "0", "length": "1", "exercicio": str(ano_busca),
            "mes_ini": str(mes_busca), "mes_fim": str(mes_busca), "tipo_exibicao_despesa": "7"
        }
        
        try:
            r = sessao.post(url_api, data=dados, timeout=10)
            total = r.json().get('recordsTotal', 0)
            
            if total > 0:
                print(f"\n✅ ÚLTIMA ATUALIZAÇÃO ENCONTRADA!")
                print(f"📅 Competência: {mes_busca}/{ano_busca}")
                print(f"📊 Volume de Dados: {total} registros lançados.")
                
                # Cálculo de atraso
                meses_atraso = i
                if meses_atraso == 0:
                    print("Status: 🟢 RIGOROSAMENTE EM DIA")
                elif meses_atraso == 1:
                    print("Status: 🟡 ALERTA (30 dias de atraso)")
                else:
                    print(f"Status: 🔴 CRÍTICO ({meses_atraso} meses de atraso)")
                return
        except:
            continue

    print("❌ STATUS: PORTAL ABANDONADO (Nenhum dado nos últimos 6 meses)")

if __name__ == "__main__":
    verificar_ultima_atualizacao()
