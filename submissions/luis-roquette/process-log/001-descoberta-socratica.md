# Diário de processo: descoberta socrática

- **Início:** 21 de setembro de 2026
- **Estado:** Onda 1 em andamento
- **SPEC:** ainda não criada

## Protocolo de registro

Cada pergunta e resposta será registrada durante a sessão. A resposta literal de Luis será preservada; interpretação e consequência serão descritas separadamente, em português revisado. Nenhuma interpretação será apresentada como decisão humana sem confirmação.

## Onda 1: problema, decisão e usuário

### Pergunta 1

Qual deve ser a decisão principal que o CEO conseguirá tomar após cinco minutos com nossa entrega?

- A. Onde investir para reduzir churn de receita.
- B. Quais contas o CS deve abordar imediatamente.
- C. Qual problema de produto ou suporte corrigir primeiro.

### Resposta de Luis

> C

### Interpretação

A entrega deve ajudar o CEO a escolher qual problema sistêmico de produto ou suporte merece correção prioritária. O centro da solução será a causa raiz e a decisão de intervenção, não apenas uma previsão de churn ou uma fila de contas.

### Consequência para o desenho

Precisaremos comparar problemas concorrentes por evidência, receita exposta, quantidade de contas afetadas e possibilidade de ação. A lista de contas em risco continua obrigatória pelo briefing, mas funcionará como evidência e instrumento operacional da recomendação principal.

### Ponto ainda aberto

Ainda não sabemos se devemos começar com uma hipótese sobre a área responsável ou deixar os dados escolherem entre produto, suporte e fatores comerciais.

### Pergunta 2

Devemos iniciar sem uma área culpada e deixar os dados escolherem?

- A. Sim: produto, suporte, cobrança/plano e aquisição competem igualmente.
- B. Produto deve ser a hipótese principal.
- C. Suporte deve ser a hipótese principal.
- D. Cobrança, plano ou contrato deve ser a hipótese principal.

### Resposta de Luis

> A

### Interpretação

A investigação começa com tese zero. Nenhuma área será favorecida antes da análise; produto, suporte, cobrança/plano e aquisição competirão pela força da evidência.

### Consequência para o desenho

A solução precisará aplicar critérios comparáveis às causas candidatas e mostrar evidências contrárias, não somente as que confirmam a narrativa vencedora. Isso reduz o risco de adaptar os dados a uma hipótese escolhida cedo demais.

### Ponto ainda aberto

Precisamos definir como priorizar uma causa quando quantidade de contas afetadas e receita exposta apontarem para direções diferentes.

### Pergunta 3

Quando quantidade de contas e receita exposta apontarem para causas diferentes, como devemos priorizar?

- A. Maior receita mensal exposta.
- B. Maior quantidade de contas afetadas.
- C. Matriz multicritério: receita, contas, confiança da evidência e possibilidade de ação.
- D. Dois rankings separados, sem prioridade final única.

### Resposta de Luis

> C

### Interpretação

A prioridade não será definida por uma única métrica. Cada causa candidata será avaliada por impacto financeiro, alcance entre contas, confiança da evidência e viabilidade de intervenção.

### Consequência para o desenho

A solução deverá mostrar as dimensões separadamente e explicar qualquer síntese de prioridade. Pesos e thresholds não poderão parecer precisão científica se forem escolhas de negócio; precisarão estar visíveis e passar por análise de sensibilidade.

### Ponto ainda aberto

Precisamos definir o horizonte da recomendação: resposta imediata, correção estrutural ou sequência das duas.

### Pergunta 4

Qual horizonte deve orientar a recomendação principal?

- A. Ação emergencial executável em até uma semana.
- B. Correção estrutural para os próximos 30–90 dias.
- C. Sequência das duas: contenção imediata seguida da correção estrutural.
- D. Estratégia anual de retenção.

### Resposta de Luis

> C

### Interpretação

A recomendação deverá operar em duas velocidades. Primeiro, uma contenção que reduza exposição imediata; depois, uma correção estrutural que remova ou reduza a causa sistêmica.

### Consequência para o desenho

Cada causa prioritária precisará de duas ações conectadas: uma medida de curto prazo, executável em até uma semana, e uma iniciativa de 30–90 dias com responsável, métrica e resultado esperado. A contenção não poderá ser apresentada como solução definitiva.

### Ponto ainda aberto

Precisamos escolher qual artefato apresentará essa decisão ao CEO primeiro, antes dos detalhes analíticos e operacionais.

### Pergunta 5

Qual artefato o CEO deve encontrar primeiro?

- A. Memorando executivo de uma página com causa e decisão recomendada.
- B. Dashboard interativo com filtros e comparações.
- C. Fila operacional de contas e ações para o CS.
- D. Entrega em camadas: decisão executiva primeiro, dashboard como evidência e fila de contas para execução.

### Resposta de Luis

> D

### Interpretação

A entrega atenderá três níveis de leitura sem obrigar o CEO a percorrer detalhes técnicos: decisão executiva primeiro, evidência explorável para verificação e fila operacional para transformar a recomendação em ação.

### Consequência para o desenho

As três camadas deverão compartilhar a mesma fonte de dados e os mesmos critérios. Não serão três produtos independentes. A arquitetura deverá permitir leitura progressiva, evitando números ou prioridades divergentes entre resumo, dashboard e fila de contas.

## Síntese provisória da Onda 1

- **Decisão principal:** escolher qual problema sistêmico corrigir primeiro.
- **Postura analítica:** tese zero; nenhuma área começa favorecida.
- **Priorização:** matriz transparente de impacto, alcance, confiança e possibilidade de ação.
- **Horizonte:** contenção em até uma semana e correção estrutural em 30–90 dias.
- **Entrega:** decisão executiva, dashboard de evidências e fila operacional conectados.

### Estado da onda

Aguardando confirmação de Luis. Após a aprovação, a Onda 2 investigará sucesso, evidências e prioridades mensuráveis com base nas cinco decisões acima.
