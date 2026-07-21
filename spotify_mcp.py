from fastmcp import FastMCP
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional, List
import os

mcp = FastMCP("spotify-agent")

# Inicializar Spotify
def get_spotify_client():
    """Conecta com API do Spotify"""
    try:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return None
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except:
        return None

@mcp.tool()
def buscar_musica(
    nome_musica: str,
    limite: int = 5
) -> dict:
    """
    Busca uma música no Spotify.
    
    Args:
        nome_musica: Nome da música a buscar
        limite: Quantos resultados retornar
    
    Returns:
        Lista de músicas encontradas
    """
    sp = get_spotify_client()
    
    if not sp:
        return {
            "sucesso": False,
            "erro": "Spotify não configurado. Defina SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET"
        }
    
    try:
        resultados = sp.search(q=nome_musica, type='track', limit=limite)
        
        musicas = []
        for track in resultados.get('tracks', {}).get('items', []):
            musicas.append({
                "id": track.get('id', ''),
                "nome": track.get('name', ''),
                "artista": ", ".join([a.get('name', '') for a in track.get('artists', [])]),
                "album": track.get('album', {}).get('name', ''),
                "duracao_ms": track.get('duration_ms', 0),
                "popularidade": track.get('popularity', 0),
                "url": track.get('external_urls', {}).get('spotify', '')
            })
        
        return {
            "sucesso": True,
            "total": len(musicas),
            "musicas": musicas,
            "mensagem": f"✓ Encontradas {len(musicas)} músicas"
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@mcp.tool()
def buscar_artista(
    nome_artista: str,
    limite: int = 5
) -> dict:
    """
    Busca artistas no Spotify.
    
    Args:
        nome_artista: Nome do artista
        limite: Quantos resultados
    
    Returns:
        Lista de artistas
    """
    sp = get_spotify_client()
    
    if not sp:
        return {
            "sucesso": False,
            "erro": "Spotify não configurado"
        }
    
    try:
        resultados = sp.search(q=nome_artista, type='artist', limit=limite)
        
        artistas = []
        for artist in resultados.get('artists', {}).get('items', []):
            artistas.append({
                "id": artist.get('id', ''),
                "nome": artist.get('name', ''),
                "generos": artist.get('genres', []),
                "popularidade": artist.get('popularity', 0),
                "seguidores": artist.get('followers', {}).get('total', 0),
                "url": artist.get('external_urls', {}).get('spotify', '')
            })
        
        return {
            "sucesso": True,
            "total": len(artistas),
            "artistas": artistas,
            "mensagem": f"✓ Encontrados {len(artistas)} artistas"
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@mcp.tool()
def top_musicas_artista(
    id_artista: str,
    limite: int = 5
) -> dict:
    """
    Retorna top músicas de um artista.
    
    Args:
        id_artista: ID do artista no Spotify
        limite: Quantas top músicas
    
    Returns:
        Top músicas do artista
    """
    sp = get_spotify_client()
    
    if not sp:
        return {"sucesso": False, "erro": "Spotify não configurado"}
    
    try:
        resultados = sp.artist_top_tracks(id_artista, country='US')
        
        musicas = []
        for track in resultados['tracks'][:limite]:
            musicas.append({
                "nome": track['name'],
                "artista": ", ".join([a['name'] for a in track['artists']]),
                "popularidade": track['popularity'],
                "duracao_ms": track['duration_ms'],
                "url": track['external_urls']['spotify']
            })
        
        return {
            "sucesso": True,
            "total": len(musicas),
            "musicas": musicas,
            "mensagem": f"✓ Top {len(musicas)} músicas"
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@mcp.tool()
def recomendacoes(
    ids_musicas: List[str],
    limite: int = 5
) -> dict:
    """
    Pega recomendações baseadas em músicas.
    
    Args:
        ids_musicas: Lista com IDs de músicas (máx 5)
        limite: Quantas recomendações
    
    Returns:
        Músicas recomendadas
    """
    sp = get_spotify_client()
    
    if not sp:
        return {"sucesso": False, "erro": "Spotify não configurado"}
    
    try:
        # Limitar a 5 músicas
        ids_musicas = ids_musicas[:5]
        
        resultados = sp.recommendations(seed_tracks=ids_musicas, limit=limite)
        
        musicas = []
        for track in resultados['tracks']:
            musicas.append({
                "nome": track['name'],
                "artista": ", ".join([a['name'] for a in track['artists']]),
                "album": track['album']['name'],
                "popularidade": track['popularity'],
                "url": track['external_urls']['spotify']
            })
        
        return {
            "sucesso": True,
            "total": len(musicas),
            "musicas": musicas,
            "mensagem": f"✓ {len(musicas)} recomendações geradas"
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


@mcp.tool()
def analise_musica(id_musica: str) -> dict:
    """
    Analisa características de uma música.
    
    Args:
        id_musica: ID da música no Spotify
    
    Returns:
        Análise com features da música
    """
    sp = get_spotify_client()
    
    if not sp:
        return {"sucesso": False, "erro": "Spotify não configurado"}
    
    try:
        track = sp.track(id_musica)
        features = sp.audio_features(id_musica)[0]
        
        return {
            "sucesso": True,
            "musica": {
                "nome": track['name'],
                "artista": ", ".join([a['name'] for a in track['artists']]),
                "features": {
                    "danca": features['danceability'],
                    "energia": features['energy'],
                    "acustica": features['acousticness'],
                    "instrumental": features['instrumentalness'],
                    "valencia": features['valence'],
                    "tempo": features['tempo'],
                    "tempo_assinatura": features['time_signature']
                }
            },
            "mensagem": "✓ Análise concluída"
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


if __name__ == "__main__":
    import uvicorn
    print("🎵 MCP Spotify iniciando na porta 8000...")
    print("Ferramentas disponíveis:")
    print("  - buscar_musica")
    print("  - buscar_artista")
    print("  - top_musicas_artista")
    print("  - recomendacoes")
    print("  - analise_musica")
    uvicorn.run(mcp.app, host="0.0.0.0", port=8000)
