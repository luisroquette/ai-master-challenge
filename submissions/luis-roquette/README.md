# Lead Scorer — Challenge 003

**Luis Fernando Roquette** · [LinkedIn](https://br.linkedin.com/in/luisroquette)

## Comece aqui

1. **[Abra a experiência visual guiada](delivery/index.html)** — visão executiva do problema, produto e método.
2. **[Rode o produto](solution/003-lead-scorer/README.md)** — aplicação Streamlit funcional com dados reais.
3. **Veja a construção** — [vídeo explicativo de 5:48](delivery/assets/video-notebooklm.mp4), [infográfico executivo](delivery/assets/infografico-notebooklm.png) e [mapa mental expandido](delivery/assets/mapa-mental-notebooklm.png), gerados no NotebookLM a partir de uma fonte curada.

> O vendedor abre o sistema e recebe uma fila curta: **qual lead priorizar, por quê, quais sinais observar e qual ação executar**.

## Resultado

- 8.800 oportunidades reais analisadas; 2.089 ativas priorizadas.
- Filas separadas para `Engaging` e `Prospecting`, sem comparar escalas incompatíveis.
- Probabilidades foram ocultadas porque as quatro rotas avaliadas falharam nos gates de suporte.
- Gestor e vendedor recebem recomendações acionáveis; o sistema não escreve no CRM.

<details>
<summary><strong>Como a solução foi construída</strong></summary>

O Método de Construção Cognitiva em Loops (MCCL) combinou leitura redundante, seis ondas socráticas adaptativas, SDD, implementação em feedback loop, lapidação e segurança. A sequência completa está em [Metodologia](docs/metodologia-construcao-cognitiva-em-loops.md), [Prompts-chave](docs/prompts-chave.md) e [Diário contemporâneo](process-log/003-lead-scorer.md).

Ferramentas: OpenAI Codex, SDD Context Engineering Kit, Frontend Design, Git e GitHub.

A principal correção humana foi mudar o objetivo de “um dashboard com score” para “uma ferramenta que indique onde agir”. As revisões também bloquearam leakage, ambiguidade entre estágios e a publicação indevida de probabilidades.
</details>

<details>
<summary><strong>Evidências, limitações e recomendações</strong></summary>

- [Métricas e avaliação](solution/003-lead-scorer/docs/evaluation.md)
- [Checklist de segurança](solution/003-lead-scorer/docs/security-checklist.md)
- [Versão executiva em DOCX](docs/metodologia-construcao-cognitiva-em-loops.docx)
- Limites: dados estáticos, perfis demonstrativos sem autenticação, nenhuma escrita no CRM, sem inferência causal.
- Próximo passo recomendado: piloto controlado antes de integrar CRM ou publicar probabilidades.
</details>

Uma URL pública, o Arcade e qualquer envio aos avaliadores dependem de validação final e autorização expressa.
