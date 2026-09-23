# Método de Construção Cognitiva em Loops

## Propósito

O Método de Construção Cognitiva em Loops, ou MCCL, organiza a criação assistida por IA como uma sequência de entendimento, decisão, especificação, implementação e prova. A ideia central é simples: a IA não deve correr para produzir uma solução antes de demonstrar que compreendeu o problema, e nenhuma etapa avança apenas porque “parece pronta”. Cada fase termina com evidência e um critério explícito de saída.

O método foi aplicado ao Challenge 003 para construir um Lead Scorer utilizável por vendedores e gestores. O resultado prático é uma aplicação que abre com uma fila curta de trabalho e explica qual lead merece foco, por quê, quais sinais sustentam a recomendação e qual ação deve ser executada.

## 1 Absorção por redundância

Antes de pesquisar soluções ou escrever código, o briefing foi relido integralmente em ciclos. O objetivo de parada foi definido como duas passadas consecutivas sem novos achados, dúvidas ou requisitos. Essa redundância necessária reduz o risco de transformar uma leitura superficial em arquitetura.

O registro ocorreu durante a leitura, não depois. Cada descoberta recebeu um fragmento curto no diário, preservando origem, decisão e impacto. Essa disciplina criou uma fonte contemporânea de verdade e evitou reconstruir retrospectivamente uma história mais limpa do que o processo real.

## 2 Descoberta socrática adaptativa

A solução foi discutida antes da SPEC por meio de seis ondas de perguntas. Cada pergunta tinha opções mutuamente exclusivas, recomendação quando útil e uma consequência operacional clara. As ondas posteriores dependeram das respostas anteriores.

1. **Resultado e usuário:** definiu a decisão que o vendedor deveria tomar e a métrica norteadora.
2. **Fluxo comercial:** separou atualização contínua, mudança material e intervenção temporária do gestor.
3. **Dados e verdade temporal:** definiu splits temporais, leakage, rótulos e dados insuficientes.
4. **Score e explicação:** definiu modelos candidatos, calibração, fallback e explicações fiéis.
5. **Experiência e operação:** definiu filas separadas, filtros, detalhes e próxima ação.
6. **Arquitetura e prova:** consolidou Streamlit, Python, dados versionados, execução e validação.

O valor dessa fase não estava no volume de perguntas, mas na dependência entre elas. A arquitetura surgiu das decisões aprovadas, em vez de ser apresentada pronta pela IA.

## 3 SDD e especificação verificável

Com a descoberta aprovada, a metodologia SDD transformou decisões em requisitos, critérios de aceite, riscos e contratos de teste. A SPEC separou `Engaging` de `Prospecting`, proibiu features de leakage, definiu quando probabilidades poderiam ser publicadas e estabeleceu como cada explicação seria reconstruída.

A especificação também descreveu falhas aceitáveis. Quando a evidência não sustenta probabilidade, o sistema deve se abster e publicar prioridade relativa. Quando um dado crítico falta, o deal permanece visível como “Dados insuficientes”; ele não recebe média, zero ou confiança inventada.

## 4 Arquitetura mínima e rastreável

A arquitetura usa quatro módulos principais: carregamento e recuperação dos dados, scoring e evidência, interface Streamlit e testes. Os quatro CSVs reais são versionados com manifesto e checksums. O runtime não chama APIs de IA e o playbook de ações é determinístico.

A menor arquitetura suficiente venceu alternativas mais complexas. Não foram adicionados banco, autenticação, API própria, orquestrador ou infraestrutura que o protótipo não exigia. Os limites foram documentados em vez de escondidos.

## 5 Implementação em feedback looping

Cada etapa seguiu o mesmo ciclo:

> Planejamento → Revisão → Execução → Teste

Se o teste falhava, a etapa voltava ao início do loop. A causa era corrigida na fronteira compartilhada e todos os gates aplicáveis eram repetidos. O avanço só ocorria após validação ou diante de um impedimento externo explícito.

Esse ciclo expôs erros reais: valores `pd.NA` incompatíveis com o modelo, seleção divergente entre grades, identidade incorreta da fonte, serialização de estruturas imutáveis e verificações live que afirmavam mais do que a evidência permitia. As correções receberam regressões focais, não apenas ajustes visuais.

## 6 Redundância necessária

Depois da primeira implementação completa, iniciou-se uma busca específica por erros, falhas e lacunas. O critério de parada voltou a ser duas passadas completas consecutivas sem novos apontamentos relevantes. Um achado reiniciava a contagem.

Essa fase distinguiu “funciona uma vez” de “foi reavaliado como sistema”. Ela revisou dados, score, explicações, estados vazios, navegação, testes, documentação e identidade da execução.

## 7 Lapidação de produto e interface

A lapidação não se limitou à estética. O primeiro dashboard ainda exigia interpretação demais. O feedback humano redefiniu a pergunta central: o vendedor deve abrir a ferramenta e saber onde focar sem filtrar ou ordenar manualmente.

O produto evoluiu em três movimentos:

1. o ranking ganhou um foco automático por estágio;
2. o foco virou **Minha fila agora**, com até três oportunidades acionáveis;
3. cada item passou a separar **Por quê**, **Sinais** e **Ação**.

A nota 10/10 só foi restabelecida após a primeira dobra responder, em sequência: qual lead, por que ele, quais sinais justificam a atenção e qual ação executar.

## 8 Segurança proporcional ao projeto

A auditoria classificou 19 controles como FEITO, NÃO FEITO ou NÃO APLICÁVEL. Controles de login, cadastro, cookies, senhas, banco e RLS não foram simulados em um protótipo que não possui essas superfícies.

Os controles pertinentes foram tratados: nenhuma chave é necessária no runtime; dados públicos são validados por checksum; prioridades temporárias geram eventos locais append-only com permissões restritas, `fsync` e encadeamento SHA-256; adulteração faz a operação falhar fechado. Como não existe autenticação, o ator permanece explicitamente não verificado.

O único gap aceito é backup externo. Um bundle Git local foi criado e restaurado com sucesso, mas a cópia externa foi adiada para respeitar o embargo de publicação.

## 9 Documentação como instrumento de engenharia

O diário registra intenção, hipótese, pergunta, resposta, erro, causa, correção e evidência. Ele não é um memorial produzido depois do resultado; é parte do mecanismo de decisão. Os commits preservam a evolução técnica e o documento de avaliação separa provas executadas, revisões estáticas e gates ainda pendentes.

Essa disciplina materializa uma ideia autoral de Luis: ganha quem documenta. Como na analogia atribuída a Silvio Santos, a galinha vende mais ovos porque anuncia quando põe. O trabalho precisa funcionar, mas também precisa tornar visível como foi pensado, construído, corrigido e validado.

## Resultado do método

O MCCL produziu mais do que um score. Produziu uma cadeia auditável entre problema de negócio, decisão humana, requisito, implementação e prova. No Challenge 003, essa cadeia levou a uma solução que se abstém quando a probabilidade não é confiável e, ainda assim, oferece ao vendedor uma fila útil e explicável.

O método não promete eliminar erro. Ele torna o erro observável, corrigível e documentado antes da entrega.
