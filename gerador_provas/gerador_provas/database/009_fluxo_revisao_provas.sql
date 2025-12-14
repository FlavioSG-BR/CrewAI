-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 009: FLUXO DE REVISÃO E PROVAS INDIVIDUAIS
-- ============================================================================
-- Descrição: Tabelas para o novo fluxo de negócio com revisão de questões
--            pelo professor e geração de provas individualizadas por aluno
-- Autor: Sistema
-- Data: 2024-12-14
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- NOVOS TIPOS ENUMERADOS
-- ============================================================================

-- Status de revisão de questão
CREATE TYPE provas.status_revisao AS ENUM (
    'pendente',           -- Aguardando revisão do professor
    'em_revisao',         -- Professor está analisando
    'aprovada',           -- Professor aprovou a questão
    'rejeitada',          -- Professor rejeitou (precisa regenerar)
    'correcao_pendente'   -- Professor solicitou correções
);

-- ============================================================================
-- TABELA: QUESTAO_REVISOES
-- ============================================================================
-- Registra o histórico de revisões de cada questão pelo professor

CREATE TABLE IF NOT EXISTS provas.questao_revisoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    professor_id UUID REFERENCES provas.usuarios(id),
    
    -- Status da revisão
    status provas.status_revisao DEFAULT 'pendente',
    
    -- Feedback do professor
    comentarios TEXT,                    -- Comentários gerais sobre a questão
    sugestoes_melhoria TEXT,             -- Sugestões de como melhorar
    correcoes_texto TEXT,                -- Texto corrigido/sugerido
    
    -- Fontes bibliográficas
    fontes_bibliograficas JSONB,
    /*
    Exemplo:
    [
        {
            "tipo": "livro",
            "autor": "Guyton & Hall",
            "titulo": "Tratado de Fisiologia Médica",
            "edicao": "13ª",
            "ano": 2017,
            "paginas": "123-125"
        },
        {
            "tipo": "artigo",
            "autor": "Silva, J.A.",
            "titulo": "Revisão sobre metabolismo",
            "revista": "Nature",
            "doi": "10.1038/xxx"
        }
    ]
    */
    
    -- Avaliação da qualidade
    nota_qualidade INT CHECK (nota_qualidade >= 1 AND nota_qualidade <= 5),
    precisao_cientifica BOOLEAN,         -- A questão está cientificamente correta?
    clareza_enunciado BOOLEAN,           -- O enunciado está claro?
    adequacao_nivel BOOLEAN,             -- O nível está adequado ao público?
    
    -- Versão da questão revisada
    versao INT DEFAULT 1,                -- Para rastrear múltiplas revisões
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aprovada_em TIMESTAMP,
    
    CONSTRAINT uk_revisao_questao_versao UNIQUE (questao_id, versao)
);

CREATE TRIGGER trg_questao_revisoes_updated_at
    BEFORE UPDATE ON provas.questao_revisoes
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.questao_revisoes IS 'Histórico de revisões de questões pelo professor';

-- ============================================================================
-- TABELA: PROVAS_ALUNOS (Provas Individualizadas)
-- ============================================================================
-- Cada registro representa uma versão única da prova para um aluno

