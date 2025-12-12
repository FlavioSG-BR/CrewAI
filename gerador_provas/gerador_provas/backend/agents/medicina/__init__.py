# -*- coding: utf-8 -*-
"""
Agentes especializados em Medicina.
Módulo focado em questões para cursos de graduação em Medicina.
"""

from backend.agents.medicina.farmacologia import AgenteFarmacologia
from backend.agents.medicina.histologia import AgenteHistologia
from backend.agents.medicina.anatomia import AgenteAnatomia
from backend.agents.medicina.fisiologia import AgenteFisiologia
from backend.agents.medicina.patologia import AgentePatologia
from backend.agents.medicina.bioquimica import AgenteBioquimica
from backend.agents.medicina.microbiologia import AgenteMicrobiologia
from backend.agents.medicina.casos_clinicos import AgenteCasosClinico

__all__ = [
    'AgenteFarmacologia',
    'AgenteHistologia',
    'AgenteAnatomia',
    'AgenteFisiologia',
    'AgentePatologia',
    'AgenteBioquimica',
    'AgenteMicrobiologia',
    'AgenteCasosClinico',
]

