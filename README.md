# Sistema de Linhas Aéreas (Flask)

Projeto simples de um sistema de gestão e busca de voos construído com Flask.

## Descrição

Aplicação web para cadastro, busca e compra de passagens aéreas com duas áreas principais: administrador e passageiro. Os dados são armazenados em arquivos JSON na pasta `data/` para manter a simplicidade.

## Recursos

- Área do administrador: login, gerenciar voos e clientes.
- Área do passageiro: registro, login, pesquisa de voos, compra de passagem.
- Templates Jinja2 em `app/templates/` e páginas estáticas em `app/static/`.
- Dados de exemplo em JSON dentro da pasta `data/`.

## Estrutura do projeto (resumo)

- `app/` - código da aplicação Flask
  - `routes/` - rotas para admin e passenger
  - `templates/` - templates HTML (admin, passenger, voos)
  - `static/` - CSS, imagens
  - `structures.py` - modelos/estruturas do projeto
- `data/` - arquivos JSON com dados (voos, clientes, compras etc.)
- `app.py` - ponto de entrada da aplicação
- `requirements.txt` - dependências Python

## Requisitos

- Python 3.10+
- Virtualenv (recomendado)

## Instalação e execução (desenvolvimento)

1. Crie e ative um ambiente virtual (Linux/macOS):

```bash
python3 -m venv venv-airline-system
source venv-airline-system/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute a aplicação:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Acesse `http://127.0.0.1:5000` no navegador.

Observação: se preferir, existe uma venv no repositório chamada `venv-airline-system/` com dependências já instaladas — ative-a com `source venv-airline-system/bin/activate`.

## Configuração

- A aplicação usa arquivos JSON em `data/`. Faça backup antes de alterar dados reais.
- Para produção, substitua o armazenamento por um banco de dados e configure variáveis de ambiente apropriadas.

## Teste rápido

- Verifique as rotas em `app/routes/` para ver endpoints existentes (`admin_routes.py`, `passenger_routes.py`).
- Abra as páginas de exemplo em `app/templates/` para validar o layout.

## Contribuição

- Faça um fork do repositório.
- Crie uma branch com sua feature: `git checkout -b feature/nome`.
- Abra um pull request descrevendo as mudanças.

## Licença

Este projeto inclui um arquivo `LICENSE` na raiz — verifique-o para detalhes da licença.

