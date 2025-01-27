"""
title: Youtube Transcript Provider (Langchain Community)
author: thearyadev && cloph
author_url: https://github.com/thearyadev/youtube-transcript-provider
funding_url: https://github.com/open-webui
version: 0.0.3
"""

from typing import Awaitable, Callable, Any
from langchain_community.document_loaders import YoutubeLoader
import traceback

class Tools:
    def __init__(self):
        self.citation = True

    async def get_youtube_transcript(
        self,
        url: str,
        __event_emitter__: Callable[[dict[str, dict[str, Any] | str]], Awaitable[None]],
    ) -> str:
        """
        Tenta recolher a transcrição na seguinte ordem de prioridade:
         1. Inglês oficial (en)
         2. Inglês automático (en_auto)
         3. Português (pt)
         4. Português automático (pt_auto)
         5. Português do Brasil (pt-BR)
         6. Português do Brasil automático (pt-BR_auto)

        Retorna a primeira transcrição encontrada ou mensagem de erro.
        """
        try:
            # Exemplo de URL inválida
            if "dQw4w9WgXcQ" in url:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"{url} is not a valid youtube link",
                            "done": True,
                        },
                    }
                )
                return "The tool failed with an error. No transcript has been provided."

            # Ordem de prioridade
            languages_in_order = [
                "en",
                "en_auto",
                "pt",
                "pt_auto",
                "pt-BR",
                "pt-BR_auto"
            ]

            data = None

            for lang in languages_in_order:
                try:
                    candidate_data = YoutubeLoader.from_youtube_url(
                        youtube_url=url,
                        add_video_info=False,
                        language=[lang]
                    ).load()
                    if candidate_data:
                        data = candidate_data
                        break  # Encontrou e interrompe
                except Exception:
                    pass

            if not data:
                # Não encontrou legendas em nenhum idioma listado
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Failed to retrieve transcript for {url}. No results",
                            "done": True,
                        },
                    }
                )
                return "The tool failed with an error. No transcript has been provided."

            # Constrói a resposta a partir do primeiro Document
            doc = data[0]
            title = doc.metadata.get("title", "No Title")
            lang = doc.metadata.get("language", "unknown")
            auto_flag = doc.metadata.get("is_auto_generated", False)
            transcript_content = doc.page_content
            auto_text = " (auto)" if auto_flag else ""

            # Emite evento de sucesso
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Successfully retrieved transcript for {url} in language {lang}{auto_text}",
                        "done": True,
                    },
                }
            )

            return (
                f"Title: {title}\n"
                f"Language: {lang}{auto_text}\n\n"
                f"Transcript:\n{transcript_content}"
            )

        except:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Failed to retrieve transcript for {url}.",
                        "done": True,
                    },
                }
            )
            return (
                "The tool failed with an error. No transcript has been provided.\n"
                f"Error Traceback:\n{traceback.format_exc()}"
            )

