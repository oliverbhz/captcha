# Automação de Login COD

Este projeto implementa uma automação de login para o sistema COD usando Python, Selenium e Google Vision API para resolução de CAPTCHA.

## Requisitos

- Python 3.7+
- Google Chrome instalado
- Arquivo de credenciais do Google Vision API
- Pacotes Python listados em `requirements.txt`

## Configuração

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Configure o arquivo de credenciais do Google Vision API em `key/quebra-captcha-b2266280152a.json`
4. Certifique-se que o Chrome está instalado em `C:\Program Files\Google\Chrome\Application\chrome.exe`

## Uso

Execute o script com os seguintes parâmetros:

```bash
python main.py <url> <email> <senha> <estado>
```

Exemplo:
```bash
python main.py "https://homolog.cod.cni.com.br/Home.aspx" "seu.email@exemplo.com" "sua_senha" "MG - FIEMG"
```

## Funcionalidades

- Automação de login usando Selenium
- Resolução automática de CAPTCHA usando Google Vision API
- Manipulação de teclado virtual
- Sistema de retry para tentativas falhas
- Logging detalhado das operações

## Estrutura do Projeto

```
.
├── key/
│   └── quebra-captcha-b2266280152a.json
├── screenshots/
├── main.py
├── requirements.txt
└── README.md
```

## Logs

Os logs são salvos em:
- Console (stdout)
- Arquivo `login_automation.log`

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request 