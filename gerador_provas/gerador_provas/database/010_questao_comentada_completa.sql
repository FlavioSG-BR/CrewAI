-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 010: QUESTÃO COMENTADA COMPLETA
-- ============================================================================
-- Descrição: Estrutura para questões com explicações detalhadas de cada
--            alternativa, geradas pela IA e revisadas pelo professor.
--            A questão já nasce completa para facilitar a revisão.
-- Autor: Sistema
-- Data: 2024-12-14
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- ALTERAÇÕES NA TABELA DE QUESTÕES
-- ============================================================================

-- Adicionar campo para armazenar explicações detalhadas de cada alternativa
ALTER TABLE provas.questoes 
ADD COLUMN IF NOT EXISTS alternativas_comentadas JSONB,
ADD COLUMN IF NOT EXISTS explicacao_geral TEXT,
ADD COLUMN IF NOT EXISTS resolucao_passo_a_passo TEXT,
ADD COLUMN IF NOT EXISTS erros_comuns JSONB,
ADD COLUMN IF NOT EXISTS dicas_correcao JSONB,
ADD COLUMN IF NOT EXISTS criterios_correcao JSONB,
ADD COLUMN IF NOT EXISTS pontos_chave JSONB,
ADD COLUMN IF NOT EXISTS nivel_cognitivo VARCHAR(50),
ADD COLUMN IF NOT EXISTS tempo_estimado_min INT,
ADD COLUMN IF NOT EXISTS palavras_chave JSONB;

/*
Estrutura do campo alternativas_comentadas (JSONB):
{
    "alternativas": [
        {
            "letra": "A",
            "texto": "Texto da alternativa A",
            "correta": false,
            "explicacao": "Por que esta alternativa está ERRADA: explicação detalhada...",
            "erro_conceitual": "Tipo de erro que o aluno comete ao marcar esta",
            "dica_professor": "O que observar quando aluno marca esta opção"
        },
        {
            "letra": "B",
            "texto": "Texto da alternativa B",
            "correta": true,
            "explicacao": "Por que esta alternativa está CORRETA: explicação detalhada...",
            "conceitos_envolvidos": ["conceito1", "conceito2"],
            "dica_professor": "Pontos importantes desta resposta"
        },
        {
            "letra": "C",
            "texto": "Texto da alternativa C",
            "correta": false,
            "explicacao": "Por que esta alternativa está ERRADA...",
            "erro_conceitual": "Confusão comum entre X e Y",
            "dica_professor": "Aluno pode ter confundido com..."
        },
        ...
    ],
    "distratores_eficazes": ["A", "D"],
    "alternativa_mais_confusa": "C",
    "justificativa_ordem": "Alternativas ordenadas por plausibilidade"
}

Estrutura do campo erros_comuns (JSONB):
[
    {
        "erro": "Confundir força com energia",
        "frequencia": "alta",
        "como_identificar": "Aluno marca alternativa com Joule",
        "como_corrigir": "Revisar conceito de grandezas físicas"
    },
    {
        "erro": "Esquecer unidade de medida",
        "frequencia": "media",
        "como_identificar": "Resposta sem unidade",
        "como_corrigir": "Enfatizar importância das unidades"
    }
]

Estrutura do campo criterios_correcao (JSONB) - para dissertativas:
{
    "criterios": [
        {
            "descricao": "Mencionar o conceito X",
            "peso": 2,
            "obrigatorio": true
        },
        {
            "descricao": "Apresentar exemplo prático",
            "peso": 1,
            "obrigatorio": false
        }
    ],
    "pontuacao_maxima": 10,
    "pontuacao_minima_aprovacao": 6
}

Estrutura do campo fontes_bibliograficas (JSONB):
[
    {
        "tipo": "livro",
        "autor": "Halliday, Resnick, Walker",
        "titulo": "Fundamentos de Física",
        "edicao": "10ª",
        "editora": "LTC",
        "ano": 2016,
        "paginas": "45-48",
        "capitulo": "3",
        "isbn": "978-85-216-2951-5",
        "relevancia": "Definição formal do conceito"
    },
    {
        "tipo": "artigo",
        "autor": "Silva, J.A.; Santos, M.B.",
        "titulo": "Revisão sobre mecânica newtoniana",
        "revista": "Revista Brasileira de Física",
        "volume": "42",
        "numero": "3",
        "ano": 2020,
        "doi": "10.1590/xxx",
        "relevancia": "Aplicações modernas"
    },
    {
        "tipo": "site",
        "autor": "Khan Academy",
        "titulo": "Leis de Newton",
        "url": "https://...",
        "acesso_em": "2024-12-14",
        "relevancia": "Material complementar para alunos"
    }
]
*/

