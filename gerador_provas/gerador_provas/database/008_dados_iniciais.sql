-- ============================================================================
-- GERADOR DE PROVAS - MIGRAÇÃO 008: DADOS INICIAIS (SEED)
-- ============================================================================
-- Descrição: Dados iniciais para o funcionamento do sistema
-- Autor: Sistema
-- Data: 2024-12-11
-- ============================================================================

SET search_path TO provas, public;

-- ============================================================================
-- MATÉRIAS
-- ============================================================================

INSERT INTO provas.materias (codigo, nome, descricao, icone, cor_primaria, cor_secundaria, ordem)
VALUES 
    ('FIS', 'Física', 'Mecânica, Termodinâmica, Eletromagnetismo, Óptica e Ondulatória', '🔬', '#3498db', '#2980b9', 1),
    ('QUI', 'Química', 'Química Geral, Orgânica, Inorgânica e Físico-Química', '⚗️', '#27ae60', '#1e8449', 2),
    ('MAT', 'Matemática', 'Álgebra, Geometria, Trigonometria, Cálculo e Estatística', '📐', '#e74c3c', '#c0392b', 3),
    ('BIO', 'Biologia', 'Citologia, Genética, Ecologia, Fisiologia e Evolução', '🧬', '#9b59b6', '#8e44ad', 4),
    ('GEO', 'Geografia', 'Geografia Física, Humana, Política e Econômica', '🌍', '#1abc9c', '#16a085', 5),
    ('HIS', 'História', 'História Geral, do Brasil, Contemporânea e Antiga', '📜', '#f39c12', '#d68910', 6),
    ('POR', 'Português', 'Gramática, Literatura, Interpretação e Redação', '📚', '#34495e', '#2c3e50', 7)
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================================
-- TÓPICOS DE FÍSICA
-- ============================================================================

INSERT INTO provas.topicos (materia_id, codigo, nome, descricao, icone, ordem)
SELECT m.id, t.codigo, t.nome, t.descricao, t.icone, t.ordem
FROM provas.materias m
CROSS JOIN (
    VALUES 
        ('MRU', 'Movimento Retilíneo Uniforme', 'Movimento com velocidade constante', '🚗', 1),
        ('MRUV', 'Movimento Retilíneo Uniformemente Variado', 'Movimento com aceleração constante', '🚀', 2),
        ('QUEDA_LIVRE', 'Queda Livre', 'Movimento sob ação exclusiva da gravidade', '🍎', 3),
        ('LANCAMENTOS', 'Lançamentos', 'Lançamento horizontal e oblíquo', '🎯', 4),
        ('LEIS_NEWTON', 'Leis de Newton', 'Dinâmica e forças', '⚖️', 5),
        ('TRABALHO_ENERGIA', 'Trabalho e Energia', 'Energia cinética, potencial e conservação', '⚡', 6),
        ('IMPULSO_MOMENTUM', 'Impulso e Quantidade de Movimento', 'Colisões e conservação de momentum', '💥', 7),
        ('GRAVITACAO', 'Gravitação', 'Leis de Kepler e gravitação universal', '🌍', 8),
        ('TERMODINAMICA', 'Termodinâmica', 'Calor, temperatura e leis da termodinâmica', '🌡️', 9),
        ('ONDAS', 'Ondas', 'Ondulatória e acústica', '🌊', 10),
        ('OPTICA', 'Óptica', 'Reflexão, refração e instrumentos ópticos', '💡', 11),
        ('ELETROSTATICA', 'Eletrostática', 'Cargas elétricas e campo elétrico', '⚡', 12),
        ('ELETRODINAMICA', 'Eletrodinâmica', 'Corrente elétrica e circuitos', '🔌', 13),
        ('MAGNETISMO', 'Magnetismo', 'Campo magnético e eletromagnetismo', '🧲', 14)
) AS t(codigo, nome, descricao, icone, ordem)
WHERE m.codigo = 'FIS'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- TÓPICOS DE QUÍMICA
-- ============================================================================

