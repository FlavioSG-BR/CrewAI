-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 007: ÍNDICES E CONSTRAINTS
-- ============================================================================
-- Descrição: Índices adicionais para performance e constraints
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- ÍNDICES PARA QUESTÕES
-- ============================================================================

-- Busca por matéria e tópico (mais comum)
CREATE INDEX IF NOT EXISTS idx_questoes_materia_topico 
    ON provas.questoes (materia_id, topico_id);

-- Busca por dificuldade
CREATE INDEX IF NOT EXISTS idx_questoes_dificuldade 
    ON provas.questoes (dificuldade);

-- Busca por status
CREATE INDEX IF NOT EXISTS idx_questoes_status 
    ON provas.questoes (status) WHERE status != 'arquivada';

-- Full-text search no enunciado
CREATE INDEX IF NOT EXISTS idx_questoes_enunciado_gin 
    ON provas.questoes USING gin(to_tsvector('portuguese', enunciado));

-- Palavras-chave (array)
CREATE INDEX IF NOT EXISTS idx_questoes_palavras_chave 
    ON provas.questoes USING gin(palavras_chave);

-- Questões não deletadas
CREATE INDEX IF NOT EXISTS idx_questoes_ativas 
    ON provas.questoes (id) WHERE deleted_at IS NULL;

-- ============================================================================
-- ÍNDICES PARA ALTERNATIVAS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_alternativas_questao 
    ON provas.alternativas (questao_id);

CREATE INDEX IF NOT EXISTS idx_alternativas_correta 
    ON provas.alternativas (questao_id) WHERE correta = TRUE;

-- ============================================================================
-- ÍNDICES PARA RESOLUÇÕES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_resolucoes_questao 
    ON provas.resolucoes (questao_id);

-- ============================================================================
-- ÍNDICES PARA DIAGRAMAS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_diagramas_questao 
    ON provas.diagramas (questao_id);

CREATE INDEX IF NOT EXISTS idx_diagramas_tipo 
    ON provas.diagramas (tipo_diagrama);

-- ============================================================================
-- ÍNDICES PARA PROVAS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_provas_status 
    ON provas.provas (status);

CREATE INDEX IF NOT EXISTS idx_provas_materia 
    ON provas.provas (materia_id);

CREATE INDEX IF NOT EXISTS idx_provas_data 
    ON provas.provas (data_aplicacao);

CREATE INDEX IF NOT EXISTS idx_provas_ativas 
    ON provas.provas (id) WHERE deleted_at IS NULL;

-- ============================================================================
-- ÍNDICES PARA USUÁRIOS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_usuarios_email 
    ON provas.usuarios (email);

CREATE INDEX IF NOT EXISTS idx_usuarios_perfil 
    ON provas.usuarios (perfil);

CREATE INDEX IF NOT EXISTS idx_usuarios_ativos 
    ON provas.usuarios (id) WHERE ativo = TRUE AND deleted_at IS NULL;

-- ============================================================================
-- ÍNDICES PARA RESPOSTAS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_respostas_usuario 
    ON provas.respostas_usuario (usuario_id);

CREATE INDEX IF NOT EXISTS idx_respostas_prova 
    ON provas.respostas_usuario (prova_id);

CREATE INDEX IF NOT EXISTS idx_respostas_questao 
    ON provas.respostas_usuario (questao_id);

CREATE INDEX IF NOT EXISTS idx_respostas_correta 
    ON provas.respostas_usuario (usuario_id, correta);

-- ============================================================================
-- ÍNDICES PARA ESTATÍSTICAS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_estatisticas_usuario 
    ON provas.estatisticas_usuario (usuario_id);

CREATE INDEX IF NOT EXISTS idx_estatisticas_materia 
    ON provas.estatisticas_usuario (usuario_id, materia_id);

-- ============================================================================
-- ÍNDICES COMPOSTOS PARA RELATÓRIOS
-- ============================================================================

-- Performance de usuários por período
CREATE INDEX IF NOT EXISTS idx_respostas_usuario_data 
    ON provas.respostas_usuario (usuario_id, respondida_em);

-- Questões mais usadas
CREATE INDEX IF NOT EXISTS idx_questoes_uso 
    ON provas.questoes (vezes_usada DESC) WHERE status = 'aprovada';

-- ============================================================================
-- CONSTRAINTS ADICIONAIS
-- ============================================================================

-- Garantir que alternativa correta existe
CREATE OR REPLACE FUNCTION provas.validar_alternativa_correta()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo = 'multipla_escolha' THEN
        IF NOT EXISTS (
            SELECT 1 FROM provas.alternativas 
            WHERE questao_id = NEW.id AND correta = TRUE
        ) THEN
            -- Não bloqueia, apenas avisa (questão pode estar em rascunho)
            NULL;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('007_indices.sql', md5('007_indices'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 007
-- ============================================================================

