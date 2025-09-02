import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

ARQUIVO_DADOS = 'dados_financeiros.json'

entradas = []
gastos = []
categorias_entradas = ["Salario", "Investimentos", "Freelance", "Outros"]
categorias_gastos = ["Alimentcao", "Transporte", "Moradia", "Lazer", "Outros"]


def carregar_dados():
    """Carrega os dados do arquivo JSON, se existir"""
    global entradas, gastos, categorias_entradas, categorias_gastos
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
                entradas = dados.get("entradas", [])
                gastos = dados.get("gastos", [])
                categorias_entradas = dados.get("categorias_entradas", ["Salario", "Investimentos", "Freelance", "Outros"])
                categorias_gastos = dados.get("categorias_gastos", ["Alimentacao", "Transporte", "Moradia" "Lazer", "Outros"])

                for registro in entradas:
                    if "categoria" not in registro:
                        registro["categoria"] = "Outros"
                for registro in gastos:
                    if "categoria" not in registro:
                        registro["categoria"] = "Outros"

                salvar_dados()
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao carregar o arquivo. Inicando com listas vazias")
            entradas = []
            gastos = []
    else:
        entradas = []
        gastos = []


def salvar_dados():
    """
    Salva as listas de entradas e gastos no arquivo JSON.
    """
    dados = {
        "entradas": entradas,
        "gastos": gastos,
        "categorias_entradas": categorias_entradas,
        "categorias_gastos": categorias_gastos
    }
    try:
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar os dados: {e}")


def converter_valor_brasil(valor_str):
    """Converte uma string monetaria (ex: '199,27') para Float (ex : 199.27)"""
    try:
        valor_str = valor_str.replace(',', '.')
        valor = float(valor_str)
        return valor
    except ValueError:
        raise ValueError("Formato de valor inválido. Use numeros com virgula ou ponto(ex.: 199,27 ou 199.27)")


def atualizar_listbox(listbox, tipo):
    """Atualiza a ListBox com entradas ou gastos."""
    listbox.delete(0, tk.END)
    registros = entradas if tipo == "entradas" else gastos
    for i, registro in enumerate(registros, 1):
        listbox.insert(tk.END, f"{i}. {registro['descricao']} ({registro['categoria']}): R${registro['valor']:.2f}")


def calcular_saldo():
    """Calcula o saldo total(entradas - gastos)"""
    total_entradas = sum(entrada["valor"] for entrada in entradas)
    total_gastos = sum(gasto["valor"] for gasto in gastos)
    return total_entradas - total_gastos


