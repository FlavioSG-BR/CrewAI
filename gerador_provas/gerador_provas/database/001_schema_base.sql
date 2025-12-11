-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 001: SCHEMA BASE
-- ============================================================================
-- Descrição: Cria extensões, schemas e configurações base
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Schema principal
CREATE SCHEMA IF NOT EXISTS provas;
CREATE SCHEMA IF NOT EXISTS auditoria;

-- Comentário no schema
COMMENT ON SCHEMA provas IS 'Schema principal do Gerador de Provas';
COMMENT ON SCHEMA auditoria IS 'Schema para logs e auditoria';

-- Definir search_path padrão
SET search_path TO provas, public;

-- ============================================================================
-- TIPOS ENUMERADOS
-- ============================================================================

-- Níveis de dificuldade
CREATE TYPE provas.nivel_dificuldade AS ENUM ('facil', 'medio', 'dificil', 'muito_dificil');

-- Tipos de questão
CREATE TYPE provas.tipo_questao AS ENUM (
    'multipla_escolha',
    'verdadeiro_falso',
    'dissertativa',
    'numerica',
    'associacao',
    'ordenacao'
);

-- Status de questão
CREATE TYPE provas.status_questao AS ENUM ('rascunho', 'revisao', 'aprovada', 'arquivada');

-- Status de prova
CREATE TYPE provas.status_prova AS ENUM ('rascunho', 'publicada', 'encerrada', 'arquivada');

-- Perfis de usuário
CREATE TYPE provas.perfil_usuario AS ENUM ('admin', 'professor', 'aluno', 'visitante');

-- ============================================================================
-- FUNÇÃO PARA ATUALIZAR TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION provas.atualizar_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABELA DE CONTROLE DE MIGRAÇÕES
-- ============================================================================

CREATE TABLE IF NOT EXISTS provas.migrations (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    executada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64)
);

-- Registrar esta migração
INSERT INTO provas.migrations (nome, checksum) 
VALUES ('001_schema_base.sql', md5('001_schema_base'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 001
-- ============================================================================

