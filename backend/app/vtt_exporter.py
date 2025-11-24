# backend/app/vtt_exporter.py
import json
import zipfile
import io
from .models import Aventura

class VTTExporter:
    def __init__(self, aventura: Aventura):
        self.aventura = aventura
        self.module = {
            "name": self.aventura.titulo.lower().replace(" ", "-"),
            "title": self.aventura.titulo,
            "description": self.aventura.sinopse,
            "version": "1.0.0",
            "author": "Gerador de One-Shots",
            "packs": []
        }

    def _create_journal_entries(self):
        """Cria as entradas do diário para a aventura."""
        journal_entries = []
        
        # Entrada para a Sinopse e Contexto
        journal_entries.append({
            "name": f"{self.aventura.titulo}: Sinopse e Contexto",
            "content": f"<h1>Sinopse</h1><p>{self.aventura.sinopse}</p><h1>Contexto</h1><p>{self.aventura.contexto}</p>",
            "img": "",
            "flags": {}
        })
        
        # Entrada para Ganchos da Trama
        ganchos_html = "<ul>" + "".join(f"<li>{gancho}</li>" for gancho in self.aventura.gancho_trama) + "</ul>"
        journal_entries.append({
            "name": "Ganchos da Trama",
            "content": ganchos_html,
            "img": "",
            "flags": {}
        })
        
        # Entradas para cada Ato
        for i, ato in enumerate(self.aventura.estrutura):
            journal_entries.append({
                "name": f"Ato {i+1}: {ato.titulo}",
                "content": f"<p>{ato.descricao}</p>",
                "img": "",
                "flags": {}
            })
            
        self.journal_pack = {
            "name": "aventura",
            "label": "Aventura",
            "system": "dnd5e", # Pode ser parametrizado no futuro
            "path": "./packs/aventura.db",
            "entity": "JournalEntry"
        }
        
        self.module["packs"].append(self.journal_pack)
        self.journal_entries_json = "\n".join(json.dumps(entry) for entry in journal_entries)


    def _create_actors(self):
        """Cria os Atores para os NPCs."""
        actors = []
        for npc in self.aventura.personagens_chave:
            actors.append({
                "name": npc.nome,
                "type": "npc",
                "img": npc.url_imagem or "icons/svg/mystery-man.svg",
                "data": {
                    "details": {
                        "biography": {
                            "value": f"<p><strong>Aparência:</strong> {npc.aparencia}</p><p><strong>Motivação:</strong> {npc.motivacao}</p><p><strong>Segredo:</strong> {npc.segredo}</p>"
                        }
                    }
                },
                "flags": {}
            })
            
        self.actor_pack = {
            "name": "npcs",
            "label": "NPCs",
            "system": "dnd5e",
            "path": "./packs/npcs.db",
            "entity": "Actor"
        }
        self.module["packs"].append(self.actor_pack)
        self.actors_json = "\n".join(json.dumps(actor) for actor in actors)

    def _create_scenes(self):
        """Cria as Cenas para os locais."""
        scenes = []
        for local in self.aventura.locais_importantes:
            scenes.append({
                "name": local.nome,
                "img": local.url_imagem,
                "navName": local.nome,
                "width": 4000,
                "height": 3000,
                "grid": 100,
                "flags": {}
            })
            
        self.scene_pack = {
            "name": "cenas",
            "label": "Cenas",
            "system": "dnd5e",
            "path": "./packs/cenas.db",
            "entity": "Scene"
        }
        self.module["packs"].append(self.scene_pack)
        self.scenes_json = "\n".join(json.dumps(scene) for scene in scenes)

    def export_to_foundry(self) -> bytes:
        """Exporta a aventura para um módulo do FoundryVTT."""
        self._create_journal_entries()
        self._create_actors()
        self._create_scenes()

        # Cria um arquivo zip em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Adiciona o module.json
            zip_file.writestr("module.json", json.dumps(self.module, indent=2))

            # Adiciona os compendium packs
            if hasattr(self, 'journal_entries_json'):
                zip_file.writestr(self.journal_pack['path'].replace('./', ''), self.journal_entries_json)
            if hasattr(self, 'actors_json'):
                zip_file.writestr(self.actor_pack['path'].replace('./', ''), self.actors_json)
            if hasattr(self, 'scenes_json'):
                zip_file.writestr(self.scene_pack['path'].replace('./', ''), self.scenes_json)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()
