# Guia de contribuição

## Fluxo de trabalho

1. Escolha uma issue e confirme suas dependências.
2. Atualize a branch `main` local.
3. Crie uma branch curta a partir de `main`.
4. Implemente somente o escopo da issue.
5. Execute os testes e verificações da área alterada.
6. Abra um pull request usando o template do projeto.
7. Obtenha ao menos uma revisão de outra frente antes do merge.

## Branches

Use um destes formatos:

```text
feat/123-ticket-create
fix/145-login-error
chore/110-ci
docs/120-readme
```

Não faça push direto na `main` depois que a proteção da branch estiver configurada.

## Commits

Use Conventional Commits em português:

```text
tipo(escopo): descricao curta no imperativo
```

Tipos permitidos: `feat`, `fix`, `test`, `docs`, `chore`, `ci` e `refactor`.

Exemplo:

```text
feat(tickets): cria abertura de chamados
```

Cada integrante deve usar seu próprio nome e o e-mail associado ao GitHub. Não compartilhe contas e não produza commits em nome de outra pessoa.

## Pull requests

- Relacione a issue.
- Explique como testar.
- Inclua evidência dos testes.
- Para interface, inclua screenshot ou gravação curta.
- Não inclua segredos, credenciais pessoais ou dados bancários reais.
- Atualize contrato e documentação quando o comportamento público mudar.

## Segredos e dados

- Use `.env` local; nunca o adicione ao Git.
- O `.env.example` deve conter apenas nomes e valores seguros de desenvolvimento.
- Use exclusivamente usuários e dados fictícios com domínios reservados, como `example.test`.
- Revise o diff antes de todo commit.