CREATE TABLE IF NOT EXISTS provas.provas_alunos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prova_base_id UUID NOT NULL REFERENCES provas.provas(id) ON DELETE CASCADE,
    
    -- Identificação
    numero_aluno INT NOT NULL,           -- Número sequencial (1, 2, 3... N)
    codigo_prova VARCHAR(20),            -- Código único da prova (ex: "A01", "B02")
    
    -- Mapeamento de embaralhamento
    ordem_questoes JSONB NOT NULL,
    /*
    Exemplo - mapeia posição original para nova posição:
    {
        "mapeamento": [3, 1, 5, 2, 4],  // Questão 3 vai para posição 1, etc.
        "questoes": [
            {"original": 1, "nova_posicao": 2, "questao_id": "uuid..."},
            {"original": 2, "nova_posicao": 4, "questao_id": "uuid..."},
            ...
        ]
    }
    */
    
    ordem_alternativas JSONB NOT NULL,
    /*
    Exemplo - embaralhamento das alternativas por questão:
    {
        "questao_1": {
            "mapeamento": ["C", "A", "E", "B", "D"],  // Original A->C, B->A, etc.
            "correta_original": "A",
            "correta_nova": "C"
        },
        "questao_2": {
            "mapeamento": ["B", "D", "A", "E", "C"],
            "correta_original": "C",
            "correta_nova": "A"
        }
    }
    */
    
    -- Gabarito específico desta versão
    gabarito JSONB NOT NULL,
    /*
    Exemplo:
    {
        "1": "C",
        "2": "A",
        "3": "B",
        "4": "E",
        "5": "D"
    }
    */
    
    -- Arquivos gerados
    caminho_pdf VARCHAR(500),
    caminho_gabarito VARCHAR(500),
    
    -- Metadados
    hash_verificacao VARCHAR(64),        -- Hash para verificar integridade
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_prova_aluno UNIQUE (prova_base_id, numero_aluno)
);

COMMENT ON TABLE provas.provas_alunos IS 'Versões individualizadas de provas para cada aluno';

-- ============================================================================
-- TABELA: LOTES_PROVA (Agrupamento de provas geradas)
-- ============================================================================
-- Agrupa as provas geradas em um mesmo lote (mesma solicitação)

CREATE TABLE IF NOT EXISTS provas.lotes_prova (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prova_base_id UUID NOT NULL REFERENCES provas.provas(id) ON DELETE CASCADE,
    professor_id UUID REFERENCES provas.usuarios(id),
    
    -- Configurações do lote
    quantidade_alunos INT NOT NULL,
    embaralhar_questoes BOOLEAN DEFAULT TRUE,
    embaralhar_alternativas BOOLEAN DEFAULT TRUE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'gerando',  -- gerando, concluido, erro
    erro_mensagem TEXT,
    
    -- Arquivos
    caminho_zip VARCHAR(500),              -- ZIP com todas as provas
    
    -- Estatísticas
    provas_geradas INT DEFAULT 0,
    tempo_geracao_seg INT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    concluido_em TIMESTAMP
);

COMMENT ON TABLE provas.lotes_prova IS 'Lotes de provas geradas para turmas';

-- ============================================================================
-- ALTERAÇÕES NA TABELA DE QUESTÕES
-- ============================================================================

-- Adicionar campos para o fluxo de revisão
ALTER TABLE provas.questoes 
ADD COLUMN IF NOT EXISTS professor_id UUID REFERENCES provas.usuarios(id),
ADD COLUMN IF NOT EXISTS aprovada_em TIMESTAMP,
ADD COLUMN IF NOT EXISTS fontes_bibliograficas JSONB,
ADD COLUMN IF NOT EXISTS versao_atual INT DEFAULT 1,
ADD COLUMN IF NOT EXISTS observacoes_professor TEXT;

COMMENT ON COLUMN provas.questoes.professor_id IS 'Professor que criou/solicitou a questão';
COMMENT ON COLUMN provas.questoes.aprovada_em IS 'Data/hora da aprovação final';
COMMENT ON COLUMN provas.questoes.fontes_bibliograficas IS 'Referências bibliográficas validadas';
COMMENT ON COLUMN provas.questoes.versao_atual IS 'Versão atual da questão após revisões';
COMMENT ON COLUMN provas.questoes.observacoes_professor IS 'Observações do professor durante criação';

-- ============================================================================
-- ALTERAÇÕES NA TABELA DE PROVAS
-- ============================================================================

-- Adicionar campos para controle de provas individualizadas
ALTER TABLE provas.provas
ADD COLUMN IF NOT EXISTS permite_individualizacao BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS quantidade_versoes_geradas INT DEFAULT 0;

-- ============================================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- Índices para questao_revisoes
CREATE INDEX IF NOT EXISTS idx_revisoes_questao ON provas.questao_revisoes(questao_id);
CREATE INDEX IF NOT EXISTS idx_revisoes_professor ON provas.questao_revisoes(professor_id);
CREATE INDEX IF NOT EXISTS idx_revisoes_status ON provas.questao_revisoes(status);
CREATE INDEX IF NOT EXISTS idx_revisoes_created ON provas.questao_revisoes(created_at DESC);

