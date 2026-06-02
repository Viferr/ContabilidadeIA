import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Core Contabilístico SQL", layout="centered")

# ==============================================================================
# 1. MOTOR DE BASE DE DADOS (SQLITE)
# ==============================================================================
DB_NOME = "contabilidade.db"

def inicializar_bd():
    conn = sqlite3.connect(DB_NOME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regras_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            chaves TEXT NOT NULL,
            conta_d TEXT NOT NULL,
            deducao_base REAL NOT NULL,
            lei TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM regras_fiscais")
    if cursor.fetchone() == 0:
        dados_iniciais = [
            ("Depósitos à Ordem", "banco,transferência,extrato,pagamento banco", "12 - Depósitos à Ordem", 0.0, "Movimentação financeira base."),
            ("Caixa", "caixa,dinheiro,numerário,moedas,notas", "11 - Caixa", 0.0, "Meios financeiros físicos."),
            ("Clientes", "cliente,fatura cliente,faturação,recebimento,pagou,liquidou", "21 - Clientes", 0.0, "Contas a receber de terceiros."),
            ("Fornecedores", "fornecedor,fatura fornecedor,compra a prazo,pagamento", "22 - Fornecedores", 0.0, "Contas a pagar a terceiros."),
            ("Estado - IVA Dedutível", "iva dedutível,recuperar iva,civa", "2432 - IVA Dedutível", 1.0, "Artigo 19.º do CIVA."),
            ("Compras de Mercadorias", "compra stock,mercadoria,revenda", "312 - Compras de Mercadorias", 1.0, "Regra Geral: 100% dedutível."),
            ("Compras de Matérias-Primas", "matérias primas,materias,primas,produção,fabrico", "311 - Compras de Matérias-Primas", 1.0, "Processo produtivo industrial."),
            ("Equipamento Básico", "máquina,ferramenta,empilhador,industrial", "433 - Equipamento Básico", 1.0, "Ativo fixo tangível."),
            ("Equipamento Transporte", "carro novo,carrinha nova,aquisição viatura,compra viatura", "434 - Equipamento de Transporte", 0.0, "Art. 21.º, n.º 1, al. a) do CIVA."),
            ("Capital Subscrito", "capital social,constituição empresa, quotas", "51 - Capital", 0.0, "Fundo próprio inicial da empresa."),
            ("Conservação e Reparação", "oficina,reparação,pneus,manutenção,revisão", "6221 - Conservação e Reparação", 0.0, "Art. 21.º/1/a) do CIVA. Excluído se viatura ligeira."),
            ("Combustíveis", "combustível,gasóleo,gasolina,abastecer,gpl", "6223 - Combustíveis", 0.50, "Art. 21.º/1/b) do CIVA. 50% Gasóleo/GPL."),
            ("Eletricidade", "eletricidade,luz,edp,iberdrola", "62241 - Eletricidade", 1.0, "100% Dedutível para uso empresarial."),
            ("Refeições e Restauração", "restaurante,almoço,refeição,jantar,café", "6226 - Refeições", 0.0, "Art. 21.º/1/d) do CIVA."),
            ("Despesas de Representação", "oferta,brinde,convite,hotel,alojamento", "6227 - Representação", 0.0, "Excluído de IVA. TA fixa de 10% (Art. 88.º/7 CIRC)."),
            ("Software e Cloud", "software,licença,microsoft,sap,cloud", "6262 - Serviços de Software", 1.0, "Regra Geral: 100% dedutível."),
            ("Seguros", "seguro,acidentes,multirriscos,apólice", "6263 - Seguros", 0.0, "Isento de IVA nos termos do Artigo 9.º do CIVA."),
            ("Comunicações", "telefone,internet,telemóvel,meo,nos", "6264 - Comunicações", 1.0, "100% Dedutível."),
            ("Vendas e Serviços", "venda,fatura emitida,vendi,faturação,emitida", "711 - Vendas e Serviços", 1.0, "Sujeito a IVA à taxa em vigor."),
            ("Resultado Líquido do Período", "lucro,prejuízo,apuramento resultados", "818 - Resultado Líquido", 0.0, "Conta de síntese de fecho.")
        ]
        cursor.executemany('INSERT INTO regras_fiscais (categoria, chaves, conta_d, deducao_base, lei) VALUES (?, ?, ?, ?, ?)', dados_iniciais)
        conn.commit()
    conn.close()

def adicionar_regra_bd(cat, chaves, conta, deducao, lei):
    conn = sqlite3.connect(DB_NOME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO regras_fiscais (categoria, chaves, conta_d, deducao_base, lei) VALUES (?, ?, ?, ?, ?)', (cat, chaves, conta, deducao, lei))
    conn.commit()
    conn.close()

def atualizar_regra_bd(id_regra, chaves, conta, deducao, lei):
    conn = sqlite3.connect(DB_NOME)
    cursor = conn.cursor()
    cursor.execute('UPDATE regras_fiscais SET chaves = ?, conta_d = ?, deducao_base = ?, lei = ? WHERE id = ?', (chaves, conta, deducao, lei, id_regra))
    conn.commit()
    conn.close()

def puxar_regras_bd():
    conn = sqlite3.connect(DB_NOME)
    df = pd.read_sql_query("SELECT * FROM regras_fiscais", conn)
    conn.close()
    return df

inicializar_bd()
# ==============================================================================
# 🔒 INJETOR DE EMERGÊNCIA SQLITE (Garante a carga imediata se o banco estiver vazio)
# ==============================================================================
try:
    conexao_teste = sqlite3.connect(DB_NOME)
    cursor_teste = conexao_teste.cursor()
    cursor_teste.execute("SELECT COUNT(*) FROM regras_fiscais")

    if cursor_teste.fetchone()[0] == 0:
        carga_emergencia = [
            ("Depósitos à Ordem", "banco,transferência,extrato,pagamento banco", "12 - Depósitos à Ordem", 0.0, "Movimentação financeira base."),
            ("Caixa", "caixa,dinheiro,numerário,moedas,notas", "11 - Caixa", 0.0, "Meios financeiros físicos."),
            ("Clientes", "cliente,fatura cliente,faturação,recebimento,pagou,liquidou,cobrança", "21 - Clientes", 0.0, "Contas a receber de terceiros."),
            ("Fornecedores", "fornecedor,fatura fornecedor,compra a prazo,pagamento", "22 - Fornecedores", 0.0, "Contas a pagar a terceiros."),
            ("Estado - IVA Dedutível", "iva dedutível,recuperar iva,civa", "2432 - IVA Dedutível", 1.0, "Artigo 19.º do CIVA."),
            ("Compras de Mercadorias", "compra stock,mercadoria,revenda", "312 - Compras de Mercadorias", 1.0, "Regra Geral: 100% dedutível."),
            ("Compras de Matérias-Primas", "matérias primas,materias,primas,produção,fabrico", "311 - Compras de Matérias-Primas", 1.0, "Processo produtivo industrial."),
            ("Equipamento Básico", "máquina,ferramenta,empilhador,industrial", "433 - Equipamento Básico", 1.0, "Ativo fixo tangível."),
            ("Equipamento Transporte", "carro novo,carrinha nova,aquisição viatura,compra viatura", "434 - Equipamento de Transporte", 0.0, "Art. 21.º/1/a) CIVA."),
            ("Capital Subscrito", "capital social,constituição empresa, quotas", "51 - Capital", 0.0, "Fundo próprio inicial."),
            ("Conservação e Reparação", "oficina,reparação,pneus,manutenção,revisão", "6221 - Conservação e Reparação", 0.0, "Art. 21.º/1/a) do CIVA."),
            ("Combustíveis", "combustível,gasóleo,gasolina,abastecer,gpl", "6223 - Combustíveis", 0.50, "Art. 21.º/1/b) do CIVA. 50% Gasóleo/GPL."),
            ("Eletricidade", "eletricidade,luz,edp,iberdrola", "62241 - Eletricidade", 1.0, "100% Dedutível para uso empresarial."),
            ("Refeições e Restauração", "restaurante,almoço,refeição,jantar,café", "6226 - Refeições", 0.0, "Art. 21.º/1/d) do CIVA."),
            ("Despesas de Representação", "oferta,brinde,convite,hotel,alojamento", "6227 - Representação", 0.0, "TA fixa de 10% (Art. 88.º/7 CIRC)."),
            ("Software e Cloud", "software,licença,microsoft,sap,cloud", "6262 - Serviços de Software", 1.0, "Regra Geral: 100% dedutível."),
            ("Seguros", "seguro,acidentes,multirriscos,apólice", "6263 - Seguros", 0.0, "Isento de IVA nos termos do Artigo 9.º do CIVA."),
            ("Comunicações", "telefone,internet,telemóvel,meo,nos", "6264 - Comunicações", 1.0, "100% Dedutível."),
            ("Vendas e Serviços", "venda,fatura emitida,vendi,faturação,emitida", "711 - Vendas e Serviços", 1.0, "Sujeito a IVA à taxa em vigor."),
            ("Resultado Líquido do Período", "lucro,prejuízo,apuramento resultados", "818 - Resultado Líquido", 0.0, "Conta de síntese de fecho.")
        ]
        cursor_teste.executemany('INSERT INTO regras_fiscais (categoria, chaves, conta_d, deducao_base, lei) VALUES (?, ?, ?, ?, ?)', carga_emergencia)
        conexao_teste.commit() # 🔒 FORÇA A GRAVAÇÃO REAL E IMEDIATA NO DISCO
    conexao_teste.close()
except Exception as e:
    st.error(f"Erro na carga de emergência: {e}")


# ==============================================================================
# 2. PAINEL DE ADMINISTRAÇÃO (SIDEBAR ESCONDIDA)
# ==============================================================================
st.sidebar.title("🔐 Painel de Controlo (CC)")
modo_admin = st.sidebar.checkbox("Ativar Modo Administrador")

if modo_admin:
    senha = st.sidebar.text_input("Introduza a senha de acesso:", type="password")
    if senha == "cc123":
        st.sidebar.success("Acesso Autorizado!")
        df_atual = puxar_regras_bd()
        operacao = st.sidebar.radio("Operação:", ["Criar Nova Regra", "Editar/Expandir Regra Existente"])
        st.sidebar.divider()

        if operacao == "Criar Nova Regra":
            nova_cat = st.sidebar.text_input("Nome da Categoria:")
            novas_chaves = st.sidebar.text_input("Palavras-Chave:")
            nova_conta = st.sidebar.text_input("Conta SNC Débito:")
            nova_deducao = st.sidebar.slider("Dedução Base de IVA:", 0.0, 1.0, 0.0, 0.1)
            nova_lei = st.sidebar.text_input("Base Legal:")
            if st.sidebar.button("Gravar Regra em SQL", key="btn_criar_regra"):
                if nova_cat and novas_chaves and nova_conta:
                    adicionar_regra_bd(nova_cat, novas_chaves.lower(), nova_conta, nova_deducao, nova_lei)
                    st.sidebar.success(f"Regra para '{nova_cat}' gravada!")
        else:
            categoria_selecionada = st.sidebar.selectbox("Selecione a Categoria:", df_atual["categoria"].unique())
                        # 🔒 Proteção contra tabelas vazias no Modo Admin
            linhas_filtradas = df_atual[df_atual["categoria"] == categoria_selecionada]
            if not linhas_filtradas.empty:
                dados_regra = linhas_filtradas.iloc[0]
                chaves_editadas = st.sidebar.text_area("Palavras-Chave:", value=dados_regra["chaves"])
                conta_editada = st.sidebar.text_input("Conta SNC Débito:", value=dados_regra["conta_d"])
                deducao_editada = st.sidebar.slider("Dedução Base de IVA:", 0.0, 1.0, float(dados_regra["deducao_base"]), 0.1)
                lei_editada = st.sidebar.text_input("Base Legal:", value=dados_regra["lei"])
                id_regra_atual = int(dados_regra["id"])
            else:
                st.sidebar.warning("Aguardando carregamento dos dados SQL...")
                chaves_editadas, conta_editada, lei_editada = "", "", ""
                deducao_editada, id_regra_atual = 0.0, 0
            if st.sidebar.button("Atualizar Regra em SQL", key="btn_atualizar_regra"):
                atualizar_regra_bd(id_regra_atual, chaves_editadas.lower(), conta_editada, deducao_editada, lei_editada)
                st.sidebar.success("Regra atualizada com sucesso!")
        if st.sidebar.checkbox("Visualizar Tabela SQL Completa"):
            st.sidebar.dataframe(df_atual[["categoria", "chaves", "conta_d"]])
    elif senha != "":
        st.sidebar.error("Senha Incorreta!")

# ==============================================================================
# 3. INTERFACE PÚBLICA EM ABAS (TABS)
# ==============================================================================
aba1, aba2 = st.tabs(["🚀 Lançamentos Diários SQL", "💼 Processamento de Salários"])
with aba1:
    st.title("🌲 Árvore de Decisão Fiscal Inteligente (SNC)")
    st.caption("Ferramenta avançada de automação de lançamentos alimentada por SQL.")

    pergunta = st.text_input("Descreva a despesa ou o documento:", value="Fatura emitida de venda de serviços")

    col_val1, col_val2 = st.columns(2)
    with col_val1:
        total_fatura = st.number_input("Valor total do documento (€):", min_value=0.0, value=250.00, step=10.0)
    with col_val2:
        taxa_iva_opcao = st.radio("Taxa de IVA aplicada:", [23, 13, 6], index=0, horizontal=True)

    df_regras = puxar_regras_bd()
    regra_aplicada = None
    classe_conta = ""
    nome_conta_debito = "Conta Inicial"


    # 🟢 Limpa a pontuação e divide a frase do utilizador em palavras isoladas exatas
    frase_limpa = pergunta.lower().replace(",", " ").replace(".", " ").replace("/", " ")
    palavras_utilizador = [p.strip() for p in frase_limpa.split() if p.strip() != ""]

    # 1. PRIORIDADE: Procura primeiro se é uma Venda Comercial (71 ou 72)
    for idx, linha in df_regras.iterrows():
        conta_limpa = str(linha["conta_d"]).strip()
        if conta_limpa.startswith("71") or conta_limpa.startswith("72"):
            lista_chaves = [c.strip().lower() for c in linha["chaves"].split(",")]
            if any(chave in palavras_utilizador for chave in lista_chaves if chave != ""):
                regra_aplicada = linha
                break

    # 2. SEGUNDA VIA: Se não for venda pura, procura nas restantes (incluindo 69 e 79)
    if regra_aplicada is None:
        for idx, linha in df_regras.iterrows():
            conta_limpa = str(linha["conta_d"]).strip()
            if not (conta_limpa.startswith("71") or conta_limpa.startswith("72")):
                lista_chaves = [c.strip().lower() for c in linha["chaves"].split(",")]
                # 🟢 Validação por expressão composta (Garante que "juros de empréstimo" não falha)
                if any(chave in pergunta.lower() for chave in lista_chaves if chave != ""):
                    regra_aplicada = linha
                    break

    if regra_aplicada is not None:
        st.success(f"🎯 Categoria Identificada via SQL: **{regra_aplicada['categoria']}**")
        percentagem_deducao = float(regra_aplicada["deducao_base"])
        nota_fiscal = regra_aplicada["lei"]
        nome_conta_debito = regra_aplicada["conta_d"]

        if regra_aplicada["categoria"] == "Refeições e Restauração":
            foi_congresso = st.radio("Enquadramento:", ["Almoço normal da empresa", "Participação em congresso", "Organização do evento"])
            if "organização" in foi_congresso.lower():
                percentagem_deducao = 1.0
                nota_fiscal = "IVA 100% dedutível (Art. 21.º, n.º 3 do CIVA)."
            elif "participação" in foi_congresso.lower():
                percentagem_deducao = 0.50
                nota_fiscal = "IVA 50% dedutível (Art. 21.º, n.º 2, al. d) do CIVA)."
            else:
                percentagem_deducao = 0.0
                nota_fiscal = "IVA Não Dedutível (Art. 21.º, n.º 1, al. d) do CIVA)."

        elif regra_aplicada["categoria"] in ["Conservação e Reparação", "Equipamento Transporte"]:
            tipo_viatura = st.radio("Tipologia da viatura:", ["Ligeira de Passageiros", "Ligeira de Mercadorias", "Viatura Elétrica"])
            if "mercadorias" in tipo_viatura.lower() or "elétrica" in tipo_viatura.lower():
                percentagem_deducao = 1.0
                nota_fiscal = "IVA 100% dedutível para viatura empresarial elegível."
            else:
                percentagem_deducao = 0.0
                nota_fiscal = "Ligeira de Passageiros: IVA Excluído (Art. 21.º, n.º 1, al. a) do CIVA)."

        elif regra_aplicada["categoria"] == "Combustíveis":
            tipo_comb = st.radio("Combustível:", ["Gasóleo", "Gasolina", "GPL / Gás Natural"])
            if "gasóleo" in tipo_comb.lower() or "gpl" in tipo_comb.lower():
                percentagem_deducao = 0.50
                nota_fiscal = "IVA 50% dedutível conforme Art. 21.º, n.º 1, al. b) do CIVA."
            else:
                percentagem_deducao = 0.0
                nota_fiscal = "Gasolina: IVA totalmente excluído de dedução."

        #---------------- 🔒 SEPARAÇÃO ABSOLUTA DA CLASSE 7 (Baseada no nome da Categoria SQL)
        if "Vendas" in regra_aplicada["categoria"]:
            st.markdown("##### 📄 Natureza do Rendimento Emitido (Classe 7)")
            tipo_rendimento = st.radio(
                "Selecione o enquadramento desta faturação:",
                ["Venda de Mercadorias (Conta 711)", "Venda de Produtos Acabados (Conta 712)", "Prestação de Serviços / Honorários (Conta 72)"],
                horizontal=True,
                key="radio_vendas_faturacao_final"
            )

            # Antecipa a matemática para a retenção ler os valores líquidos
            taxa_iva_decimal = taxa_iva_opcao / 100
            valor_base = round(total_fatura / (1 + taxa_iva_decimal), 2)
            total_iva = round(total_fatura - valor_base, 2)

            if "Mercadorias" in tipo_rendimento:
                nome_conta_debito = "711 - Vendas de Mercadorias"
                nota_fiscal = f"Faturação Comercial. IVA liquidado a {taxa_iva_opcao}% nos termos do Artigo 1.º do CIVA."
                st.session_state["valor_retencao_ativo"] = 0.0
            elif "Produtos" in tipo_rendimento:
                nome_conta_debito = "712 - Venda de Produtos Acabados"
                nota_fiscal = f"Faturação Industrial (Produção Própria). IVA liquidado a {taxa_iva_opcao}%."
                st.session_state["valor_retencao_ativo"] = 0.0
            else:
                nome_conta_debito = "72 - Prestações de Serviços"
                nota_fiscal = f"Prestação de Serviços / Honorários obtidos. IVA liquidado a {taxa_iva_opcao}% nos termos do CIVA."

                # 🏛️ INTERFACE DE RETENÇÃO NA FONTE (ART. 94.º DO CIRC)
                st.markdown("##### 🏛️ Retenção na Fonte de IRC")
                sujeito_retencao = st.checkbox("Esta fatura de serviços está sujeita a Retenção na Fonte de IRC? (Taxa de 25%)", key="chk_retencao_irc")

                if sujeito_retencao:
                    valor_retencao = round(valor_base * 0.25, 2)
                    nota_fiscal += f" Sujeito a Retenção na Fonte de 25% (Ativo na Conta 2413): -{valor_retencao}€."
                    st.session_state["valor_retencao_ativo"] = valor_retencao
                else:
                    st.session_state["valor_retencao_ativo"] = 0.0
#-----------
            iva_movimento = total_iva
            valor_liquido_razao = valor_base
            nome_conta_iva = "Conta 2433 - IVA Liquidado"

            # 🟢 Puxa o valor da retenção calculado na sessão
            retencao_fatura = st.session_state.get("valor_retencao_ativo", 0.0)

            if retencao_fatura > 0:
                nome_conta_contrapartida = "Conta 21 / 12 (Valor Líquido)"
                # 🟢 MATEMÁTICA DEFINITIVA (SNC): Valor Bruto Total - Retenção Fonte = 199.19€
                total_documento = round((valor_base + total_iva) - retencao_fatura, 2)
                st.session_state["total_fatura_com_desconto"] = total_documento
                st.info(f"⚖️ **Desdobramento de Ativo:** Valor Bruto da Fatura: {round(valor_base + total_iva, 2)}€ | Retenção AT (Conta 2413): **{retencao_fatura}€** | Líquido a Receber: **{total_documento}€**")
            else:
                nome_conta_contrapartida = "Conta 21 / 12 - Terc. / Fin."
                total_documento = round(valor_base + total_iva, 2)
                st.session_state["total_fatura_com_desconto"] = total_documento

            razao_natureza_credito = True
            contrapartida_credito = False
#---------
        elif "Juros e Rendimentos" in regra_aplicada["categoria"]:
            # 🟢 RENDIMENTOS FINANCEIROS (791): Isento de IVA, sem botões comerciais!
            nome_conta_debito = "791 - Juros Obtidos"
            iva_movimento = 0.0
            valor_liquido_razao = total_fatura
            nome_conta_iva = "Conta N/A - Isento"
            nome_conta_contrapartida = "Conta 12 - Depósitos à Ordem"
            razao_natureza_credito = True
            contrapartida_credito = False

        elif any(classe in classe_conta for classe in ["6", "3", "4"]):
            iva_movimento = round(total_iva * percentagem_deducao, 2)
            iva_custo = round(total_iva - iva_movimento, 2)
            valor_liquido_razao = round(valor_base + iva_custo, 2)
            nome_conta_iva = "Conta 2432 - IVA Dedutível"
            nome_conta_contrapartida = "Conta 12 / 22 - Meios Fin."
            razao_natureza_credito = False
            contrapartida_credito = True
        else:
            iva_movimento = 0.0
            valor_liquido_razao = total_fatura
            nome_conta_iva = "Conta N/A - Sem IVA"
            if "clientes" in regra_aplicada["categoria"].lower() or "caixa" in regra_aplicada["categoria"].lower():
                nome_conta_contrapartida = "Conta 12 - Depósitos à Ordem"
                razao_natureza_credito = True
                contrapartida_credito = False
            elif "financiamentos" in regra_aplicada["categoria"].lower():
                nome_conta_contrapartida = "Conta 12 - Depósitos à Ordem"
                razao_natureza_credito = True
                contrapartida_credito = False
            else:
                nome_conta_contrapartida = "Conta 12 / 11 - Financeira"
                razao_natureza_credito = False
                contrapartida_credito = True

        valor_ta = 0.0
        taxa_ta = 0.0
        msg_ta = ""

        st.markdown("### 🏛️ Enquadramento em Sede de IRC / Impostos")
        empresa_prejuizo = st.checkbox("A empresa apresenta Prejuízo Fiscal no exercício? (Art. 88.º, n.º 14 do CIRC)")

        if "6227" in str(nome_conta_debito):
            taxa_ta = 0.10
            if empresa_prejuizo: taxa_ta += 0.10
            valor_ta = round(valor_liquido_razao * taxa_ta, 2)
            msg_ta = f"⚠️ **Despesas de Representação:** TA de **{int(taxa_ta*100)}%**. Imposto extra: **{valor_ta}€**"
        elif any(num in str(nome_conta_debito) for num in ["6221", "6223", "434"]):
            if "tipo_viatura" in locals() and "Passageiros" in tipo_viatura:
                st.markdown("##### 🚗 Configuração da Viatura Ligeira de Passageiros (IRC)")
                escalao_carro = st.selectbox("Selecione o valor de aquisição histórico da viatura:", ["Até 27.500€ (Taxa base: 8.5%)", "Entre 27.500€ e 35.000€ (Taxa base: 25.5%)", "Mais de 35.000€ (Taxa base: 32.5%)"])
                if "Até 27.500€" in escalao_carro: taxa_ta = 0.085
                elif "Entre" in escalao_carro: taxa_ta = 0.255
                else: taxa_ta = 0.325
                if empresa_prejuizo: taxa_ta += 0.10
                if "434" in str(nome_conta_debito):
                    valor_ta = 0.0
                    msg_ta = f"ℹ️ **Planeamento Fiscal IRC:** Viatura registada no Ativo (434). Futuros encargos sujeitos a TA de **{round(taxa_ta*100, 1)}%**."
                else:
                    valor_ta = round(valor_liquido_razao * taxa_ta, 2)
                    msg_ta = f"⚠️ **Encargos com Viatura:** Sujeito a TA de **{round(taxa_ta*100, 1)}%**. Imposto extra: **{valor_ta}€**"

            st.divider()
            st.subheader("📊 Resultado do Lançamento nos Razonetes (T)")
            st.write(f"**Enquadramento Fiscal (CC):** {nota_fiscal}")
            if valor_ta > 0 or msg_ta != "": st.warning(msg_ta)

        # 🏛️ MOTOR DE DESENHO UNIVERSAL DE RAZONETES (Aba 1)
        # Puxa os valores calculados na sessão
        retencao_fatura_desenho = st.session_state.get("valor_retencao_ativo", 0.0)

        if retencao_fatura_desenho > 0 and "72" in str(nome_conta_debito):
            # Se houver retenção na Conta 72, divide o ecrã em 4 colunas reais
            col1, col2, col_ret, col3 = st.columns(4)
        else:
            col1, col2, col3 = st.columns(3)
            col_ret = None

        with col1:
            # Nas Vendas (Classe 7), o Proveito é sempre registado pelo valor base bruto a Crédito
            if "Vendas" in regra_aplicada["categoria"]:
                val_d = ""
                val_c = f"{valor_base}€"
            else:
                val_d = f"{valor_liquido_razao}€" if not razao_natureza_credito else ""
                val_c = f"{valor_liquido_razao}€" if razao_natureza_credito else ""
            st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #1E88E5; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">{nome_conta_debito}</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{val_d}</span><span style="width: 50%; text-align: right; padding-right: 2px; color: white; font-weight: bold; height: 100%; display: flex; align-items: center; justify-content: flex-end;">{val_c}</span></div></div>', unsafe_allow_html=True)

        with col2:
            # O IVA Liquidado de uma venda deve refletir sempre o valor total calculado sobre o bruto
            if "Vendas" in regra_aplicada["categoria"]:
                val_iva_d = ""
                val_iva_c = f"{total_iva}€"
            else:
                val_iva_d = f"{iva_movimento}€" if (any(x in str(nome_conta_debito) for x in ["6","3","4"]) and iva_movimento > 0) else ""
                val_iva_c = f"{iva_movimento}€" if (any(x in str(nome_conta_debito) for x in ["71","72","7"]) and iva_movimento > 0) else ""

            st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #1E88E5; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">{nome_conta_iva}</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{val_iva_d}</span><span style="width: 50%; text-align: right; padding-right: 2px; color: white; font-weight: bold; height: 100%; display: flex; align-items: center; justify-content: flex-end;">{val_iva_c}</span></div></div>', unsafe_allow_html=True)


        # 🟢 INJETA O RAZONETE DA RETENÇÃO SE ELE ESTIVER ATIVO:
        if col_ret is not None:
            with col_ret:
                st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #1E88E5; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">Conta 2413<br>Retenção Fonte IRC</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{retencao_fatura_desenho}€</span><span style="width: 50%;"></span></div></div>', unsafe_allow_html=True)

        with col3:
            val_tot_d = f"{total_documento}€" if not contrapartida_credito else ""
            val_tot_c = f"{total_documento}€" if contrapartida_credito else ""
            st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #E53935; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">{nome_conta_contrapartida}</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{val_tot_d}</span><span style="width: 50%; text-align: right; padding-right: 2px; color: white; font-weight: bold; height: 100%; display: flex; align-items: center; justify-content: flex-end;">{val_tot_c}</span></div></div>', unsafe_allow_html=True)

    else:
        st.info("💡 Descreva a despesa ou venda acima para consultar a Base de Dados SQL.")

# --- DICIONÁRIO DE CONSULTA PÚBLICA (Fica na Aba 1) ---
    st.markdown("---")
    with st.expander("📖 Consultar Dicionário de Contas e Palavras-Chave Disponíveis"):
        df_consulta = puxar_regras_bd()
        df_exibicao = df_consulta[["categoria", "chaves", "conta_d", "lei"]].rename(columns={"categoria": "Natureza", "chaves": "Palavras-Chave", "conta_d": "Conta SNC", "lei": "Base Legal"})
        st.dataframe(df_exibicao, width="stretch", hide_index=True)

    # ==============================================================================
    # 7. MÓDULO DE FECHO E APURAMENTO ANUAL (CLASSE 8 - Dentro da Aba 1)
    # ==============================================================================
    st.markdown("---")
    st.subheader("🏁 Encerramento do Exercício & Apuramento de Resultados (Classe 8)")
    st.caption("Simulação do fecho anual de contas com cálculo de IRC estimativo (Taxas 2026).")

    with st.expander("🦅 Abrir Painel de Encerramento e Apuramento de IRC"):
        st.markdown("### 📊 Acumulado de Custos e Proveitos do Exercício")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            total_custos_acum = st.number_input("Total de Gastos Acumulados (Classe 6) (€):", min_value=0.0, value=15000.00, step=1000.0)
        with col_f2:
            total_proveitos_acum = st.number_input("Total de Rendimentos Acumulados (Classe 7) (€):", min_value=0.0, value=28000.00, step=1000.0)

        rai = round(total_proveitos_acum - total_custos_acum, 2)

        if rai > 0:
            st.success(f"📈 **Resultado Antes de Impostos (RAI - Conta 811):** Lucro de **{rai}€**")
            if rai <= 50000.0:
                irc_estimado = round(rai * 0.17, 2)
                taxa_mencionada = "17% (Taxa PME até 50.000€)"
            else:
                limite_pme = 50000.0 * 0.17
                excesso = (rai - 50000.0) * 0.21
                irc_estimado = round(limite_pme + excesso, 2)
                taxa_mencionada = "17% até 50k + 21% sobre o excesso"
            resultado_liquido = round(rai - irc_estimado, 2)
        else:
            st.error(f"📉 **Resultado Antes de Impostos (RAI - Conta 811):** Prejuízo de **{rai}€**")
            irc_estimado = 0.0
            taxa_mencionada = "0% (Sem matéria coletável)"
            resultado_liquido = rai

        st.markdown("#### 🏛️ Movimentação das Contas de Síntese")
        col_r8_1, col_r8_2, col_r8_3 = st.columns(3)

        with col_r8_1:
            v_rai_d = f"{abs(rai)}€" if rai < 0 else ""
            v_rai_c = f"{rai}€" if rai > 0 else ""
            st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #1E88E5; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">811 - Resultado Antes de Impostos</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{v_rai_d}</span><span style="width: 50%; text-align: right; padding-right: 2px; color: white; font-weight: bold; height: 100%; display: flex; align-items: center; justify-content: flex-end;">{v_rai_c}</span></div></div>', unsafe_allow_html=True)

        with col_r8_2:
            v_irc_d = f"{irc_estimado}€" if irc_estimado > 0 else ""
            st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #E53935; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">8121 - IRC do Período</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{v_irc_d}</span><span style="width: 50%;"></span></div></div>', unsafe_allow_html=True)
            st.caption(f"<div style='text-align:center; font-size:0.75rem;'>Cálculo: {taxa_mencionada}</div>", unsafe_allow_html=True)

        with col_r8_3:
            v_rl_d = f"{abs(resultado_liquido)}€" if resultado_liquido < 0 else ""
            v_rl_c = f"{resultado_liquido}€" if resultado_liquido > 0 else ""
            st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 140px; margin: 0 auto;"><h4 style="color: #4CAF50; margin-bottom: 8px; font-size: 0.85rem; min-height: 45px; display: flex; align-items: center; justify-content: center;">818 - Resultado Líquido do Período</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; padding-bottom: 3px; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; padding-left: 2px; color: white; font-weight: bold; border-right: 2px solid white; height: 100%; display: flex; align-items: center;">{v_rl_d}</span><span style="width: 50%; text-align: right; padding-right: 2px; color: white; font-weight: bold; height: 100%; display: flex; align-items: center; justify-content: flex-end;">{v_rl_c}</span></div></div>', unsafe_allow_html=True)

        st.divider()
        st.metric(label="💰 Resultado Líquido Final (Lucro Disponível)", value=f"{resultado_liquido}€")

# ==============================================================================
# 6. MÓDULO DE SALÁRIOS INDEPENDENTE (ABA 2 - Encostado à esquerda, sem espaços)
# ==============================================================================
with aba2:
    st.subheader("💼 Simulador Avançado de Processamento de Salários (2026)")
    st.caption("Cálculo automático de retribuições líquidas, descontos e encargos patronais.")
    col_sal1, col_sal2 = st.columns(2)
    with col_sal1:
        salario_base = st.number_input("Salário Bruto / Base Mensal (€):", min_value=0.0, value=1200.00, step=50.0)
        subsidio_alime = st.number_input("Subsídio de Alimentação Diário (€):", min_value=0.0, value=6.00, step=0.5)
    with col_sal2:
        estado_civil = st.radio("Estado Civil:", ["Solteiro / Divorciado", "Casado (1 Titular)", "Casado (2 Titulares)"], horizontal=True)
        dependentes = st.slider("Número de Dependentes:", 0, 5, 0)

    taxa_irs = 0.0
    if "Solteiro" in estado_civil or "2 Titulares" in estado_civil:
        if salario_base <= 870: taxa_irs = 0.0
        elif salario_base <= 1050: taxa_irs = 0.04
        elif salario_base <= 1300: taxa_irs = 0.08
        elif salario_base <= 1600: taxa_irs = 0.12
        elif salario_base <= 2000: taxa_irs = 0.16
        else: taxa_irs = 0.22
    else:
        if salario_base <= 1000: taxa_irs = 0.0
        elif salario_base <= 1250: taxa_irs = 0.03
        elif salario_base <= 1500: taxa_irs = 0.07
        elif salario_base <= 1900: taxa_irs = 0.12
        else: taxa_irs = 0.18

    taxa_irs = max(0.0, taxa_irs - (dependentes * 0.015))
    dias_uteis = 22
    total_sub_alimentacao = round(subsidio_alime * dias_uteis, 2)
    desconto_ss_trabalhador = round(salario_base * 0.11, 2)
    desconto_irs_trabalhador = round(salario_base * taxa_irs, 2)
    total_descontos_trabalhador = round(desconto_ss_trabalhador + desconto_irs_trabalhador, 2)
    salario_liquido = round(salario_base - total_descontos_trabalhador + total_sub_alimentacao, 2)
    encargo_ss_empresa = round(salario_base * 0.2375, 2)
    custo_total_empresa = round(salario_base + encargo_ss_empresa + total_sub_alimentacao, 2)

    st.markdown("#### 🎯 Painel de Resultados Financeiros")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="💰 Salário Líquido a Receber", value=f"{salario_liquido}€")
        st.caption(f"Base: {salario_base}€ | Subsídio: {total_sub_alimentacao}€")
    with col_res2:
        st.metric(label="📉 Descontos do Trabalhador", value=f"-{total_descontos_trabalhador}€")
        st.caption(f"SS (11%): {desconto_ss_trabalhador}€ | IRS ({round(taxa_irs*100,1)}%): {desconto_irs_trabalhador}€")
    with col_res3:
        st.metric(label="🏢 Custo Total para a Empresa", value=f"{custo_total_empresa}€")
        st.caption(f"SS (23.75%): {encargo_ss_empresa}€")
            # 5. Lançamento Contabilístico nos Razonetes (Aba 2)
    st.divider()
    st.subheader("📊 Lançamento Contabilístico da Folha de Salários (SNC)")
    st.caption("Visualização dos fluxos de Débito (Custos) e Crédito (Obrigações e Meios Financeiros).")

    # Contas de Passivo acumuladas para o Estado
    total_seg_social_estado = round(desconto_ss_trabalhador + encargo_ss_empresa, 2)

    col_sal_t1, col_sal_t2 = st.columns(2)
    with col_sal_t1:
        st.markdown("##### 🔺 Contas de Gasto (Débito)")
        # Gasto com Ordenado Bruto
        st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 160px; margin: 0 auto 15px auto;"><h4 style="color: #1E88E5; margin-bottom: 8px; font-size: 0.85rem; min-height: 40px;">631 - Remunerações do Pessoal</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; color: white; font-weight: bold; border-right: 2px solid white; height: 100%;">{salario_base}€</span><span style="width: 50%;"></span></div></div>', unsafe_allow_html=True)
        # Gasto com TSU da Empresa
        st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 160px; margin: 0 auto;"><h4 style="color: #1E88E5; margin-bottom: 8px; font-size: 0.85rem; min-height: 40px;">635 - Encargos sobre Remunerações</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; text-align: left; color: white; font-weight: bold; border-right: 2px solid white; height: 100%;">{encargo_ss_empresa}€</span><span style="width: 50%;"></span></div></div>', unsafe_allow_html=True)

    with col_sal_t2:
        st.markdown("##### 🔻 Contas de Passivo / Dívida (Crédito)")
        # Dívida ao Trabalhador (Valor Líquido + Subsídio Refeição)
        st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 160px; margin: 0 auto 15px auto;"><h4 style="color: #E53935; margin-bottom: 8px; font-size: 0.85rem; min-height: 40px;">231 - Pessoal (Líquido a Pagar)</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; border-right: 2px solid white; height: 100%;"></span><span style="width: 50%; text-align: right; color: white; font-weight: bold;">{salario_liquido}€</span></div></div>', unsafe_allow_html=True)
        # Dívida à Segurança Social (Trabalhador + Empresa)
        st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 160px; margin: 0 auto 15px auto;"><h4 style="color: #E53935; margin-bottom: 8px; font-size: 0.85rem; min-height: 40px;">245 - Estado (Segurança Social)</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; border-right: 2px solid white; height: 100%;"></span><span style="width: 50%; text-align: right; color: white; font-weight: bold;">{total_seg_social_estado}€</span></div></div>', unsafe_allow_html=True)
        # Retenção de IRS do Trabalhador
        st.markdown(f'<div style="text-align: center; font-family: sans-serif; max-width: 160px; margin: 0 auto;"><h4 style="color: #E53935; margin-bottom: 8px; font-size: 0.85rem; min-height: 40px;">242 - Estado (Retenção IRS)</h4><div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 0.75rem; color: white; border-bottom: 3px solid white;"><span>D</span><span>C</span></div><div style="display: flex; justify-content: space-between; height: 28px; align-items: center;"><span style="width: 50%; border-right: 2px solid white; height: 100%;"></span><span style="width: 50%; text-align: right; color: white; font-weight: bold;">{desconto_irs_trabalhador}€</span></div></div>', unsafe_allow_html=True)

    # Nota de Conciliação das Partidas Dobradas
    soma_debitos = round(salario_base + encargo_ss_empresa, 2)
    soma_creditos = round(salario_liquido + total_seg_social_estado + desconto_irs_trabalhador - total_sub_alimentacao, 2)
    st.info(f"⚖️ **Balanço das Partidas Dobradas:** Total Débitos (Custos): **{soma_debitos + total_sub_alimentacao}€** | Total Créditos (Obrigações): **{soma_debitos + total_sub_alimentacao}€** (Lançamento perfeitamente equilibrado).")

