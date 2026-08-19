import os
import sys
import json
from google import genai
from google.genai import types
from tools import buscar_clima, buscar_atracoes, calcular_orcamento, TOOL_IMPLEMENTATIONS

MAX_ITERACOES = 8  # Guardrail contra loops infinitos de ferramentas

SYSTEM_PROMPT = """Você é um agente de planejamento de viagens.
Use as ferramentas disponíveis para reunir informações reais antes de responder.
Sempre que possível: verifique o clima, sugira atrações e calcule se cabem no orçamento do usuário.
Quando tiver informação suficiente, dê uma resposta final clara e organizada, sem chamar mais ferramentas.
Se o usuário pedir alterações (ex: remover atrações, alterar orçamento), use o histórico da conversa para recalcular e adaptar o plano."""


def executar_ferramenta(nome: str, args: dict) -> dict:
    fn = TOOL_IMPLEMENTATIONS.get(nome)
    if not fn:
        return {"erro": f"Ferramenta desconhecida: {nome}"}
    try:
        return fn(**args)
    except Exception as err:
        return {"erro": f"Falha ao executar {nome}: {str(err)}"}


def processar_turno(
    client: genai.Client,
    model_name: str,
    config: types.GenerateContentConfig,
    historico: list,
    mensagem_usuario: str,
) -> str:
    """Processa um turno de conversa dentro do loop ReAct."""
    historico.append(
        types.Content(role="user", parts=[types.Part.from_text(text=mensagem_usuario)])
    )

    iteracao = 0

    while iteracao < MAX_ITERACOES:
        iteracao += 1
        print(f"\n--- [Agente Pensando - Iteração {iteracao}] ---")

        resultado = client.models.generate_content(
            model=model_name,
            contents=historico,
            config=config,
        )

        candidato = resultado.candidates[0]
        historico.append(candidato.content)

        if resultado.text:
            print(f"[Raciocínio]: {resultado.text}")

        # Se não houver chamadas de ferramenta, o modelo chegou à resposta final
        if not resultado.function_calls:
            return resultado.text or ""

        respostas_funcao = []
        for chamada in resultado.function_calls:
            nome = chamada.name
            args = dict(chamada.args)

            print(f"[Chamando ferramenta]: {nome}({json.dumps(args, ensure_ascii=False)})")
            resultado_ferramenta = executar_ferramenta(nome, args)
            print(
                f"[Resultado de {nome}]:\n"
                f"{json.dumps(resultado_ferramenta, indent=2, ensure_ascii=False)}"
            )

            respostas_funcao.append(
                types.Part.from_function_response(
                    name=nome,
                    response=resultado_ferramenta,
                )
            )

        # Envia o resultado das ferramentas de volta ao modelo
        historico.append(types.Content(role="user", parts=respostas_funcao))

    return "⚠️ Limite de iterações atingido sem uma resposta final. Tente simplificar seu pedido."


def exportar_para_txt(historico: list, nome_arquivo: str = "plano_de_viagem.txt") -> None:
    """Exporta as mensagens e respostas textuais da conversa para um arquivo .txt"""
    conteudo = "===========================================\n"
    conteudo += "       PLANO DE VIAGEM E CONVERSA          \n"
    conteudo += "===========================================\n\n"

    for item in historico:
        role = getattr(item, "role", None)
        parts = getattr(item, "parts", []) or []

        textos = []
        for p in parts:
            text = getattr(p, "text", None)
            if text:
                textos.append(text)

        texto_final = "\n".join(textos).strip()

        if texto_final:
            if role == "user":
                conteudo += f"👤 VOCÊ:\n{texto_final}\n\n"
            elif role == "model":
                conteudo += f"🤖 AGENTE:\n{texto_final}\n\n"
            conteudo += "-------------------------------------------\n"

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"\n💾 Conversa exportada com sucesso para: {nome_arquivo}")


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY antes de rodar.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[buscar_clima, buscar_atracoes, calcular_orcamento],
    )

    historico = []

    print("=== Agente de Planejamento de Viagens (Google Gemini) ===")
    print("Comandos especiais a qualquer momento:")
    print(" - Digite 'exportar' para salvar o plano em .txt e encerrar.")
    print(" - Digite 'sair' para encerrar sem salvar.\n")

    em_execucao = True
    primeira_pergunta = True

    while em_execucao:
        prompt_texto = (
            "O que você precisa planejar? > "
            if primeira_pergunta
            else "\nO que deseja alterar ou perguntar? > "
        )

        try:
            entrada = input(prompt_texto)
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Encerrando o chat. Até logo!")
            break

        comando = entrada.strip().lower()

        if comando == "sair":
            print("👋 Encerrando o chat. Até logo!")
            em_execucao = False
            break

        if comando == "exportar":
            exportar_para_txt(historico)
            print("👋 Encerrando o chat. Até logo!")
            em_execucao = False
            break

        if not entrada.strip():
            continue

        primeira_pergunta = False

        resposta_final = processar_turno(client, model_name, config, historico, entrada)

        print("\n================ RESPOSTA ================")
        print(resposta_final)
        print("==========================================")


if __name__ == "__main__":
    main()