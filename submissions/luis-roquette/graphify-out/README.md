# Grafo da solução — Challenge 003

Abra [`graph.html`](graph.html) para navegar por código, testes, documentos, imagens e transcrições em um único mapa interativo.

## Artefatos

1. [`graph.html`](graph.html): visualização interativa autocontida.
2. [`GRAPH_REPORT.md`](GRAPH_REPORT.md): comunidades, hubs, conexões e perguntas sugeridas.
3. [`QUESTION_TRACE_REPORT.md`](QUESTION_TRACE_REPORT.md): rastreamento de todos os hubs, conexões surpreendentes e perguntas.
4. [`diagnostics.json`](diagnostics.json): integridade do grafo final em formato verificável.
5. [`graph.json`](graph.json): dados estruturados completos.

## Escopo e leitura honesta

- O grafo combina AST local com extração semântica dos documentos, das cinco imagens e das transcrições locais dos dois vídeos.
- Relações `EXTRACTED` aparecem diretamente na fonte; relações `INFERRED` são hipóteses navegacionais, não prova causal ou de runtime.
- O artefato final tem zero endpoints ausentes, zero endpoints pendentes, zero duplicatas exatas e zero colapsos de arestas; cinco auto-relações AST permanecem declaradas no diagnóstico.
- O DOCX não foi convertido porque o extra opcional de Office não estava instalado; o Markdown equivalente foi indexado.
- Nenhuma API paga de IA foi chamada para criar o grafo.
