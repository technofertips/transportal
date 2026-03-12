#!/bin/bash

# Configuração de Cores
VERDE='\033[1;32m'
VERMELHO='\033[1;31m'
AZUL='\033[1;34m'
AMARELO='\033[1;33m'
BRANCO='\033[1;37m'
NC='\033[0m'

ANO=$1
MES=$2

if [ -z "$ANO" ] || [ -z "$MES" ]; then
    echo -e "${VERMELHO}⚠️ ERRO: Faltam parâmetros.${NC}"
    echo -e "Como usar: ${BRANCO}./auditoria_braspires.sh <ANO> <MES>${NC}"
    echo -e "Exemplo:   ${BRANCO}./auditoria_braspires.sh 2026 1${NC}"
    exit 1
fi

clear
echo -e "${AZUL}==================================================${NC}"
echo -e "${BRANCO}    🚀 PAINEL DE AUDITORIA DE TRANSPARÊNCIA${NC}"
echo -e "${BRANCO}             SISTEMA: TECHNOFER${NC}"
echo -e "${AZUL}==================================================${NC}"
echo -e "📍 Município: ${BRANCO}Brás Pires - MG${NC}"
echo -e "📅 Período Analisado: ${BRANCO}${MES}/${ANO}${NC}"
echo -e "🕒 Data da Varredura: ${BRANCO}$(date '+%d/%m/%Y %H:%M:%S')${NC}"
echo -e "${AZUL}--------------------------------------------------${NC}"

# --- MÓDULO 1: RECURSOS HUMANOS ---
echo -e -n "👨‍💼 [1] Verificando Folha de Pagamento (RH)... "
RESPOSTA_RH=$(python3 extrator_api.py $ANO $MES)

if [[ "$RESPOSTA_RH" == OK* ]]; then
    TOTAL=$(echo $RESPOSTA_RH | cut -d':' -f2)
    echo -e "${VERDE}[STATUS VERDE]${NC}"
    echo -e "    ↳ ✅ Dados transparentes e atualizados!"
    echo -e "    ↳ 📄 Registros extraídos: ${BRANCO}$TOTAL funcionários${NC}"
    echo -e "    ↳ 💾 Salvo em: ${BRANCO}folha_real_braspires_${ANO}_${MES}.csv${NC}"
else
    echo -e "${VERMELHO}[ALERTA VERMELHO]${NC}"
    echo -e "    ↳ ⚠️ Nenhum dado encontrado no banco de dados!"
    echo -e "    ↳ 🛑 Possível omissão ou atraso no envio de informações."
fi

echo -e "${AZUL}--------------------------------------------------${NC}"

# --- MÓDULO 2: DESPESAS E EMPENHOS ---
echo -e -n "💰 [2] Verificando Gastos e Empenhos... "
RESPOSTA_EMP=$(python3 extrator_empenhos.py $ANO $MES)

if [[ "$RESPOSTA_EMP" == OK* ]]; then
    TOTAL_EMP=$(echo $RESPOSTA_EMP | cut -d':' -f2)
    echo -e "${VERDE}[STATUS VERDE]${NC}"
    echo -e "    ↳ ✅ Dados financeiros atualizados e transparentes!"
    echo -e "    ↳ 📄 Notas e empenhos extraídos: ${BRANCO}$TOTAL_EMP registros${NC}"
    echo -e "    ↳ 💾 Salvo em: ${BRANCO}empenhos_reais_braspires_${ANO}_${MES}.csv${NC}"
else
    echo -e "${VERMELHO}[ALERTA VERMELHO]${NC}"
    echo -e "    ↳ ⚠️ Nenhum empenho encontrado no portal."
    echo -e "    ↳ 🛑 Cuidado: Caixa preta identificada neste mês."
fi

echo -e "${AZUL}==================================================${NC}"
echo -e "${BRANCO}🏁 Auditoria finalizada. Arquivos CSV prontos para análise.${NC}"
echo -e "${AZUL}==================================================${NC}"