INSERT INTO provas.topicos (materia_id, codigo, nome, descricao, icone, ordem)
SELECT m.id, t.codigo, t.nome, t.descricao, t.icone, t.ordem
FROM provas.materias m
CROSS JOIN (
    VALUES 
        ('TABELA_PERIODICA', 'Tabela Periódica', 'Elementos e propriedades periódicas', '📊', 1),
        ('MODELO_ATOMICO', 'Modelos Atômicos', 'Evolução dos modelos atômicos', '⚛️', 2),
        ('LIGACOES', 'Ligações Químicas', 'Iônica, covalente e metálica', '🔗', 3),
        ('FUNCOES_INORGANICAS', 'Funções Inorgânicas', 'Ácidos, bases, sais e óxidos', '🧪', 4),
        ('REACOES', 'Reações Químicas', 'Tipos de reações e balanceamento', '⚗️', 5),
        ('ESTEQUIOMETRIA', 'Estequiometria', 'Cálculos estequiométricos', '⚖️', 6),
        ('SOLUCOES', 'Soluções', 'Concentração e diluição', '💧', 7),
        ('TERMOQUIMICA', 'Termoquímica', 'Entalpia e lei de Hess', '🔥', 8),
        ('CINETICA', 'Cinética Química', 'Velocidade das reações', '⏱️', 9),
        ('EQUILIBRIO', 'Equilíbrio Químico', 'Constante de equilíbrio e Le Chatelier', '⚖️', 10),
        ('ELETROQUIMICA', 'Eletroquímica', 'Pilhas e eletrólise', '🔋', 11),
        ('ORGANICA', 'Química Orgânica', 'Hidrocarbonetos e funções orgânicas', '🧬', 12)
) AS t(codigo, nome, descricao, icone, ordem)
WHERE m.codigo = 'QUI'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- TÓPICOS DE MATEMÁTICA
-- ============================================================================

INSERT INTO provas.topicos (materia_id, codigo, nome, descricao, icone, ordem)
SELECT m.id, t.codigo, t.nome, t.descricao, t.icone, t.ordem
FROM provas.materias m
CROSS JOIN (
    VALUES 
        ('CONJUNTOS', 'Conjuntos', 'Teoria dos conjuntos e operações', '🔵', 1),
        ('FUNCOES', 'Funções', 'Funções e seus gráficos', '📈', 2),
        ('FUNCAO_1GRAU', 'Função do 1º Grau', 'Função afim e equações', '📊', 3),
        ('FUNCAO_2GRAU', 'Função do 2º Grau', 'Parábola e equações quadráticas', '🎯', 4),
        ('EXPONENCIAL', 'Função Exponencial', 'Exponenciais e logaritmos', '📈', 5),
        ('LOGARITMO', 'Logaritmos', 'Propriedades e equações logarítmicas', '📉', 6),
        ('TRIGONOMETRIA', 'Trigonometria', 'Razões trigonométricas e funções', '📐', 7),
        ('PROGRESSOES', 'Progressões', 'PA e PG', '🔢', 8),
        ('MATRIZES', 'Matrizes', 'Operações e determinantes', '🔲', 9),
        ('SISTEMAS', 'Sistemas Lineares', 'Resolução de sistemas', '⚖️', 10),
        ('GEOMETRIA_PLANA', 'Geometria Plana', 'Áreas e perímetros', '📏', 11),
        ('GEOMETRIA_ESPACIAL', 'Geometria Espacial', 'Volumes e áreas de sólidos', '📦', 12),
        ('GEOMETRIA_ANALITICA', 'Geometria Analítica', 'Coordenadas e cônicas', '📍', 13),
        ('PROBABILIDADE', 'Probabilidade', 'Cálculo de probabilidades', '🎲', 14),
        ('ESTATISTICA', 'Estatística', 'Média, mediana e desvio padrão', '📊', 15),
        ('COMBINATORIA', 'Análise Combinatória', 'Permutações e combinações', '🔀', 16)
) AS t(codigo, nome, descricao, icone, ordem)
WHERE m.codigo = 'MAT'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- TAGS PADRÃO
-- ============================================================================

