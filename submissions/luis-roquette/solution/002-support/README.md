# Support Decision Copilot — ambiente e dados de desenvolvimento

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
- `make reproduce`: valida fontes, sanitiza e grava manifesto/splits de desenvolvimento.

## Fontes e retomada

Execute `make data` uma vez, depois `make reproduce` no ambiente gerenciado.
Se o download falhar, baixe os ZIPs públicos e extraia os nomes exatos abaixo em
`data/raw/`; repita `make reproduce`. Nenhum login, CSV sintético ou API paga serve de fallback.

| Domínio | Fonte pública | Nome esperado |
|---|---|---|
| Customer | [Kaggle](https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset) | `customer_support_tickets.csv` |
| IT | [Kaggle](https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset) | `all_tickets_processed_improved_v3.csv` |

A leitura real nesta etapa confirmou os schemas e oito classes IT: Access,
Administrative rights, HR Support, Hardware, Internal Project, Miscellaneous,
Purchase e Storage. Contagens são reavaliadas em cada execução, não hardcoded.
Raw, runtime e artefatos são ignorados pelo Git.

## Contrato de privacidade e qualidade

`data.py` entrega somente campos operacionais permitidos. Nome/email/idade/gênero,
produto e data de compra não saem da fronteira de ingestão. Nomes conhecidos, emails,
telefones, URLs, IPs e identificadores alfanuméricos são mascarados. Nome por contexto,
entidade capitalizada desconhecida ou identificador residual suspeito coloca a linha
inteira em quarentena; somente a contagem permanece, sem texto bruto em logs/erros.
Datas ilegíveis viram sentinela inválida; notas inválidas viram `null`, nunca zero.

Regexes não comprovam anonimização universal: nomes minúsculos sem contexto e
near-duplicates sem igualdade canônica podem escapar. Falsos positivos de nomes
também reduzem suporte. Toda amostra pública exige revisão humana; manifesto marca
`pending_human_review`. Para revisão, selecionar somente amostras sanitizadas de
`artifacts/data/*-train.json`; registrar aprovação/reprovação no diário. Falha exige
ajuste do sanitizador e nova reprodução, nunca publicação da amostra recusada.

## Splits e manifesto

Cada domínio agrupa texto normalizado com casefold, pontuação/espaços normalizados e
números/identificadores variáveis substituídos. O menor ID é representante estável;
grupos com rótulos conflitantes ficam em quarentena. Por classe: treino `floor(0,6*n)`,
calibração `floor(0,2*n)` e teste com o restante. Calibração se divide uma única vez
em duas metades seeded, `floor/ceil`; mínimo de dez representantes por classe garante
cinco folds de treino e presença nas duas metades. Insuficiência desativa o domínio
sem duplicar linhas. IDs e grupos são disjuntos entre os três conjuntos.

`DatasetSplit.test` e manifesto contêm apenas IDs/grupos de teste e contagens agregadas;
features, resoluções e rótulos individuais finais não são exportados antes dos locks.
Os próximos steps poderão recuperar as linhas finais da mesma fonte/hash somente após
congelar modelo, calibração, regras e thresholds. Diagnóstico inicial usa desenvolvimento.
Modelos, fila final e recuperação constam como indisponíveis, sem resultados inventados.

JSON é finito, canônico e escrito por substituição atômica; o manifesto é publicado por
último e não inclui seu próprio hash. Ele registra hash da fonte/lock/configuração,
fingerprint dos arquivos de código, versões, exclusões e IDs/grupos. Comparações entre
reproduções removem somente `generated_at`; hashes binários e lógicos são registrados.

Na reprodução real do step 02, Customer passou de 8.469 linhas a 1.392 sanitizadas e
1.136 representantes após retirar 255 linhas conflitantes e uma duplicata. IT passou
de 47.837 a 26.472 representantes sanitizados. Quarentena: 7.077 Customer e 21.365 IT.
Essas exclusões podem enviesar análises e devem acompanhar seus denominadores; somente
34 linhas Customer sanitizadas têm satisfação observada. Os dois splits tiveram
suporte suficiente; isso não comprova sinal preditivo nem qualidade das respostas.
