# Pipeline de Consolidação de Dados + Resumo via IA

## Problema
Consolidar manualmente múltiplas planilhas (formatos e padrões inconsistentes) em
um relatório único levava 5 horas/semana. O processo era repetitivo e sujeito a
erro humano (dados duplicados, colunas com nomes diferentes entre arquivos).

## Solução
Script em Python que:
1. Lê automaticamente todos os arquivos `.xlsx`/`.csv` de uma pasta
2. Padroniza nomes de colunas e remove duplicatas
3. Consolida tudo em uma única base
4. Gera métricas agregadas
5. Exporta um relatório final em Excel
6. (Opcional) Usa a API da Anthropic para gerar um resumo em linguagem natural
   dos principais achados

## Resultado
As 5 horas/semana gastas manualmenteforam reduzidas a poucos minutos de execução do script.

## Como rodar

```bash
pip install -r requirements.txt

# Defina sua API key (opcional, só para a etapa de IA)
export ANTHROPIC_API_KEY="sua-chave-aqui"

python consolidar.py
```

## Estrutura
```
.
├── dados_brutos/          # arquivos de entrada (.xlsx/.csv)
├── relatorio_final/       # output gerado
├── consolidar.py          # script principal
├── README.md
└── requirements.txt
```

## Próximos passos
- [ ] Adaptar `limpar_dados()` e `gerar_resumo()` às colunas reais do domínio
- [ ] Adicionar testes básicos
- [ ] Integrar a camada de IA (Fase 3)
