-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 005: TABELAS DE USUÁRIOS
-- ============================================================================
-- Descrição: Tabelas para gerenciamento de usuários e suas interações
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- TABELA: USUARIOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificação
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    nome_usuario VARCHAR(50) UNIQUE,
    
    -- Autenticação
    senha_hash VARCHAR(255),          -- Senha criptografada
    salt VARCHAR(64),
    
    -- Perfil
    perfil provas.perfil_usuario DEFAULT 'aluno',
    avatar_url VARCHAR(500),
    bio TEXT,
    
    -- Contato
    telefone VARCHAR(20),
    
    -- Status
    ativo BOOLEAN DEFAULT TRUE,
    email_verificado BOOLEAN DEFAULT FALSE,
    ultimo_acesso TIMESTAMP,
    
    -- Preferências
    preferencias JSONB DEFAULT '{}',
    /*
    {
        "tema": "dark",
        "idioma": "pt-BR",
        "notificacoes_email": true,
        "materias_favoritas": ["fisica", "matematica"]
    }
    */
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TRIGGER trg_usuarios_updated_at
    BEFORE UPDATE ON provas.usuarios
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.usuarios IS 'Usuários do sistema';

-- ============================================================================
-- TABELA: TOKENS_RECUPERACAO
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.tokens_recuperacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES provas.usuarios(id) ON DELETE CASCADE,
    
    token VARCHAR(255) NOT NULL UNIQUE,
    tipo VARCHAR(30) DEFAULT 'senha',  -- senha, email_verificacao
    
    expira_em TIMESTAMP NOT NULL,
    usado_em TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE provas.tokens_recuperacao IS 'Tokens de recuperação de senha';

-- ============================================================================
-- TABELA: RESPOSTAS_USUARIO
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.respostas_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES provas.usuarios(id) ON DELETE CASCADE,
    prova_id UUID REFERENCES provas.provas(id) ON DELETE SET NULL,
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    
    -- Resposta
    resposta TEXT,                    -- Resposta dada
    alternativa_id UUID REFERENCES provas.alternativas(id),  -- Para múltipla escolha
    
    -- Avaliação
    correta BOOLEAN,
    pontuacao_obtida DECIMAL(5,2),
    feedback TEXT,                    -- Feedback do professor
    
    -- Metadados
    tempo_gasto_seg INT,              -- Tempo gasto em segundos
    tentativa INT DEFAULT 1,          -- Número da tentativa
    
    -- Timestamps
    respondida_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    corrigida_em TIMESTAMP,
    corrigida_por UUID REFERENCES provas.usuarios(id)
);

COMMENT ON TABLE provas.respostas_usuario IS 'Respostas dos usuários às questões';

-- ============================================================================
-- TABELA: ESTATISTICAS_USUARIO
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.estatisticas_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES provas.usuarios(id) ON DELETE CASCADE,
    materia_id UUID REFERENCES provas.materias(id),
    topico_id UUID REFERENCES provas.topicos(id),
    
    -- Estatísticas
    total_questoes INT DEFAULT 0,
    questoes_corretas INT DEFAULT 0,
    questoes_erradas INT DEFAULT 0,
    taxa_acerto DECIMAL(5,2),
    
    -- Tempo
    tempo_total_min INT DEFAULT 0,
    tempo_medio_por_questao_seg INT,
    
    -- Evolução
    melhor_sequencia INT DEFAULT 0,   -- Maior sequência de acertos
    sequencia_atual INT DEFAULT 0,
    
    -- Período
    periodo VARCHAR(20) DEFAULT 'total', -- dia, semana, mes, total
    data_referencia DATE,
    
    -- Timestamps
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_estatistica_usuario UNIQUE (usuario_id, materia_id, topico_id, periodo, data_referencia)
);

COMMENT ON TABLE provas.estatisticas_usuario IS 'Estatísticas de desempenho por usuário';

-- ============================================================================
-- TABELA: CONQUISTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.conquistas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    icone VARCHAR(100),
    
    -- Requisitos
    tipo VARCHAR(50),                 -- questoes, provas, sequencia, tempo
    requisito_valor INT,              -- Ex: 100 questões
    
    -- Pontos de gamificação
    pontos INT DEFAULT 0,
    
    ativo BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE provas.conquistas IS 'Conquistas/achievements do sistema';

-- ============================================================================
-- TABELA: USUARIO_CONQUISTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.usuario_conquistas (
    usuario_id UUID NOT NULL REFERENCES provas.usuarios(id) ON DELETE CASCADE,
    conquista_id UUID NOT NULL REFERENCES provas.conquistas(id) ON DELETE CASCADE,
    
    desbloqueada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notificado BOOLEAN DEFAULT FALSE,
    
    PRIMARY KEY (usuario_id, conquista_id)
);

COMMENT ON TABLE provas.usuario_conquistas IS 'Conquistas desbloqueadas por usuário';

-- ============================================================================
-- TABELA: FAVORITOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.favoritos (
    usuario_id UUID NOT NULL REFERENCES provas.usuarios(id) ON DELETE CASCADE,
    questao_id UUID NOT NULL REFERENCES provas.questoes(id) ON DELETE CASCADE,
    
    notas TEXT,                       -- Anotações pessoais
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (usuario_id, questao_id)
);

COMMENT ON TABLE provas.favoritos IS 'Questões favoritas do usuário';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('005_tabelas_usuarios.sql', md5('005_tabelas_usuarios'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 005
-- ============================================================================

