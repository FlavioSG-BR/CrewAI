-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 003: TABELAS DE QUESTÕES
-- ============================================================================
-- Descrição: Tabelas principais de questões, resoluções e diagramas
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- TABELA: QUESTOES
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.questoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Classificação
    materia_id UUID NOT NULL REFERENCES provas.materias(id),
    topico_id UUID REFERENCES provas.topicos(id),
    tipo provas.tipo_questao DEFAULT 'dissertativa',
    dificuldade provas.nivel_dificuldade DEFAULT 'medio',
    status provas.status_questao DEFAULT 'rascunho',
    
    -- Conteúdo
    codigo VARCHAR(20) UNIQUE,       -- Código único da questão (ex: FIS-001)
    enunciado TEXT NOT NULL,
    enunciado_complementar TEXT,     -- Textos, tabelas, contexto adicional
    pontuacao DECIMAL(5,2) DEFAULT 1.0,
    tempo_estimado_min INT,          -- Tempo estimado em minutos
    
    -- Metadados
    fonte VARCHAR(255),              -- Ex: "ENEM 2023", "Própria"
    ano_referencia INT,
    palavras_chave TEXT[],           -- Array de palavras-chave
    
    -- Estatísticas
    vezes_usada INT DEFAULT 0,
    taxa_acerto DECIMAL(5,2),        -- Porcentagem de acertos
    
    -- Auditoria
    criado_por UUID,                 -- Referência para usuários
    revisado_por UUID,
    aprovado_por UUID,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TRIGGER trg_questoes_updated_at
    BEFORE UPDATE ON provas.questoes
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.questoes IS 'Questões geradas pelo sistema';

-- ============================================================================
-- TABELA: ALTERNATIVAS (para múltipla escolha)
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.alternativas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    
    letra CHAR(1) NOT NULL,          -- A, B, C, D, E
    texto TEXT NOT NULL,
    correta BOOLEAN DEFAULT FALSE,
    justificativa TEXT,              -- Por que está certa/errada
    ordem INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_alternativa_questao_letra UNIQUE (questao_id, letra)
);

COMMENT ON TABLE provas.alternativas IS 'Alternativas para questões de múltipla escolha';

-- ============================================================================
-- TABELA: RESOLUCOES
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.resolucoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    
    -- Resposta
    resposta_curta TEXT,             -- Resposta direta (ex: "x = 5")
    resposta_completa TEXT,          -- Resolução detalhada
    
    -- Passo a passo
    passos JSONB,                    -- Array de passos em JSON
    /*
    Exemplo de passos:
    [
        {"numero": 1, "descricao": "Identificar dados", "formula": null, "resultado": null},
        {"numero": 2, "descricao": "Aplicar fórmula", "formula": "v = d/t", "resultado": "10 m/s"}
    ]
    */
    
    -- Fórmulas utilizadas
    formulas TEXT[],                 -- Array de fórmulas
    
    -- Observações
    dicas TEXT,
    erros_comuns TEXT,               -- Erros frequentes dos alunos
    
    -- Metadados
    metodo_resolucao VARCHAR(100),   -- Ex: "Bhaskara", "Regra de 3"
    nivel_detalhamento VARCHAR(20) DEFAULT 'completo', -- resumido, normal, completo
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_resolucoes_updated_at
    BEFORE UPDATE ON provas.resolucoes
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.resolucoes IS 'Resoluções detalhadas das questões';

-- ============================================================================
-- TABELA: DIAGRAMAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.diagramas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questao_id UUID REFERENCES provas.questoes(id) ON DELETE CASCADE,
    resolucao_id UUID REFERENCES provas.resolucoes(id) ON DELETE CASCADE,
    
    -- Arquivo
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho VARCHAR(500) NOT NULL,
    tipo_arquivo VARCHAR(20) DEFAULT 'png', -- png, svg, jpg
    tamanho_bytes BIGINT,
    
    -- Metadados
    tipo_diagrama VARCHAR(50),       -- mru, circuito, geometria, atomo, etc
    titulo VARCHAR(200),
    descricao TEXT,
    alt_text VARCHAR(255),           -- Texto alternativo para acessibilidade
    
    -- Parâmetros de geração (para regenerar se necessário)
    parametros_geracao JSONB,
    
    -- Posição na questão
    posicao VARCHAR(20) DEFAULT 'apos_enunciado', -- antes, apos_enunciado, na_resolucao
    ordem INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Pelo menos uma referência deve existir
    CONSTRAINT chk_diagrama_referencia CHECK (questao_id IS NOT NULL OR resolucao_id IS NOT NULL)
);

COMMENT ON TABLE provas.diagramas IS 'Diagramas e imagens das questões';

-- ============================================================================
-- TABELA: QUESTAO_TAGS (Relacionamento N:N)
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.questao_tags (
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES provas.tags(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (questao_id, tag_id)
);

COMMENT ON TABLE provas.questao_tags IS 'Relacionamento entre questões e tags';

-- ============================================================================
-- TABELA: QUESTOES_RELACIONADAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.questoes_relacionadas (
    questao_origem_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    questao_destino_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    
    tipo_relacao VARCHAR(50) DEFAULT 'similar', -- similar, pre_requisito, complementar
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (questao_origem_id, questao_destino_id),
    CONSTRAINT chk_diferentes CHECK (questao_origem_id != questao_destino_id)
);

COMMENT ON TABLE provas.questoes_relacionadas IS 'Relacionamento entre questões similares';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('003_tabelas_questoes.sql', md5('003_tabelas_questoes'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 003
-- ============================================================================

