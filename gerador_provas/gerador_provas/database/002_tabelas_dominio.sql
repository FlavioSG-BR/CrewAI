-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 002: TABELAS DE DOMÍNIO
-- ============================================================================
-- Descrição: Tabelas de configuração e domínio do sistema
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- TABELA: MATERIAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.materias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    icone VARCHAR(50),               -- Emoji ou classe de ícone
    cor_primaria VARCHAR(7),         -- Código hex (#FFFFFF)
    cor_secundaria VARCHAR(7),
    ordem INT DEFAULT 0,             -- Para ordenação no frontend
    ativo BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP             -- Soft delete
);

-- Trigger para updated_at
CREATE TRIGGER trg_materias_updated_at
    BEFORE UPDATE ON provas.materias
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.materias IS 'Matérias disponíveis no sistema';

-- ============================================================================
-- TABELA: TOPICOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.topicos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    materia_id UUID NOT NULL REFERENCES provas.materias(id) ON DELETE CASCADE,
    codigo VARCHAR(50) NOT NULL,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    icone VARCHAR(50),
    nivel INT DEFAULT 1,             -- Nível hierárquico (1=principal, 2=subtópico)
    topico_pai_id UUID REFERENCES provas.topicos(id), -- Para subtópicos
    ordem INT DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Constraint única
    CONSTRAINT uk_topico_materia UNIQUE (materia_id, codigo)
);

CREATE TRIGGER trg_topicos_updated_at
    BEFORE UPDATE ON provas.topicos
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.topicos IS 'Tópicos por matéria';

-- ============================================================================
-- TABELA: TAGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(50) NOT NULL UNIQUE,
    cor VARCHAR(7) DEFAULT '#6c757d',
    descricao TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE provas.tags IS 'Tags para categorização livre';

-- ============================================================================
-- TABELA: CONFIGURACOES
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.configuracoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT,
    tipo VARCHAR(20) DEFAULT 'string', -- string, int, bool, json
    categoria VARCHAR(50),
    descricao TEXT,
    editavel BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_configuracoes_updated_at
    BEFORE UPDATE ON provas.configuracoes
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.configuracoes IS 'Configurações do sistema';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('002_tabelas_dominio.sql', md5('002_tabelas_dominio'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 002
-- ============================================================================

