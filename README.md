# projeto_calconc_2023

Esse repositório contém o sistema produzindo durante a disciplina 'Projeto de Sistemas de Informação', do curso 'Bacharelado em Engenharia de Software', na Universidade Estadual de Ponta Grossa (UEPG).

## Executando o projeto localmente

Esse tópico descreve o passo a passo necessário para executar o projeto localmente.

### Requisitos

- Python 3.9
- pip 20.3

### Instalação de dependências

```
pip install virtualenv
pip install django
```

### Iniciando Virtual Environment

- para Windows:
    ```
    ./calconc/Scripts/activate
    ```

- para Linux:
    ```
    $ source calconc/bin/activate
    ```

Após entrar no venv (virtual environment), deverá aparecer `(calconc)` no início da linha do seu terminal

Todas as ações feitar a partir de agora devem ser feitas dentro do venv


### Instalação de dependências

```
pip install django
pip install -r requirements.txt
```

### Subindo servidor

1. Rodar _migrations_

    ```
    python manage.py migrate
    ```

2. Rodar servidor

    ```
    python manage.py runserver
    ```