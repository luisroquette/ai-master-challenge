# Check de segurança — Support Decision Copilot

Data: 2026-09-22  
Escopo: código, configuração e histórico Git da solução `002-support`; deploy público
Streamlit observado. Nenhuma configuração privada do provedor foi presumida.

## Parecer geral

**Risco atual: alto para uso operacional; aceitável somente como demo pública sem dados
reais.** A solução foi construída como protótipo offline/fail-closed, não como sistema
multiusuário. Ela não possui identidade, autorização ou armazenamento persistente de
produção. O maior risco não é uma senha fraca: é qualquer visitante poder registrar
decisões e baixar todos os registros do SQLite compartilhado.

## Checklist

| # | Controle | Estado | Risco | Parecer |
|---:|---|---|---|---|
| 1 | Rate limit no login | Não aplicável hoje | — | Não existe login. Passa a P0 quando autenticação for criada. |
| 2 | CAPTCHA + normalização de e-mail no cadastro | Não aplicável hoje | — | Não existe cadastro nem e-mail de usuário. CAPTCHA só após abuso mensurável; normalização precisa preservar identidade do provedor. |
| 3 | Rate limit de e-mail e defesa contra alias | Não aplicável hoje | — | Não há envio de e-mail. Futuro limite deve usar conta, IP, destino canônico e janela temporal; alias não pode criar cota nova. |
| 4 | Segredo e chave API no frontend | Rejeitado como desenho | Crítico se feito | Frontend público não guarda segredo. Usar segredo apenas no servidor; frontend recebe somente identificador público com escopo mínimo. |
| 5 | WAF e detecção avançada de bots (Cloudflare) | Ausente | Médio | Deploy usa domínio do Streamlit; nenhum WAF/bot rule próprio foi encontrado. Avaliar proxy/domínio controlado somente após autenticação. |
| 6 | Logs de auditoria | Parcial | Alto | SQLite registra decisões sanitizadas, versões e timestamps. Faltam ator autenticado, login/falha, leitura, export, administração, IP/UA protegido, retenção e trilha imutável central. |
| 7 | Backup e recuperação | Ausente | Crítico | `data/runtime/decisions.sqlite3` está ignorado e no filesystem efêmero do Streamlit. Reinício pode apagar decisões; não há snapshot, retenção, restore testado nem runbook. Artefatos analíticos são reproduzíveis, decisões não. |
| 8 | Sentry | Ausente | Médio | Nenhum SDK/DSN/configuração. Antes de instalar, definir redaction para não enviar texto de tickets, PII ou segredos. |
| 9 | Alertas de custo | Ausente / baixa exposição atual | Baixo | Não há API paga; treino é local no boot. Faltam alertas do provedor e limites de CPU/storage/reboot. |
| 10 | Ocultar chaves de API | Coberto por ausência | Baixo hoje | Não foram encontradas chaves ou `.env` rastreados. Se surgir integração, segredo deve ficar no cofre do provedor e nunca no browser/log. |
| 11 | Remover segredos do histórico Git | Sem indício, não certificado | Médio | Busca por padrões conhecidos no histórico da pasta não encontrou candidatos; `gitleaks` não está instalado, portanto a prova ainda não é completa. |
| 12 | Chave pública para banco | Não aplicável | — | O banco é SQLite local e não usa chave. Em banco remoto, chave pública não substitui autorização; credencial privilegiada fica somente no servidor. |
| 13 | Row-Level Security | Não aplicável hoje | Crítico numa migração multiusuário | SQLite não oferece RLS e não há tenants/usuários. Banco remoto deve negar por padrão e testar políticas por organização e papel. |
| 14 | Criptografia de dados sensíveis | Parcial | Alto | A aplicação sanitiza PII e pretende não persistir dado sensível, mas o SQLite não tem criptografia de aplicação nem chave gerenciada. TLS/criptografia do provedor não foram verificados. |
| 15 | Autenticação no servidor | Ausente | Crítico | App público não autentica servidor-side. Ocultar navegação não resolveria; toda mutação e export precisam exigir identidade validada no servidor. |
| 16 | Restringir acesso aos registros | Ausente | Crítico | A página Evidências lista e exporta todo o banco compartilhado para qualquer visitante. Não há ownership, papel ou escopo por organização. |
| 17 | Impedir adulteração de campos | Parcial forte | Alto residual | SQL parametrizado, validação fechada, UUID idempotente e schemas reduzem adulteração. Sem ator autenticado, qualquer visitante ainda pode criar uma decisão válida. |
| 18 | Proteger cookies de sessão | Não verificável / sem sessão de auth | Alto ao adicionar auth | A aplicação não emite cookie de autenticação próprio. Flags `Secure`, `HttpOnly`, `SameSite`, rotação, expiração e CSRF devem ser verificadas quando houver sessão. |
| 19 | Hash de senhas | Não aplicável | — | Não há senha local. Preferir IdP/OIDC; se senha existir, usar Argon2id com parâmetros versionados, salt automático e proteção contra credential stuffing. |

## Ordem de tratamento

1. **P0 — fronteira de confiança:** autenticação servidor-side, autorização e bloqueio de
   mutações/exports anônimos.
2. **P0 — persistência:** banco durável, backup automático, retenção e restore testado.
3. **P1 — auditoria:** ator, evento, alvo, resultado e correlação em log append-only com
   redaction e acesso restrito.
4. **P1 — observabilidade:** Sentry com scrubbing e alertas de disponibilidade/custo.
5. **P2 — borda:** rate limits, WAF/bot management, CAPTCHA somente nos fluxos que
   realmente existirem.

## Evidência examinada

- `deploy_app.py`: bootstrap público, sem autenticação ou middleware de autorização.
- `src/support_copilot/store.py`: SQLite transacional, validação, SQL parametrizado,
  idempotência e export; sem identidade, criptografia ou backup.
- `.gitignore`: `.env` não aparece explicitamente; SQLite/runtime são ignorados.
- `.streamlit/config.toml`: somente telemetria, watcher e modo headless.
- Git atual e histórico da pasta: nenhum segredo reconhecido pelos padrões executados;
  varredura especializada ainda pendente.

## Gate para produção

Não usar dados reais nem decisões operacionais antes de fechar P0. O protótipo público
deve continuar limitado a dados sanitizados de demonstração. Cada correção futura exige
teste de regressão, evidência no diário e nova medição de risco residual.
