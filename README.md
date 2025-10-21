#  MechManager — Sistema de Oficina Mecânica

##  Visão Geral
O **MechManager** é um sistema web desenvolvido com **Django 5** para gerenciamento de **oficinas mecânicas**.  
Ele permite cadastrar veículos, mecânicos e serviços, além de criar **ordens de serviço (OS)** detalhadas com cálculo automático do valor total.

Esse projeto foi desenvolvido para a disciplina **Programação Web (GAC116)** da **Universidade Federal de Lavras (UFLA)**, atendendo todos os requisitos de:
- ambiente administrativo com login/senha;  
- ambiente do usuário com login/senha;  
- uso de framework CSS (Bootstrap);  
- banco de dados relacional com tabelas e relacionamentos;  
- versionamento com Git e documentação em Markdown.

---

##  Integrantes do Grupo
| Nome | Matrícula | Função |
|------|------------|--------|
| Gustavo José | 202310431 | Modelagem, backend e documentação |

---

##  Objetivo
Facilitar o gerenciamento de uma oficina mecânica, permitindo o **controle de ordens de serviço**, **cadastro de veículos e mecânicos**, e **consulta de serviços realizados** de forma simples e segura.

---

##  Funcionalidades
- Cadastro de **veículos**, **serviços** e **mecânicos**  
- Criação de **ordens de serviço (OS)** vinculadas a um veículo  
- Cálculo automático do valor total da OS (soma dos itens)  
- Controle de status da OS (*Aberta, Em execução, Concluída, Cancelada*)  
- Área administrativa completa para CRUD  
- Área do usuário autenticado (visualização de veículos e OS)  
- Interface responsiva com **Bootstrap 5**

---

#  Tecnologias Utilizadas

Linguagem: Python 3.12

Framework: Django 5.x

Banco de Dados: SQLite

Frontend: HTML + Bootstrap 5

Versionamento: Git e GitHub

---

#  Como Executar o Projeto

1️. Criar ambiente virtual
   - python -m venv .venv

# Windows
   - .venv\Scripts\activate
# Linux/Mac
   - source .venv/bin/activate


2️. Instalar dependências
   - pip install django==5.*


3️. Migrar o banco de dados
   - python manage.py makemigrations
   - python manage.py migrate


4️. Criar superusuário
   - python manage.py createsuperuser

5️. Executar servidor
   - python manage.py runserver

---

# Acesse:

http://127.0.0.1:8000/admin
 → painel administrativo

http://127.0.0.1:8000/signup
 → cadastro de usuários

http://127.0.0.1:8000/login
 → login

http://127.0.0.1:8000/area
 → área do cliente

---

 #  Exemplo de Fluxo

 - Admin cadastra serviços e mecânicos.

 - Cliente cria conta e registra seu veículo.

 - Admin cria uma OS (WorkOrder) para o veículo, adicionando itens e valores.

 - Sistema calcula o total automaticamente.

 - Cliente logado visualiza suas últimas OS na área do usuário.

---

#  Conclusão

 - O MechManager entrega uma solução completa e funcional para oficinas mecânicas de pequeno e médio porte.
 Cumpre todos os requisitos do trabalho e serve como base sólida para expandir o sistema em futuras etapas.

---

 # Desenvolvido por:
 - Gustavo Jose Rodrigues Pereira — UFLA, 2025/2
 - Projeto acadêmico para a disciplina de Programação Web.