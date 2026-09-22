# Lead Scorer 003 — fonte curada para produção visual

## Instrução editorial

Crie materiais em português do Brasil para avaliadores do AI Master Challenge. Comece pelo produto funcionando e trate o processo como evidência. Não invente métricas, causalidade, publicação, autenticação ou integração com CRM.

## A pergunta central

“Nossos vendedores gastam tempo demais em deals que não vão fechar e deixam oportunidades boas esfriar. Quero uma ferramenta que o vendedor abra, veja o pipeline e saiba onde focar.”

## A resposta construída

O Lead Scorer é uma aplicação Streamlit que transforma 8.800 oportunidades reais de CRM em uma fila curta e explicável. Há 2.089 oportunidades ativas. A primeira dobra informa:

1. qual lead priorizar;
2. por que ele aparece primeiro;
3. quais sinais sustentam a atenção;
4. qual ação comercial executar.

O produto oferece visões de vendedor e gestor. O gestor pode orientar temporariamente uma prioridade sem alterar o score; a ação gera auditoria local encadeada. A aplicação não escreve no CRM.

## Decisões técnicas importantes

- `Engaging` e `Prospecting` usam filas independentes porque suas escalas não são comparáveis.
- `close_value`, `close_date`, estágio final e derivados foram proibidos como features; Won/Lost é apenas o rótulo.
- O objetivo econômico considerado foi probabilidade de fechamento multiplicada pelo preço do produto.
- Quatro rotas probabilísticas superaram baselines de erro, mas falharam no suporte das faixas; por isso, o produto publica prioridade relativa, não probabilidade ou receita esperada.
- Cada explicação é reconstruída a partir da lógica realmente usada, sem texto genérico gerado por IA.

## Evolução do produto

1. O briefing foi relido até duas passadas consecutivas sem novos achados.
2. Seis ondas socráticas adaptativas definiram problema, métrica, dados, validação, experiência e entrega antes da SPEC.
3. A SPEC guiou requisitos, arquitetura, critérios de aceite e contratos de teste.
4. A implementação seguiu Planejamento, Revisão, Execução e Teste; falhas voltavam ao início do loop.
5. Redundância, lapidação de UI/UX e segurança fecharam o produto.
6. O feedback humano mudou o centro da interface: de “dashboard que explica” para “ferramenta que diz onde agir”.

## Método autoral

O Método de Construção Cognitiva em Loops (MCCL) tem oito movimentos:

1. absorção redundante do briefing;
2. descoberta socrática em ondas adaptativas;
3. SPEC orientada por decisões aprovadas;
4. revisão e lapidação da SPEC;
5. implementação em feedback looping;
6. redundância necessária para encontrar lacunas;
7. lapidação técnica, visual, de UX e segurança;
8. entrega verificável, com produto primeiro e processo como prova.

O fechamento de cada revisão exige duas rodadas consecutivas sem novos achados relevantes.

## Intervenções humanas decisivas

- “Antes da SPEC, precisamos criá-la e discutir o projeto”: impediu arquitetura prematura.
- “Elimine viés”: separou sinais legítimos de informação disponível apenas após o fechamento.
- “Menor necessidade de intervenção humana”: criou a fila automática de foco.
- “Focar neste lead pois... Atenção neste lead! Sinais...”: converteu ranking em decisão comercial explícita.
- “Ganha quem documenta”: tornou o diário contemporâneo parte central da entrega.

## Evidências e limites

Dados: 8.800 oportunidades, 85 contas, 7 produtos e 35 vendedores. O app prioriza 2.089 oportunidades ativas. Nenhuma probabilidade indevida foi publicada. Os perfis são demonstrativos, não existe autenticação, não há escrita no CRM, os dados são estáticos e não há inferência causal sobre a ação recomendada.

## Briefs dos três materiais

### Vídeo

Vídeo explicativo de 4 a 6 minutos. Estrutura: problema, produto funcionando, decisões que evitam falsos sinais, evolução em oito movimentos MCCL, contribuição humana, limitações e próximo passo. Tom executivo, concreto e sem linguagem promocional vazia.

### Mapa mental

Centro: “Challenge 003 — Lead Scorer”. Ramos: Produto; Dados e score; Método MCCL; Evidências; Limitações. Mostre as relações entre prioridade, explicação, ação e validação.

### Infográfico

Formato 16:9. Título: “Do prompt ao produto”. Destaque os oito movimentos do MCCL e termine com o output operacional: Lead → Por quê → Sinais → Ação.
