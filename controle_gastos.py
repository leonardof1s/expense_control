import json
import os
import tkinter as tk
from tkinter import Listbox, messagebox, ttk

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

    def salvar():
        descricao = entrada_descricao.get().strip()
        valor = entrada_valor.get().strip()
        categoria = combo_categoria.get()

        if not descricao:
            messagebox.showerror("Erro", "Descrição nao pode ser vazia!")
            return
        try:
            valor = float(valor)
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
    selecionado = Listbox.curselection
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
        valor = entrada_valor.get().strip()
        categoria = combo_categoria.get()

        if not descricao:
            messagebox.showerror("Erro", "Descricao nao pode ser vazia!")
            return
        try:
            valor = float(valor)
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
    selecionado = Listbox.curselection()
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


def exibir_resumo()