INSERT INTO provas.tags (nome, cor, descricao)
VALUES 
    ('ENEM', '#1abc9c', 'Questões no estilo ENEM'),
    ('Vestibular', '#3498db', 'Questões de vestibulares'),
    ('Olimpíada', '#9b59b6', 'Questões de olimpíadas científicas'),
    ('Conceitual', '#e74c3c', 'Questões conceituais/teóricas'),
    ('Cálculo', '#f39c12', 'Questões com cálculos'),
    ('Interpretação', '#2ecc71', 'Questões de interpretação'),
    ('Gráfico', '#34495e', 'Questões com gráficos'),
    ('Experimental', '#16a085', 'Questões sobre experimentos'),
    ('Cotidiano', '#e67e22', 'Questões do dia-a-dia'),
    ('Interdisciplinar', '#8e44ad', 'Questões interdisciplinares')
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- CONQUISTAS
-- ============================================================================

INSERT INTO provas.conquistas (codigo, nome, descricao, icone, tipo, requisito_valor, pontos)
VALUES 
    ('PRIMEIRA_QUESTAO', 'Primeiro Passo', 'Responda sua primeira questão', '🎯', 'questoes', 1, 10),
    ('QUESTOES_10', 'Iniciante', 'Responda 10 questões', '📝', 'questoes', 10, 50),
    ('QUESTOES_50', 'Estudante Dedicado', 'Responda 50 questões', '📚', 'questoes', 50, 100),
    ('QUESTOES_100', 'Veterano', 'Responda 100 questões', '🏆', 'questoes', 100, 200),
    ('QUESTOES_500', 'Mestre', 'Responda 500 questões', '👑', 'questoes', 500, 500),
    ('SEQUENCIA_5', 'Sequência de 5', 'Acerte 5 questões seguidas', '🔥', 'sequencia', 5, 30),
    ('SEQUENCIA_10', 'Imparável', 'Acerte 10 questões seguidas', '⚡', 'sequencia', 10, 75),
    ('PROVA_PERFEITA', 'Perfeição', 'Acerte todas as questões de uma prova', '💯', 'prova', 100, 150),
    ('TODAS_MATERIAS', 'Polivalente', 'Responda questões de todas as matérias', '🌟', 'materias', 7, 100)
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================================
-- CONFIGURAÇÕES DO SISTEMA
-- ============================================================================

INSERT INTO provas.configuracoes (chave, valor, tipo, categoria, descricao)
VALUES 
    ('sistema.nome', 'Gerador de Provas', 'string', 'geral', 'Nome do sistema'),
    ('sistema.versao', '1.0.0', 'string', 'geral', 'Versão atual'),
    ('questoes.max_por_prova', '50', 'int', 'questoes', 'Máximo de questões por prova'),
    ('questoes.tempo_padrao_min', '3', 'int', 'questoes', 'Tempo padrão por questão em minutos'),
    ('diagramas.dpi', '150', 'int', 'diagramas', 'DPI dos diagramas gerados'),
    ('diagramas.formato_padrao', 'png', 'string', 'diagramas', 'Formato padrão dos diagramas'),
    ('provas.embaralhar_padrao', 'false', 'bool', 'provas', 'Embaralhar questões por padrão'),
    ('usuarios.max_tentativas_login', '5', 'int', 'seguranca', 'Máximo de tentativas de login'),
    ('usuarios.tempo_bloqueio_min', '15', 'int', 'seguranca', 'Tempo de bloqueio após falhas')
ON CONFLICT (chave) DO NOTHING;

-- ============================================================================
-- MODELO DE PROVA PADRÃO
-- ============================================================================

INSERT INTO provas.modelos_prova (nome, descricao, configuracoes, ativo)
VALUES (
    'Padrão',
    'Modelo padrão de prova',
    '{
        "cabecalho": true,
        "rodape": true,
        "mostrar_pontuacao": true,
        "questoes_por_pagina": 5,
        "espaco_resposta": "medio",
        "incluir_gabarito": false
    }',
    true
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- REGISTRAR MIGRAÇÃO
-- ============================================================================

INSERT INTO provas.migrations (nome, checksum) 
VALUES ('008_dados_iniciais.sql', md5('008_dados_iniciais'))
ON CONFLICT (nome) DO NOTHING;

-- ============================================================================
-- FIM DA MIGRAÇÃO 008
-- ============================================================================