COMMENT ON COLUMN provas.questoes.alternativas_comentadas IS 'Alternativas com explicações detalhadas de cada opção (correta e incorretas)';
COMMENT ON COLUMN provas.questoes.explicacao_geral IS 'Explicação geral da questão para o professor';
COMMENT ON COLUMN provas.questoes.resolucao_passo_a_passo IS 'Resolução detalhada passo a passo';
COMMENT ON COLUMN provas.questoes.erros_comuns IS 'Erros frequentes dos alunos e como identificá-los';
COMMENT ON COLUMN provas.questoes.dicas_correcao IS 'Dicas para o professor durante a correção';
COMMENT ON COLUMN provas.questoes.criterios_correcao IS 'Critérios de correção (especialmente para dissertativas)';
COMMENT ON COLUMN provas.questoes.pontos_chave IS 'Pontos-chave que devem estar na resposta';
COMMENT ON COLUMN provas.questoes.nivel_cognitivo IS 'Nível na taxonomia de Bloom (lembrar, entender, aplicar, analisar, avaliar, criar)';
COMMENT ON COLUMN provas.questoes.tempo_estimado_min IS 'Tempo estimado para responder em minutos';
COMMENT ON COLUMN provas.questoes.palavras_chave IS 'Palavras-chave para busca e categorização';

-- ============================================================================
-- TABELA: TEMPLATES DE QUESTAO
-- ============================================================================
-- Templates para diferentes tipos de questão e níveis

CREATE TABLE IF NOT EXISTS provas.templates_questao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    tipo_questao provas.tipo_questao NOT NULL,
    
    -- Template para geração pela IA
    prompt_geracao TEXT NOT NULL,
    /*
    Exemplo:
    "Gere uma questão de múltipla escolha sobre {topico} com:
    - Enunciado claro e objetivo
    - 5 alternativas (A a E)
    - Apenas 1 alternativa correta
    - Para cada alternativa, explique:
      * Se correta: por que está certa
      * Se incorreta: por que está errada e qual erro conceitual representa
    - Inclua explicação geral da questão
    - Liste erros comuns dos alunos
    - Indique fontes bibliográficas"
    */
    
    -- Estrutura esperada da resposta
    estrutura_resposta JSONB,
    
    -- Configurações
    num_alternativas INT DEFAULT 5,
    requer_explicacao_alternativas BOOLEAN DEFAULT TRUE,
    requer_fontes BOOLEAN DEFAULT TRUE,
    requer_erros_comuns BOOLEAN DEFAULT TRUE,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TRIGGER trg_templates_questao_updated_at
    BEFORE UPDATE ON provas.templates_questao
    FOR EACH ROW
    EXECUTE FUNCTION provas.atualizar_updated_at();

COMMENT ON TABLE provas.templates_questao IS 'Templates para geração de questões pela IA';

-- ============================================================================
-- INSERIR TEMPLATES PADRÃO
-- ============================================================================

INSERT INTO provas.templates_questao (nome, descricao, tipo_questao, prompt_geracao, num_alternativas) VALUES