def abrir_janela_adicionar(tipo):
    """Abre um janela para adicionar entrada ou gasto"""
    janela = tk.Toplevel()
    janela.title(f"Adicionar {'Entrada' if tipo == 'entradas' else 'Gasto'}")
    janela.geometry("300x250")

    tk.Label(janela, text="Descrição:").pack(pady=5)
    entrada_descricao = tk.Entry(janela)
    entrada_descricao.pack(pady=5)

    tk.Label(janela, text="Valor (R$):").pack(pady=5)
    entrada_valor = tk.Entry(janela)
    entrada_valor.pack(pady=5)

    tk.Label(janela, text="Categoria").pack(pady=5)
    categorias = categorias_entradas if tipo == "entradas" else categorias_gastos
    combo_categoria = ttk.Combobox(janela, values=categorias + ["Nova Categoria ..."])
    combo_categoria.set(categorias[0])
    combo_categoria.pack(pady=5)

    entrada_nova_categoria = tk.Entry(janela)
    entrada_nova_categoria.pack(pady=5)
    entrada_nova_categoria.insert(0, "Digite nova categoria (se selecionada)")
    entrada_nova_categoria.config(state="disabled")

    def on_combobox_select(event):
        """Habilita/Desabilita o campo de nova categoria com base na seleçao."""
        if combo_categoria.get() == "Nova categoria...":
            entrada_nova_categoria.config(state="normal")
            entrada_nova_categoria.delete(0, tk.END)
        else:
            entrada_nova_categoria.config(state="disabled")
            entrada_nova_categoria.delete(0, tk.END)
            entrada_nova_categoria.insert(0, "Digite nova categoria (se selecionada)")

    combo_categoria.bind("<<ComboboxSelected>>", on_combobox_select)

    def salvar():
        descricao = entrada_descricao.get().strip()
        valor_str = entrada_valor.get().strip()
        categoria = combo_categoria.get()

        if not descricao:
            messagebox.showerror("Erro", "Descrição nao pode ser vazia!")
            return
        try:
            valor = converter_valor_brasil(valor_str)
            if valor <= 0:
                messagebox.showerror("Erro", "O valor deve ser positivo!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numerico valido!")
            return

        if categoria == "Nova categoria ...":
            nova_categoria = entrada_descricao.get().strip()   #utiliza campo descricao para nova categoria
            if not nova_categoria:
                messagebox.showerror("Erro", "Nova categoria nao pode ser vazia!")
                return
            if tipo == "entradas":
                categorias_entradas.append(nova_categoria)
                combo_categoria['values'] = categorias_entradas + ["Nova categoria..."]
            else:
                categorias_gastos.append(nova_categoria)
                combo_categoria['values'] = categorias_gastos + ["Nova categoria..."]
            categoria = nova_categoria
        registros = entradas if tipo == "entradas" else gastos
        registros.append({"descricao": descricao, "valor": valor, "categoria": categoria})
        salvar_dados()
        atualizar_listbox(listbox_entradas if tipo == "entradas" else listbox_gastos, tipo)
        messagebox.showinfo("Sucesso", f"{'Entrada' if tipo == 'entradas' else 'Gasto'} adicionado com sucesso!")
        janela.destroy()

    tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)


def abrir_janela_editar(tipo, listbox):
    """Abre uma janela para editar entrada ou gasto."""
    selecionado = listbox.curselection()
    if not selecionado:
        messagebox.showerror("Erro", "Selecione um registro para editar!")
        return

    indice = selecionado[0]
    registros = entradas if tipo == "entradas" else gastos
    if not (0 <= indice < len(registros)):
        messagebox.showerror("Erro", "Indice invalido!")
        return

    registro = registros[indice]
    janela = tk.Toplevel()
    janela.title(f"Editar {'Entrada' if tipo == 'entradas' else 'Gasto'}")
    janela.geometry("300x250")

    tk.Label(janela, text="Descrição:").pack(pady=5)
    entrada_descricao = tk.Entry(janela)
    entrada_descricao.insert(0, registro["descrição"])
    entrada_descricao.pack(pady=5)

    tk.Label(janela, text="Valor (R$):").pack(pady=5)
    entrada_valor = tk.Entry(janela)
    entrada_valor.insert(0, str(registro["valor"]))
    entrada_valor.pack(pady=5)

    tk.Label(janela, text="Categoria").pack(pady=5)
    categorias = categorias_entradas if tipo == "entradas" else categorias_gastos
    combo_categoria = ttk.Combobox(janela, values=categorias + ["Nova categoria..."])
    combo_categoria.set(registro["categoria"])
    combo_categoria.pack(pady=5)

    def salvar():
        descricao = entrada_descricao.get().strip()
        valor_str = entrada_valor.get().strip()
        categoria = combo_categoria.get()

        if not descricao:
            messagebox.showerror("Erro", "Descricao nao pode ser vazia!")
            return
        try:
            valor = converter_valor_brasil(valor_str)
            if valor <= 0:
                messagebox.showerror("Erro", "O valor deve ser positivo!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numerico valido!")
            return
        
        if categoria == "Nova_categoria...":
            nova_categoria = entrada_descricao.get().strip()
            if not nova_categoria:
                messagebox.showerror("Eroo", "Nova categoria nao pode ser vazia!")
                return
            if tipo == "entradas":
                categorias_entradas.append(nova_categoria)
                combo_categoria['Values'] = categorias_gastos + ["Nova categoria..."]
                categoria = nova_categoria

        registros[indice] = {"descricao": descricao, "valor": valor, "categoria": categoria}
        salvar_dados()
        atualizar_listbox()
        messagebox.showinfo("Sucesso", "Registro editado com sucesso!")
        janela.destroy()

    tk.Button(janela, text="Salvar", command=salvar).pack(pady=10)


