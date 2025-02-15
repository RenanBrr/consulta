# Sistema de Consulta de Viabilidade

Sistema web para consulta de viabilidade de endereços por CEP e número para os estados do Paraná, Rio Grande do Sul e Santa Catarina.

## Funcionalidades

- Consulta de viabilidade por CEP e número
- Suporte para múltiplos estados (PR, RS, SC)
- Interface web responsiva e amigável
- Carregamento dinâmico de dados por estado

## Tecnologias Utilizadas

- Python 3.x
- Flask (Backend)
- Pandas (Processamento de dados)
- HTML5/CSS3
- TailwindCSS
- JavaScript

## Requisitos

- Python 3.x
- Pip (Gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/RenanBrr/consulta.git
cd consulta
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Estrutura de pastas para os dados:
```
SUPER LISTA/
├── PR/
│   ├── PR.csv
│   └── PR-2.csv
├── SC/
│   └── SC.csv
└── RS/
    └── RS.csv
```

5. Execute o servidor:
```bash
python app.py
```

O sistema estará disponível em `http://127.0.0.1:5000`

## Estrutura dos Arquivos CSV

Para adicionar novos arquivos CSV ao sistema, consulte o arquivo `regras_csv.txt` que contém todas as regras e padrões necessários.

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 