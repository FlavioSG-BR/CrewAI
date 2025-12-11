# 📊 Estrutura do Banco de Dados - Gerador de Provas

## 🎯 Visão Geral

O banco de dados foi projetado para ser **escalável**, **flexível** e **auditável**, permitindo:
- Adicionar novas matérias e tópicos facilmente
- Rastrear histórico de alterações
- Suportar múltiplos usuários e provas
- Armazenar diagramas e recursos

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE DOMÍNIO                             │
├─────────────────────────────────────────────────────────────────┤
│  materias  │  topicos  │  dificuldades  │  tipos_questao        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA PRINCIPAL                              │
├─────────────────────────────────────────────────────────────────┤
│  questoes  │  resolucoes  │  alternativas  │  diagramas         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE PROVAS                              │
├─────────────────────────────────────────────────────────────────┤
│  provas  │  prova_questoes  │  gabaritos                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE USUÁRIOS                            │
├─────────────────────────────────────────────────────────────────┤
│  usuarios  │  respostas_usuario  │  estatisticas_usuario        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE AUDITORIA                           │
├─────────────────────────────────────────────────────────────────┤
│  logs_sistema  │  historico_alteracoes  │  sessoes              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Tabelas por Categoria

### 1. Domínio (Configuração)
| Tabela | Descrição |
|--------|-----------|
| `materias` | Matérias disponíveis (Física, Química, Matemática) |
| `topicos` | Tópicos por matéria (MRU, Álgebra, etc.) |
| `dificuldades` | Níveis de dificuldade |
| `tipos_questao` | Tipos (múltipla escolha, dissertativa, etc.) |
| `tags` | Tags para categorização |

### 2. Questões (Core)
| Tabela | Descrição |
|--------|-----------|
| `questoes` | Questões geradas |
| `resolucoes` | Resoluções detalhadas |
| `alternativas` | Alternativas para múltipla escolha |
| `diagramas` | Imagens e gráficos |
| `questao_tags` | Relacionamento questão-tags |

### 3. Provas
| Tabela | Descrição |
|--------|-----------|
| `provas` | Provas criadas |
| `prova_questoes` | Questões em cada prova |
| `gabaritos` | Gabaritos das provas |

### 4. Usuários
| Tabela | Descrição |
|--------|-----------|
| `usuarios` | Usuários do sistema |
| `perfis` | Perfis de acesso |
| `respostas_usuario` | Respostas dos alunos |
| `estatisticas_usuario` | Estatísticas de desempenho |

### 5. Auditoria
| Tabela | Descrição |
|--------|-----------|
| `logs_sistema` | Logs de operações |
| `historico_alteracoes` | Histórico de mudanças |
| `sessoes` | Sessões de usuários |

---

## 🔗 Relacionamentos Principais

```
materias (1) ──────< (N) topicos
    │
    └──< questoes (N) ──────< (N) alternativas
              │
              ├──< resolucoes (1)
              │
              ├──< diagramas (N)
              │
              └──< prova_questoes (N) >────── provas (N)
                                                  │
                                                  └──< respostas_usuario (N)
                                                              │
                                                              └────── usuarios (1)
```

---

## 📁 Arquivos de Migração

```
database/
├── README_DATABASE.md          # Esta documentação
├── 001_schema_base.sql         # Estrutura base
├── 002_tabelas_dominio.sql     # Tabelas de domínio
├── 003_tabelas_questoes.sql    # Tabelas de questões
├── 004_tabelas_provas.sql      # Tabelas de provas
├── 005_tabelas_usuarios.sql    # Tabelas de usuários
├── 006_tabelas_auditoria.sql   # Tabelas de auditoria
├── 007_indices.sql             # Índices para performance
├── 008_dados_iniciais.sql      # Dados seed
└── migrate.py                  # Script de migração
```

---

## 🚀 Como Executar

```bash
# Via Docker
docker-compose exec db psql -U user -d provas_db -f /scripts/001_schema_base.sql

# Via Python
python database/migrate.py --all

# Apenas uma migração
python database/migrate.py --file 001_schema_base.sql
```

---

## 📝 Convenções

1. **Nomenclatura**: snake_case para tabelas e colunas
2. **IDs**: UUID para todas as tabelas principais
3. **Timestamps**: `created_at`, `updated_at` em todas as tabelas
4. **Soft Delete**: `deleted_at` para exclusão lógica
5. **Auditoria**: `created_by`, `updated_by` quando aplicável

