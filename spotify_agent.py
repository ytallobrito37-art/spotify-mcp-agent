# -*- coding: utf-8 -*-

from langgraph.graph import StateGraph, END
from typing import List, Dict, Any
from pydantic import BaseModel
from spotify_mcp import (
    buscar_musica, 
    buscar_artista, 
    top_musicas_artista,
    recomendacoes,
    analise_musica
)

class AgentState(BaseModel):
    pergunta: str
    resultados: List[Dict] = []
    analise: str = ""
    
    class Config:
        arbitrary_types_allowed = True

class SpotifyAgent:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        
        graph.add_node("buscar", self._node_buscar)
        graph.add_node("analisar", self._node_analisar)
        
        graph.add_edge("buscar", "analisar")
        graph.add_edge("analisar", END)
        
        graph.set_entry_point("buscar")
        return graph.compile()

    def _node_buscar(self, state: AgentState) -> AgentState:
        """Busca músicas/artistas"""
        print(f"🔍 Buscando: {state.pergunta}")
        
        # Detectar se é música ou artista
        if "artista" in state.pergunta.lower():
            resultado = buscar_artista(state.pergunta.replace("artista", "").strip())
        else:
            resultado = buscar_musica(state.pergunta)
        
        state.resultados = resultado.get("musicas", resultado.get("artistas", []))
        state.analise = resultado.get("mensagem", "")
        
        return state

    def _node_analisar(self, state: AgentState) -> AgentState:
        """Analisa resultados"""
        print(f"📊 Analisando {len(state.resultados)} resultados...")
        
        if state.resultados:
            state.analise += f"\n\n✓ Top resultado:\n"
            primeiro = state.resultados[0]
            
            if "nome" in primeiro:
                state.analise += f"  🎵 {primeiro.get('nome', '')}\n"
            if "artista" in primeiro:
                state.analise += f"  👤 {primeiro.get('artista', '')}\n"
            if "popularidade" in primeiro:
                state.analise += f"  ⭐ Popularidade: {primeiro.get('popularidade', 0)}/100\n"
            if "url" in primeiro:
                state.analise += f"  🔗 {primeiro.get('url', '')}\n"
        
        return state

    def run(self, pergunta: str) -> Dict[str, Any]:
        """Executa agente"""
        estado_inicial = AgentState(pergunta=pergunta)
        resultado = self.graph.invoke(estado_inicial)
        
        # LangGraph sempre retorna algo dict-like
        resultado = dict(resultado)
        
        return {
            "pergunta": pergunta,
            "resultados": resultado.get("resultados", [])[:3],
            "analise": resultado.get("analise", "")
        }

    def print_resultado(self, resultado: Dict[str, Any]):
        """Imprime resultado"""
        print("\n" + "="*60)
        print("🎵 RESULTADO DA BUSCA")
        print("="*60)
        print(f"\n❓ {resultado['pergunta']}")
        print(resultado['analise'])
        print("\n" + "="*60)
