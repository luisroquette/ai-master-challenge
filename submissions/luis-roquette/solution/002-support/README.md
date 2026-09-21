# Support Decision Copilot — prova de ambiente

Este checkpoint contém apenas uma prova sintética de navegação, formulário editável,
transação SQLite, releitura por nova conexão e download do mesmo CSV persistido. Não há
dados pessoais, inferência, métrica real, API paga ou serviço externo no uso da aplicação.

## Preparação

Requer Python 3.12, `make`, `curl` e `unzip`.

```bash
make PYTHON=python3.12 doctor
make PYTHON=python3.12 setup
make PYTHON=python3.12 demo
```

O lock é gerado uma única vez no ambiente gerenciado com `make bootstrap-lock`. Depois,
`make setup` instala as versões bloqueadas e o pacote local sem resolver dependências.
O ambiente reproduzido usou Python 3.12, Streamlit 1.64.0, pandas 2.3.3,
scikit-learn 1.9.1, joblib 1.6.0, pytest 8.4.2 e Ruff 0.16.8.

## Comandos atuais

- `make doctor`: valida runtime, lock, ferramentas, fontes públicas ou CSVs já locais.
- `make test`: executa a prova de import, UI, persistência e CSV.
- `make lint`: executa Ruff.
- `make app`: inicia a prova Streamlit.
- `make demo`: valida e prepara o ambiente antes de iniciar a prova.
- `make data`: baixa os dois CSVs públicos, sem credenciais.
- `make reproduce`: falha explicitamente até o pipeline ser criado em step posterior.