-- Índices para provas_alunos
CREATE INDEX IF NOT EXISTS idx_provas_alunos_base ON provas.provas_alunos(prova_base_id);
CREATE INDEX IF NOT EXISTS idx_provas_alunos_codigo ON provas.provas_alunos(codigo_prova);

-- Índices para lotes_prova
CREATE INDEX IF NOT EXISTS idx_lotes_prova_base ON provas.lotes_prova(prova_base_id);
CREATE INDEX IF NOT EXISTS idx_lotes_status ON provas.lotes_prova(status);

-- Índice para questões por professor
CREATE INDEX IF NOT EXISTS idx_questoes_professor ON provas.questoes(professor_id);
CREATE INDEX IF NOT EXISTS idx_questoes_status_aprovacao ON provas.questoes(status, aprovada_em);

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Questões pendentes de revisão
CREATE OR REPLACE VIEW provas.vw_questoes_pendentes_revisao AS
SELECT 
    q.id,
    q.enunciado,
    q.tipo,
    q.dificuldade,
    q.status,
    q.created_at,
    m.nome AS materia,
    t.nome AS topico,
    u.nome AS professor_nome,
    COALESCE(r.versao, 0) AS versao_revisao,
    r.status AS status_revisao
FROM provas.questoes q
LEFT JOIN provas.materias m ON q.materia_id = m.id
LEFT JOIN provas.topicos t ON q.topico_id = t.id
LEFT JOIN provas.usuarios u ON q.professor_id = u.id
LEFT JOIN LATERAL (
    SELECT * FROM provas.questao_revisoes 
    WHERE questao_id = q.id 
    ORDER BY versao DESC 
    LIMIT 1
) r ON true
WHERE q.status IN ('rascunho', 'revisao')
  AND q.deleted_at IS NULL
ORDER BY q.created_at DESC;

COMMENT ON VIEW provas.vw_questoes_pendentes_revisao IS 'Questões aguardando revisão do professor';

-- View: Questões aprovadas por professor
CREATE OR REPLACE VIEW provas.vw_questoes_aprovadas AS
SELECT 
    q.id,
    q.codigo,
    q.enunciado,
    q.tipo,
    q.dificuldade,
    q.status,
    q.aprovada_em,
    q.vezes_usada,
    m.nome AS materia,
    m.codigo AS materia_codigo,
    t.nome AS topico,
    u.id AS professor_id,
    u.nome AS professor_nome
FROM provas.questoes q
LEFT JOIN provas.materias m ON q.materia_id = m.id
LEFT JOIN provas.topicos t ON q.topico_id = t.id
LEFT JOIN provas.usuarios u ON q.professor_id = u.id
WHERE q.status = 'aprovada'
  AND q.deleted_at IS NULL
ORDER BY q.aprovada_em DESC;

COMMENT ON VIEW provas.vw_questoes_aprovadas IS 'Questões aprovadas disponíveis para uso em provas';

-- View: Resumo de provas individualizadas
CREATE OR REPLACE VIEW provas.vw_lotes_resumo AS
SELECT 
    l.id AS lote_id,
    l.prova_base_id,
    p.titulo AS prova_titulo,
    l.quantidade_alunos,
    l.provas_geradas,
    l.status,
    l.embaralhar_questoes,
    l.embaralhar_alternativas,
    l.caminho_zip,
    l.created_at,
    l.concluido_em,
    u.nome AS professor_nome
FROM provas.lotes_prova l
JOIN provas.provas p ON l.prova_base_id = p.id
LEFT JOIN provas.usuarios u ON l.professor_id = u.id
ORDER BY l.created_at DESC;

COMMENT ON VIEW provas.vw_lotes_resumo IS 'Resumo dos lotes de provas geradas';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('009_fluxo_revisao_provas.sql', md5('009_fluxo_revisao_provas'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 009
-- ============================================================================

