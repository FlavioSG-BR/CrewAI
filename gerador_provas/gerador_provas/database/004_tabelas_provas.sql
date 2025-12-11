-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 004: TABELAS DE PROVAS
-- ============================================================================
-- Descrição: Tabelas para criação e gerenciamento de provas
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- TABELA: PROVAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.provas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificação
    codigo VARCHAR(30) UNIQUE,        -- Código da prova (ex: PROVA-2024-001)
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    
    -- Classificação
    materia_id UUID REFERENCES provas.materias(id),
    nivel_escolar VARCHAR(50),        -- Fundamental, Médio, Superior
    serie VARCHAR(20),                -- 1º ano, 2º ano, etc
    
    -- Configurações
    status provas.status_prova DEFAULT 'rascunho',
    tempo_limite_min INT,             -- Tempo limite em minutos
    pontuacao_total DECIMAL(5,2),
    nota_minima DECIMAL(5,2),
    
    -- Instruções
    instrucoes TEXT,
    observacoes TEXT,
    
    -- Datas
    data_aplicacao DATE,
    hora_inicio TIME,
    hora_fim TIME,
    
    -- Configurações de exibição
    embaralhar_questoes BOOLEAN DEFAULT FALSE,
    embaralhar_alternativas BOOLEAN DEFAULT FALSE,
    mostrar_gabarito BOOLEAN DEFAULT FALSE,
    permitir_revisao BOOLEAN DEFAULT TRUE,
    
    -- Auditoria
    criado_por UUID,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TRIGGER trg_provas_updated_at
    BEFORE UPDATE ON provas.provas
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.provas IS 'Provas criadas no sistema';

-- ============================================================================
-- TABELA: PROVA_QUESTOES (Relacionamento N:N)
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.prova_questoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prova_id UUID NOT NULL REFERENCES provas.provas(id) ON DELETE CASCADE,
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE RESTRICT,
    
    -- Ordenação e pontuação
    numero INT NOT NULL,              -- Número da questão na prova
    pontuacao DECIMAL(5,2),           -- Pontuação específica nesta prova
    
    -- Configurações específicas
    obrigatoria BOOLEAN DEFAULT TRUE,
    peso DECIMAL(3,2) DEFAULT 1.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_prova_questao UNIQUE (prova_id, questao_id),
    CONSTRAINT uk_prova_numero UNIQUE (prova_id, numero)
);

COMMENT ON TABLE provas.prova_questoes IS 'Questões incluídas em cada prova';

-- ============================================================================
-- TABELA: GABARITOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.gabaritos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prova_id UUID NOT NULL REFERENCES provas.provas(id) ON DELETE CASCADE,
    
    -- Tipo de gabarito
    tipo VARCHAR(20) DEFAULT 'oficial', -- oficial, alternativo
    versao INT DEFAULT 1,
    
    -- Respostas em JSON
    respostas JSONB NOT NULL,
    /*
    Exemplo:
    {
        "1": {"resposta": "A", "pontuacao": 1.0},
        "2": {"resposta": "42", "pontuacao": 2.0, "tolerancia": 0.1},
        "3": {"resposta": "dissertativa", "palavras_chave": ["energia", "trabalho"]}
    }
    */
    
    -- Metadados
    observacoes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_gabarito_prova_versao UNIQUE (prova_id, tipo, versao)
);

CREATE TRIGGER trg_gabaritos_updated_at
    BEFORE UPDATE ON provas.gabaritos
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.gabaritos IS 'Gabaritos das provas';

-- ============================================================================
-- TABELA: MODELOS_PROVA (Templates)
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.modelos_prova (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    
    -- Configurações do modelo
    configuracoes JSONB,
    /*
    {
        "cabecalho": true,
        "logo": "path/to/logo.png",
        "rodape": "© 2024 Escola XYZ",
        "questoes_por_pagina": 5,
        "mostrar_pontuacao": true
    }
    */
    
    -- CSS customizado
    estilo_css TEXT,
    
    ativo BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_modelos_prova_updated_at
    BEFORE UPDATE ON provas.modelos_prova
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.modelos_prova IS 'Modelos/templates de provas';

-- ============================================================================
-- TABELA: PROVA_EXPORTACOES
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.prova_exportacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prova_id UUID NOT NULL REFERENCES provas.provas(id) ON DELETE CASCADE,
    
    formato VARCHAR(10) NOT NULL,     -- pdf, latex, docx, html
    caminho_arquivo VARCHAR(500),
    tamanho_bytes BIGINT,
    
    -- Opções de exportação
    opcoes JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pendente', -- pendente, processando, concluido, erro
    erro_mensagem TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    concluido_em TIMESTAMP
);

COMMENT ON TABLE provas.prova_exportacoes IS 'Histórico de exportações de provas';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('004_tabelas_provas.sql', md5('004_tabelas_provas'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 004
-- ============================================================================

