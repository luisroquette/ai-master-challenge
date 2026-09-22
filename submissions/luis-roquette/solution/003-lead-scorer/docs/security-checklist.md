# Checklist de segurança

Data da análise: 22 de setembro de 2026
Escopo: aplicação Streamlit do Challenge 003, dados estáticos públicos CC0, execução local, sem autenticação, banco de dados, envio de e-mail, API própria ou deploy público.

## Critério de classificação

- **FEITO:** controle pertinente ao protótipo e atendido com evidência no código ou no histórico.
- **NÃO FEITO:** controle pertinente ao comportamento existente, mas ainda incompleto.
- **NÃO APLICÁVEL:** a superfície correspondente não existe neste protótipo. Deve ser reavaliado se o escopo mudar.

## Parecer item a item

- [ ] **NÃO APLICÁVEL — Rate limit no login.** Não existe login nem endpoint de autenticação. O seletor de perfil é demonstrativo e a interface declara que não autentica o usuário.
- [ ] **NÃO APLICÁVEL — CAPTCHA e normalização de e-mail no cadastro.** Não existe cadastro, identidade por e-mail ou formulário público de criação de conta.
- [ ] **NÃO APLICÁVEL — Rate limit no envio de e-mail e proteção contra aliases.** A aplicação não recebe nem envia e-mails.
- [ ] **NÃO APLICÁVEL — Gerar segredo ou chave de API do frontend.** Não existe API própria. Um segredo nunca deverá ser embarcado no frontend; caso uma API seja criada, a credencial deverá permanecer no servidor.
- [ ] **NÃO APLICÁVEL — WAF e detecção avançada de bots no Cloudflare.** Não existe deploy público, domínio próprio ou camada Cloudflare. Reavaliar antes de uma exposição pública fora da hospedagem do challenge.
- [ ] **NÃO FEITO — Logs de auditoria.** A única mutação é a prioridade temporária do gestor. Ela registra gestor, horário UTC, fingerprint e geração apenas em `st.session_state`, mas não produz trilha durável. O estado some no recálculo, refresh ou encerramento da sessão.
- [ ] **NÃO FEITO — Backup de todo o sistema.** Código e quatro CSVs estão versionados; o dataset pode ser recuperado por manifesto, HTTPS e SHA-256, com rollback transacional. Porém, a revisão atual existe somente na branch local porque a branch remota foi removida por embargo. Não há cópia externa atualizada e testada.
- [ ] **NÃO APLICÁVEL — Sentry.** Não existe runtime público ou serviço persistente a monitorar. Sentry é observabilidade, não blindagem de segurança; reavaliar somente quando houver deploy autorizado.
- [ ] **NÃO APLICÁVEL — Alertas de custo.** O runtime não usa API paga, banco, fila, armazenamento ou infraestrutura faturável própria. O preview é local.
- [x] **FEITO — Ocultar chaves de API.** O projeto não precisa de chaves e nenhuma credencial está presente no código, manifesto, requisitos ou configuração.
- [x] **FEITO — Remover segredos do histórico do Git.** A varredura do diretório atual e do histórico do projeto encontrou zero chaves AWS, OpenAI, GitHub, chaves privadas ou atribuições de segredo de alta confiança. `gitleaks` e `trufflehog` não estão instalados; a evidência é uma varredura regex focal, não certificação externa.
- [ ] **NÃO APLICÁVEL — Usar chave pública para o banco de dados.** Não existe banco. Se um banco cliente-servidor for introduzido, o navegador poderá receber apenas chave publicável limitada por autorização e RLS, nunca credencial administrativa.
- [ ] **NÃO APLICÁVEL — Row-Level Security.** Não existe banco nem tabela persistente.
- [ ] **NÃO APLICÁVEL — Criptografar dados sensíveis.** Os dados versionados são o dataset público CC0 do challenge e não existem senhas, tokens ou dados privados. A recuperação usa HTTPS e valida SHA-256; criptografia em repouso não é necessária neste escopo.
- [ ] **NÃO APLICÁVEL — Impor autenticação no servidor.** Não existem contas nem dados protegidos. O seletor vendedor/gestor não é controle de acesso e não deverá ser tratado como tal. Autenticação server-side será bloqueante se o protótipo receber dados reais de CRM.
- [ ] **NÃO APLICÁVEL — Restringir acesso aos registros.** Todos os registros pertencem ao dataset público demonstrativo. Se forem substituídos por dados reais, autorização por carteira deverá ser aplicada no servidor antes da consulta, não apenas por filtro visual.
- [x] **FEITO — Impedir adulteração de campos.** O aplicativo é somente leitura para os dados e scores. Resultados e pins são estruturas imutáveis; a prioridade temporária valida papel, estágio, pertencimento ao portfólio, fingerprint e geração, sem alterar score ou CSV.
- [ ] **NÃO APLICÁVEL — Proteger cookies de sessão.** Não existe sessão autenticada; `st.session_state` guarda apenas estado efêmero de interface. Cookies seguros passam a ser requisito se autenticação for adicionada.
- [ ] **NÃO APLICÁVEL — Armazenar senhas com hash.** A aplicação não coleta nem armazena senhas.

## Parecer geral

O protótipo é adequado ao escopo atual: leitura local de dados públicos, sem credenciais e sem serviços externos. A recuperação de dados já possui HTTPS obrigatório, redirects validados, limites de tamanho, allowlist do ZIP, SHA-256, rejeição de symlinks, lock e rollback verificado.

Ele **não deve receber dados reais de CRM nem ser tratado como sistema autenticado** no estado atual. Antes disso, autenticação server-side, autorização por carteira, RLS, proteção de sessão, auditoria persistente e tratamento de dados sensíveis mudariam de “não aplicável” para requisitos bloqueantes.

## Fila de tratamento

1. **Logs de auditoria persistentes:** decidir se a repriorização continuará efêmera ou se o produto passará a persistir intervenções.
2. **Backup externo:** executar somente depois da autorização expressa para remover o embargo e publicar a revisão validada.

Nenhuma remediação foi implementada nesta etapa; este documento é apenas o diagnóstico solicitado.
