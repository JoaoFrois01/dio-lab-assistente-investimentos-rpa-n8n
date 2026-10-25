import requests
from bs4 import BeautifulSoup
import json

# URL da página pública simulada com os clientes fictícios
URL_PAGINA = "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/"

# URL do Webhook no n8n:
# - Modo Produção (Workflow ativado / Active = ON):
#   http://localhost:5678/webhook/clientes
# - Modo Teste (Clicou em 'Listen for test event' no nó Webhook):
#   http://localhost:5678/webhook-test/clientes
N8N_WEBHOOK = "http://localhost:5678/webhook-test/clientes"


def extrair_clientes():
    """Etapa 1: RPA com Python e BeautifulSoup para coletar dados da tabela HTML"""
    print(f"1) Acessando página de clientes: {URL_PAGINA}")
    response = requests.get(URL_PAGINA)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    linhas = soup.select("#clientes tbody tr")

    clientes = []
    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) >= 4:
            clientes.append({
                "nome": colunas[0].get_text(strip=True),
                "email": colunas[1].get_text(strip=True),
                "saldo": colunas[2].get_text(strip=True),
                "perfil": colunas[3].get_text(strip=True),
            })

    print(f"-> Sucesso: {len(clientes)} clientes extraídos da página.")
    return clientes


def enviar_para_n8n(clientes):
    """Etapa 2: Disparar webhook enviando a lista de clientes para o n8n"""
    print(f"\n2) Enviando clientes para o Webhook do n8n: {N8N_WEBHOOK}")
    payload = {"clientes": clientes}

    try:
        resp = requests.post(N8N_WEBHOOK, json=payload, timeout=10)
        print(f"-> Código de Status HTTP: {resp.status_code}")

        if resp.status_code == 200:
            print("-> Sucesso! O n8n processou os dados e retornou:")
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        else:
            print("-> Resposta do n8n:")
            print(resp.text)
            print("\n[Dica]: Se retornar 404, verifique:")
            print("  a) Se o workflow está ATIVADO (toggle Active ligado no canto superior direito).")
            print("  b) Se estiver testando no editor do n8n, use a URL com '/webhook-test/clientes'.")
    except requests.exceptions.ConnectionError:
        print("\n[Erro de Conexão]: Não foi possível conectar ao n8n em http://localhost:5678.")
        print("Certifique-se de que o container Docker do n8n está rodando.")


if __name__ == "__main__":
    lista_clientes = extrair_clientes()
    enviar_para_n8n(lista_clientes)
