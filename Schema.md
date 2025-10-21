# 🧩 Diagrama do Banco de Dados — MechManager

O **MechManager** utiliza um modelo relacional simples e eficiente, projetado para representar o fluxo de uma oficina mecânica:  
clientes → veículos → ordens de serviço → itens de serviço.

---

## 📘 Estrutura Conceitual

Cada entidade desempenha um papel específico no sistema:

| Entidade | Descrição |
|-----------|------------|
| **User** | Representa o usuário do sistema (cliente ou funcionário). |
| **Mechanic** | Mecânico responsável por executar os serviços da OS. |
| **Vehicle** | Veículo pertencente a um cliente. |
| **Service** | Tipos de serviços oferecidos pela oficina (ex: troca de óleo, alinhamento). |
| **WorkOrder** | Ordem de serviço (OS) que agrupa os serviços prestados a um veículo. |
| **WorkItem** | Item individual dentro de uma OS, relacionando um serviço a quantidade/preço. |

---

## 🧱 Diagrama ER (Mermaid)

```mermaid
erDiagram
    USER ||--o{ VEHICLE : "possui"
    VEHICLE ||--o{ WORKORDER : "gera"
    WORKORDER ||--o{ WORKITEM : "contém"
    SERVICE ||--o{ WORKITEM : "é usado em"
    MECHANIC ||--o{ WORKORDER : "é responsável por"
