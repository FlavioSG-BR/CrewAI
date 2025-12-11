-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 006: TABELAS DE AUDITORIA
-- ============================================================================
-- Descrição: Tabelas para logs, auditoria e rastreabilidade
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO auditoria, provas, public;

-- ============================================================================
-- TABELA: LOGS_SISTEMA
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.logs_sistema (
    id BIGSERIAL PRIMARY KEY,
    
    -- Identificação
    nivel VARCHAR(10) NOT NULL,       -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    modulo VARCHAR(100),              -- Ex: questoes, provas, usuarios
    funcao VARCHAR(100),
    
    -- Mensagem
    mensagem TEXT NOT NULL,
    detalhes JSONB,
    
    -- Contexto
    usuario_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(36),           -- UUID da requisição
    
    -- Rastreamento
    stack_trace TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca por data (particionamento futuro)
CREATE INDEX idx_logs_created_at ON auditoria.logs_sistema (created_at DESC);
CREATE INDEX idx_logs_nivel ON auditoria.logs_sistema (nivel);
CREATE INDEX idx_logs_modulo ON auditoria.logs_sistema (modulo);

COMMENT ON TABLE auditoria.logs_sistema IS 'Logs gerais do sistema';

-- ============================================================================
-- TABELA: HISTORICO_ALTERACOES
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.historico_alteracoes (
    id BIGSERIAL PRIMARY KEY,
    
    -- Referência
    tabela VARCHAR(100) NOT NULL,
    registro_id UUID NOT NULL,
    
    -- Operação
    operacao VARCHAR(10) NOT NULL,    -- INSERT, UPDATE, DELETE
    
    -- Dados
    dados_antigos JSONB,
    dados_novos JSONB,
    campos_alterados TEXT[],
    
    -- Contexto
    usuario_id UUID,
    motivo TEXT,
    ip_address INET,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historico_tabela ON auditoria.historico_alteracoes (tabela, registro_id);
CREATE INDEX idx_historico_data ON auditoria.historico_alteracoes (created_at DESC);

COMMENT ON TABLE auditoria.historico_alteracoes IS 'Histórico de alterações em registros';

-- ============================================================================
-- TABELA: SESSOES
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.sessoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL,
    
    -- Sessão
    token_hash VARCHAR(255) NOT NULL,
    
    -- Dispositivo
    ip_address INET,
    user_agent TEXT,
    dispositivo VARCHAR(100),         -- Desktop, Mobile, Tablet
    navegador VARCHAR(100),
    sistema_operacional VARCHAR(100),
    
    -- Status
    ativa BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_em TIMESTAMP,
    encerrada_em TIMESTAMP
);

CREATE INDEX idx_sessoes_usuario ON auditoria.sessoes (usuario_id);
CREATE INDEX idx_sessoes_token ON auditoria.sessoes (token_hash);

COMMENT ON TABLE auditoria.sessoes IS 'Sessões de usuários';

-- ============================================================================
-- TABELA: ACOES_USUARIO
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.acoes_usuario (
    id BIGSERIAL PRIMARY KEY,
    
    usuario_id UUID,
    sessao_id UUID REFERENCES auditoria.sessoes(id),
    
    -- Ação
    acao VARCHAR(100) NOT NULL,       -- login, logout, criar_questao, etc
    recurso VARCHAR(100),             -- questao, prova, usuario
    recurso_id UUID,
    
    -- Detalhes
    parametros JSONB,
    resultado VARCHAR(20),            -- sucesso, falha, parcial
    mensagem TEXT,
    
    -- Contexto
    ip_address INET,
    url VARCHAR(500),
    metodo_http VARCHAR(10),
    
    -- Performance
    tempo_resposta_ms INT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_acoes_usuario ON auditoria.acoes_usuario (usuario_id);
CREATE INDEX idx_acoes_data ON auditoria.acoes_usuario (created_at DESC);
CREATE INDEX idx_acoes_acao ON auditoria.acoes_usuario (acao);

COMMENT ON TABLE auditoria.acoes_usuario IS 'Registro de ações dos usuários';

-- ============================================================================
-- TABELA: METRICAS_SISTEMA
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.metricas_sistema (
    id BIGSERIAL PRIMARY KEY,
    
    -- Identificação
    metrica VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    
    -- Valores
    valor DECIMAL(15,4),
    unidade VARCHAR(20),
    
    -- Período
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    periodo_inicio TIMESTAMP,
    periodo_fim TIMESTAMP,
    
    -- Metadados
    tags JSONB
);

CREATE INDEX idx_metricas_metrica ON auditoria.metricas_sistema (metrica, data_hora DESC);

COMMENT ON TABLE auditoria.metricas_sistema IS 'Métricas de performance e uso do sistema';

-- ============================================================================
-- FUNÇÃO: REGISTRAR_ALTERACAO (Trigger genérico)
-- ============================================================================

CREATE OR REPLACE FUNCTION auditoria.registrar_alteracao()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria.historico_alteracoes (tabela, registro_id, operacao, dados_novos)
        VALUES (TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME, NEW.id, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria.historico_alteracoes (tabela, registro_id, operacao, dados_antigos, dados_novos)
        VALUES (TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME, NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria.historico_alteracoes (tabela, registro_id, operacao, dados_antigos)
        VALUES (TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME, OLD.id, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auditoria.registrar_alteracao IS 'Função de trigger para auditoria automática';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('006_tabelas_auditoria.sql', md5('006_tabelas_auditoria'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 006
-- ============================================================================