('Múltipla Escolha Padrão', 
 'Questão de múltipla escolha com 5 alternativas e explicações completas',
 'multipla_escolha',
 'Gere uma questão de múltipla escolha sobre o tópico: {topico}

REQUISITOS:
1. ENUNCIADO: Claro, objetivo, sem ambiguidades
2. ALTERNATIVAS: 5 opções (A a E), apenas 1 correta
3. PARA CADA ALTERNATIVA forneça:
   - Se CORRETA: Explicação detalhada de por que está certa
   - Se INCORRETA: Explicação de por que está errada e qual erro conceitual representa

4. EXPLICAÇÃO GERAL: Resumo do conceito abordado
5. ERROS COMUNS: Liste 2-3 erros frequentes dos alunos
6. FONTES: Indique pelo menos 1 referência bibliográfica

Nível de dificuldade: {dificuldade}
Tempo estimado: {tempo_estimado} minutos',
 5),

('Verdadeiro ou Falso',
 'Questão V/F com justificativa',
 'verdadeiro_falso',
 'Gere uma questão de Verdadeiro ou Falso sobre o tópico: {topico}

REQUISITOS:
1. AFIRMAÇÃO: Clara e sem ambiguidades
2. RESPOSTA: V ou F
3. EXPLICAÇÃO:
   - Se VERDADEIRO: Por que a afirmação está correta
   - Se FALSO: O que está errado e qual seria a forma correta

4. ARMADILHAS COMUNS: O que pode confundir o aluno
5. FONTE: Referência bibliográfica

Nível de dificuldade: {dificuldade}',
 2),

('Dissertativa com Critérios',
 'Questão dissertativa com critérios de correção detalhados',
 'dissertativa',
 'Gere uma questão dissertativa sobre o tópico: {topico}

REQUISITOS:
1. ENUNCIADO: Pergunta clara que permita resposta elaborada
2. RESPOSTA ESPERADA: Resposta modelo completa
3. CRITÉRIOS DE CORREÇÃO:
   - Liste cada ponto que deve estar na resposta
   - Atribua peso/pontuação para cada critério
   - Indique quais são obrigatórios

4. PONTOS-CHAVE: Conceitos essenciais que devem aparecer
5. ERROS COMUNS: O que alunos costumam esquecer ou errar
6. RUBRICA: Como pontuar respostas parciais

Nível de dificuldade: {dificuldade}
Pontuação máxima: {pontuacao}',
 0),

('Numérica com Resolução',
 'Questão numérica/cálculo com resolução passo a passo',
 'numerica',
 'Gere uma questão numérica/de cálculo sobre o tópico: {topico}

REQUISITOS:
1. ENUNCIADO: Problema claro com todos os dados necessários
2. RESPOSTA: Valor numérico com unidade
3. RESOLUÇÃO PASSO A PASSO:
   - Cada etapa do cálculo explicada
   - Fórmulas utilizadas
   - Substituição de valores

4. TOLERÂNCIA: Margem de erro aceitável (se aplicável)
5. ERROS COMUNS:
   - Erros de unidade
   - Erros de cálculo frequentes
   - Fórmulas erradas que alunos usam

6. DICAS DE CORREÇÃO: O que verificar na resposta

Nível de dificuldade: {dificuldade}',
 0)

ON CONFLICT DO NOTHING;

-- ============================================================================
-- VIEW: Questões com Explicações Completas
-- ============================================================================

CREATE OR REPLACE VIEW provas.vw_questoes_comentadas AS
SELECT 
    q.id,
    q.codigo,
    q.enunciado,
    q.tipo,
    q.dificuldade,
    q.status,
    q.alternativas_comentadas,
    q.explicacao_geral,
    q.resolucao_passo_a_passo,
    q.erros_comuns,
    q.fontes_bibliograficas,
    q.criterios_correcao,
    q.nivel_cognitivo,
    q.tempo_estimado_min,
    q.created_at,
    q.aprovada_em,
    m.nome AS materia,
    t.nome AS topico,
    u.nome AS professor_nome,
    -- Indicadores de completude
    (q.alternativas_comentadas IS NOT NULL) AS tem_alternativas_comentadas,
    (q.explicacao_geral IS NOT NULL AND q.explicacao_geral != '') AS tem_explicacao,
    (q.fontes_bibliograficas IS NOT NULL AND jsonb_array_length(q.fontes_bibliograficas) > 0) AS tem_fontes,
    (q.erros_comuns IS NOT NULL AND jsonb_array_length(q.erros_comuns) > 0) AS tem_erros_comuns