def excluir_registro(tipo, listbox):
    """Exclui o registro selecionado"""
    selecionado = listbox.curselection()
    if not selecionado:
        messagebox.showerror("Erro", "Selecione um registro para excluir!")
        return

    indice = selecionado[0]
    registros = entradas if tipo == "entradas" else gastos
    if 0 <= indice < len(registros):
        registro = registros.pop(indice)
        salvar_dados()
        atualizar_listbox(listbox, tipo)
        messagebox.showinfo("Sucesso", f"Registro  '{registro['descricao']}' ({registro['categoria']}) excluido!")
    else:
        messagebox.showerror("Erro", "Indice invalido!")


def exibir_resumo():
    """Exibe o resumo financeiro em uma nova janela."""
    janela = tk.Toplevel()
    janela.title("Resumo Financeiro")
    janela.geometry("400x400")

    texto = tk.Text(janela, height=20, width=50)
    texto.pack(pady=10)

    texto.insert(tk.END, "=== Resumo Financeiro ===\n\n")
    texto.insert(tk.END, "Entradas:\n")
    if entradas:
        for entrada in entradas:
            texto.insert(tk.END, f"- {entrada['descricao']} ({entrada['categoria']}): R${entrada['valor']:.2f}\n")
    else:
        texto.insert(tk.END, "Nenhum gasto registrado.\n")

    saldo = calcular_saldo()
    texto.insert(tk.END, f"\nSaldo total: R${saldo:.2f}\n")
    if saldo > 0:
        texto.insert(tk.END, "Voce esta no positivo :)\n")
    elif saldo < 0:
        texto.insert(tk.END, "Voce esta falindo !:(\n)")
    else:
        texto.insert(tk.END, "Voce esta sem saldo, va trabalhar mais.\n")

    texto.config(state="disabled")

# Configuracao da janela principal


janela = tk.Tk()
janela.title("Sistema de Controle de Gastos")
janela.geometry("600x400")

# Carregar dados ao iniciar
carregar_dados()

# Frames para organizar a interface
frame_entradas = tk.Frame(janela)
frame_entradas.pack(pady=10, padx=10, fill="x")
frame_gastos = tk.Frame(janela)
frame_gastos.pack(pady=10, padx=10, fill="x")
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

# Secao de entradas
tk.Label(frame_entradas, text="Entradas", font=("Arial", 12, "bold")).pack()
listbox_entradas = tk.Listbox(frame_entradas, height=5, width=50)
listbox_entradas.pack(pady=5)
tk.Button(
    frame_entradas, text="Adicionar Entrada", command=lambda: abrir_janela_adicionar("entradas")).pack(side="left", padx=5)
tk.Button(frame_entradas, text="Editar Entrada", command=lambda: abrir_janela_editar("entradas", listbox_entradas)).pack(side="left", padx=5)
tk.Button(frame_entradas, text="Excluir Entrada", command=lambda: excluir_registro("entradas", listbox_entradas)).pack(side="left", padx=5)

# Secao de Gastos
tk.Label(frame_gastos, text="Gastos", font=("Arial", 12, "bold")).pack()
listbox_gastos = tk.Listbox(frame_gastos, height=5, width=50)
listbox_gastos.pack(pady=5)
tk.Button(frame_gastos, text="Adicionar Gasto", command=lambda: abrir_janela_adicionar("gastos")).pack(side="left", padx=5)
tk.Button(frame_gastos, text="Editar Gasto", command=lambda: abrir_janela_editar("gastos", listbox_gastos)).pack(side="left",padx=5)
tk.Button(frame_gastos, text="Excluir Gasto", command=lambda: excluir_registro("gastos", listbox_gastos)).pack(side="left", padx=5)

# Botao de Resumo
tk.Button(frame_botoes, text="Exibir Resumo", command=exibir_resumo).pack(pady=10)

# Atualizar listas iniciais
atualizar_listbox(listbox_entradas, "entradas")
atualizar_listbox(listbox_gastos, "gastos")

# Inicia o loop da interface
janela.mainloop()