FROM provas.questoes q
LEFT JOIN provas.materias m ON q.materia_id = m.id
LEFT JOIN provas.topicos t ON q.topico_id = t.id
LEFT JOIN provas.usuarios u ON q.professor_id = u.id
WHERE q.deleted_at IS NULL
ORDER BY q.created_at DESC;

COMMENT ON VIEW provas.vw_questoes_comentadas IS 'Questões com indicadores de completude das explicações';

-- ============================================================================
-- FUNÇÃO: Validar Completude da Questão
-- ============================================================================

CREATE OR REPLACE FUNCTION provas.fn_validar_questao_completa(p_questao_id UUID)
RETURNS TABLE (
    completa BOOLEAN,
    itens_faltando TEXT[],
    porcentagem_completa INT
) AS $$
DECLARE
    v_questao RECORD;
    v_itens_faltando TEXT[] := '{}';
    v_total_itens INT := 0;
    v_itens_ok INT := 0;
BEGIN
    SELECT * INTO v_questao FROM provas.questoes WHERE id = p_questao_id;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, ARRAY['Questão não encontrada']::TEXT[], 0;
        RETURN;
    END IF;
    
    -- Verificar enunciado
    v_total_itens := v_total_itens + 1;
    IF v_questao.enunciado IS NOT NULL AND v_questao.enunciado != '' THEN
        v_itens_ok := v_itens_ok + 1;
    ELSE
        v_itens_faltando := array_append(v_itens_faltando, 'Enunciado');
    END IF;
    
    -- Verificar alternativas comentadas (para múltipla escolha e V/F)
    IF v_questao.tipo IN ('multipla_escolha', 'verdadeiro_falso') THEN
        v_total_itens := v_total_itens + 1;
        IF v_questao.alternativas_comentadas IS NOT NULL THEN
            v_itens_ok := v_itens_ok + 1;
        ELSE
            v_itens_faltando := array_append(v_itens_faltando, 'Alternativas com explicações');
        END IF;
    END IF;
    
    -- Verificar explicação geral
    v_total_itens := v_total_itens + 1;
    IF v_questao.explicacao_geral IS NOT NULL AND v_questao.explicacao_geral != '' THEN
        v_itens_ok := v_itens_ok + 1;
    ELSE
        v_itens_faltando := array_append(v_itens_faltando, 'Explicação geral');
    END IF;
    
    -- Verificar fontes bibliográficas
    v_total_itens := v_total_itens + 1;
    IF v_questao.fontes_bibliograficas IS NOT NULL AND jsonb_array_length(v_questao.fontes_bibliograficas) > 0 THEN
        v_itens_ok := v_itens_ok + 1;
    ELSE
        v_itens_faltando := array_append(v_itens_faltando, 'Fontes bibliográficas');
    END IF;
    
    -- Verificar erros comuns
    v_total_itens := v_total_itens + 1;
    IF v_questao.erros_comuns IS NOT NULL AND jsonb_array_length(v_questao.erros_comuns) > 0 THEN
        v_itens_ok := v_itens_ok + 1;
    ELSE
        v_itens_faltando := array_append(v_itens_faltando, 'Erros comuns dos alunos');
    END IF;
    
    -- Critérios de correção (para dissertativas)
    IF v_questao.tipo = 'dissertativa' THEN
        v_total_itens := v_total_itens + 1;
        IF v_questao.criterios_correcao IS NOT NULL THEN
            v_itens_ok := v_itens_ok + 1;
        ELSE
            v_itens_faltando := array_append(v_itens_faltando, 'Critérios de correção');
        END IF;
    END IF;
    
    RETURN QUERY SELECT 
        (array_length(v_itens_faltando, 1) IS NULL OR array_length(v_itens_faltando, 1) = 0),
        v_itens_faltando,
        ((v_itens_ok::FLOAT / v_total_itens::FLOAT) * 100)::INT;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION provas.fn_validar_questao_completa IS 'Valida se uma questão tem todos os campos necessários preenchidos';

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('010_questao_comentada_completa.sql', md5('010_questao_comentada_completa'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 010
-- ============================================================================

