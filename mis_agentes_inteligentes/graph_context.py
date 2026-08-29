"""
AST Subgraph Context Retrieval & Impact Engine (SPEC-013).
Motor modular determinista de extracción contextual guiado por grafo AST Graphify.
"""
import json
import logging
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class GraphCacheManager:
    """Administrador de caché en memoria de graphify-out/graph.json basado en mtime."""

    _lock = threading.Lock()
    _instance: Optional["GraphCacheManager"] = None

    def __init__(self, graph_path: Optional[str] = None):
        self.graph_path = graph_path
        self.last_mtime: float = 0.0
        self.nodes_by_id: Dict[str, Dict[str, Any]] = {}
        self.nodes_by_norm_label: Dict[str, List[Dict[str, Any]]] = {}
        self.nodes_by_file: Dict[str, List[Dict[str, Any]]] = {}
        self.adjacency: Dict[str, List[Dict[str, Any]]] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls, graph_path: Optional[str] = None) -> "GraphCacheManager":
        with cls._lock:
            if cls._instance is None or (graph_path and cls._instance.graph_path != graph_path):
                cls._instance = cls(graph_path)
            return cls._instance

    def _resolve_graph_path(self) -> str:
        if self.graph_path and os.path.exists(self.graph_path):
            return self.graph_path
        # Buscar en workspace actual
        possible = os.path.join(os.getcwd(), "graphify-out", "graph.json")
        if os.path.exists(possible):
            return possible
        return possible

    def is_valid(self) -> bool:
        path = self._resolve_graph_path()
        if not os.path.exists(path):
            return False
        try:
            current_mtime = os.path.getmtime(path)
            return self._loaded and current_mtime == self.last_mtime
        except Exception:
            return False

    def load(self) -> bool:
        path = self._resolve_graph_path()
        if not os.path.exists(path):
            self._loaded = False
            return False

        try:
            current_mtime = os.path.getmtime(path)
            if self._loaded and current_mtime == self.last_mtime:
                return True

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            nodes = data.get("nodes", [])
            links = data.get("links", []) or data.get("edges", [])

            nodes_by_id = {}
            nodes_by_norm_label = {}
            nodes_by_file = {}
            adjacency = {}

            for node in nodes:
                nid = node.get("id")
                if not nid:
                    continue
                label = str(node.get("label", ""))
                norm_label = str(node.get("norm_label", label.lower().strip()))
                clean_norm = norm_label.lstrip(".").rstrip("()").strip().lower()
                clean_norm_no_underscore = clean_norm.replace("_", "")
                source_file = str(node.get("source_file", ""))

                nodes_by_id[nid] = node

                if clean_norm not in nodes_by_norm_label:
                    nodes_by_norm_label[clean_norm] = []
                nodes_by_norm_label[clean_norm].append(node)

                if clean_norm_no_underscore not in nodes_by_norm_label:
                    nodes_by_norm_label[clean_norm_no_underscore] = []
                nodes_by_norm_label[clean_norm_no_underscore].append(node)

                if norm_label not in nodes_by_norm_label:
                    nodes_by_norm_label[norm_label] = []
                nodes_by_norm_label[norm_label].append(node)

                if source_file not in nodes_by_file:
                    nodes_by_file[source_file] = []
                nodes_by_file[source_file].append(node)

            for link in links:
                src = link.get("source")
                tgt = link.get("target")
                rel = link.get("relation", "relates_to")

                if src and tgt:
                    if src not in adjacency:
                        adjacency[src] = []
                    adjacency[src].append({"neighbor": tgt, "relation": rel, "direction": "outgoing"})

                    if tgt not in adjacency:
                        adjacency[tgt] = []
                    adjacency[tgt].append({"neighbor": src, "relation": rel, "direction": "incoming"})

            with self._lock:
                self.nodes_by_id = nodes_by_id
                self.nodes_by_norm_label = nodes_by_norm_label
                self.nodes_by_file = nodes_by_file
                self.adjacency = adjacency
                self.last_mtime = current_mtime
                self._loaded = True
            return True
        except Exception as e:
            logging.warning(f"[Graphify RAG] Error al cargar {path}: {e}")
            self._loaded = False
            return False


class TargetExtractor:
    """Extractor determinista de targets (archivos/símbolos) en 5 niveles sin LLM."""

    def __init__(self, cache_manager: GraphCacheManager):
        self.cache = cache_manager

    def extract(self, user_goal: str) -> Dict[str, Any]:
        if not self.cache.is_valid():
            self.cache.load()

        goal_clean = user_goal.strip()
        matched_file = None
        matched_symbol = None
        matched_labels = []

        # Nivel 1: Exact File Match (priorizar rutas más largas)
        file_candidates = sorted(self.cache.nodes_by_file.keys(), key=len, reverse=True)
        for fpath in file_candidates:
            fname = os.path.basename(fpath)
            if fname and (fname in goal_clean or fpath in goal_clean):
                matched_file = fpath
                break

        # Nivel 2 & 3: Symbol Extraction por tokens clave en el prompt
        tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", goal_clean)
        # Ordenar tokens por longitud descendente para preferir handle_sse_events antes que handle
        tokens_sorted = sorted(tokens, key=len, reverse=True)
        stopwords = {"python", "script", "file", "function", "class", "test", "para", "como", "con", "del", "los", "las", "una", "este", "esta", "que"}

        symbol_matches = []
        for tok in tokens_sorted:
            if len(tok) < 3 or tok.lower() in stopwords:
                continue

            tok_lower = tok.lower()
            tok_no_underscore = tok_lower.replace("_", "")
            # Buscar en norm_label exacto, sin guion bajo o con ()
            candidates = (
                self.cache.nodes_by_norm_label.get(tok_lower, []) +
                self.cache.nodes_by_norm_label.get(tok_no_underscore, []) +
                self.cache.nodes_by_norm_label.get(tok_lower + "()", [])
            )
            if candidates:
                for c in candidates:
                    if c not in symbol_matches:
                        symbol_matches.append(c)

        if symbol_matches:
            # Seleccionar la mejor coincidencia
            best_node = symbol_matches[0]
            raw_label = best_node.get("label", "")
            matched_symbol = re.sub(r"^\.|\(\)$", "", raw_label).strip()
            matched_labels = [re.sub(r"^\.|\(\)$", "", n.get("label", "")).strip() for n in symbol_matches if n.get("label")]
            matched_labels.extend([n.get("label") for n in symbol_matches if n.get("label")])

        # Nivel 4: Path Suffix Match si no se encontró archivo
        if not matched_file:
            for fpath in file_candidates:
                suffix = os.path.splitext(os.path.basename(fpath))[0]
                if suffix and len(suffix) > 3 and suffix in goal_clean:
                    matched_file = fpath
                    break

        return {
            "file": matched_file,
            "symbol": matched_symbol,
            "matched_labels": list(set(matched_labels))
        }


class SubgraphRetriever:
    """Recuperador de subgrafos acotados (1-hop / 2-hop) con tipificación de relaciones."""

    def __init__(self, cache_manager: GraphCacheManager):
        self.cache = cache_manager

    def retrieve(self, target_info: Dict[str, Any], depth: int = 1, task_type: str = "FEATURE") -> Dict[str, Any]:
        if not self.cache.is_valid():
            self.cache.load()

        matched_nodes: List[Dict[str, Any]] = []
        matched_ids: Set[str] = set()

        target_file = target_info.get("file")
        target_symbol = target_info.get("symbol")
        matched_labels = target_info.get("matched_labels", [])

        # Buscar nodos semilla (seeds)
        clean_target_symbol = re.sub(r"^\.|\(\)$", "", target_symbol).strip() if target_symbol else ""

        for nid, node in self.cache.nodes_by_id.items():
            lbl = node.get("label", "")
            clean_lbl = re.sub(r"^\.|\(\)$", "", lbl).strip()
            sf = node.get("source_file", "")
            if (clean_target_symbol and (clean_lbl == clean_target_symbol or lbl == target_symbol or lbl in matched_labels)) or (target_file and sf == target_file):
                matched_nodes.append(node)
                matched_ids.add(nid)

        if not matched_nodes and target_file:
            matched_nodes = self.cache.nodes_by_file.get(target_file, [])
            matched_ids = {n["id"] for n in matched_nodes if "id" in n}

        collected_nodes: Dict[str, Dict[str, Any]] = {n["id"]: n for n in matched_nodes if "id" in n}
        collected_edges: List[Dict[str, Any]] = []
        visited: Set[str] = set(matched_ids)

        # 1-Hop Traversal
        first_hop_neighbors: Set[str] = set()
        for nid in matched_ids:
            for edge in self.cache.adjacency.get(nid, []):
                nbr_id = edge["neighbor"]
                rel = edge["relation"]
                direction = edge["direction"]

                collected_edges.append({
                    "source": nid if direction == "outgoing" else nbr_id,
                    "target": nbr_id if direction == "outgoing" else nid,
                    "relation": rel
                })

                if nbr_id not in collected_nodes and nbr_id in self.cache.nodes_by_id:
                    collected_nodes[nbr_id] = self.cache.nodes_by_id[nbr_id]
                    first_hop_neighbors.add(nbr_id)

        # 2-Hop Traversal (solo para REFACTOR y DEBUG con depth=2)
        if depth >= 2 and task_type in ("REFACTOR", "DEBUG"):
            for nbr_id in first_hop_neighbors:
                for edge in self.cache.adjacency.get(nbr_id, []):
                    sec_nbr_id = edge["neighbor"]
                    rel = edge["relation"]
                    # Evitar explosión omitiendo aristas contains masivas de módulo
                    if rel == "contains":
                        continue
                    if sec_nbr_id not in collected_nodes and sec_nbr_id in self.cache.nodes_by_id:
                        collected_nodes[sec_nbr_id] = self.cache.nodes_by_id[sec_nbr_id]
                        collected_edges.append({
                            "source": nbr_id if edge["direction"] == "outgoing" else sec_nbr_id,
                            "target": sec_nbr_id if edge["direction"] == "outgoing" else nbr_id,
                            "relation": rel
                        })

        return {
            "target_info": target_info,
            "seed_ids": list(matched_ids),
            "nodes": list(collected_nodes.values()),
            "edges": collected_edges
        }


class ContextBudgeter:
    """Priorizador y podador determinista de nodos respetando max_tokens=1500."""

    def __init__(self, max_tokens: int = 1500, max_nodes: int = 15, max_files: int = 6):
        self.max_tokens = max_tokens
        self.max_nodes = max_nodes
        self.max_files = max_files

    def rank_and_prune(self, subgraph: Dict[str, Any]) -> Dict[str, Any]:
        seed_ids = set(subgraph.get("seed_ids", []))
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

        # Asignar prioridades deterministas P1-P5
        ranked_nodes = []
        for n in nodes:
            nid = n.get("id")
            rel_priority = 5
            if nid in seed_ids:
                rel_priority = 1
            else:
                # Comprobar si es caller/callee directo (P2) o import (P3)
                is_p2 = False
                is_p3 = False
                for e in edges:
                    if e["source"] == nid or e["target"] == nid:
                        r = e.get("relation")
                        if r in ("calls", "indirect_call"):
                            is_p2 = True
                        elif r in ("imports", "imports_from"):
                            is_p3 = True
                        elif r == "contains":
                            rel_priority = min(rel_priority, 4)

                if is_p2:
                    rel_priority = 2
                elif is_p3:
                    rel_priority = min(rel_priority, 3)

            n_copy = dict(n)
            n_copy["priority"] = rel_priority
            ranked_nodes.append(n_copy)

        # Ordenar deterministamente por Prioridad ascendente, luego por grado descendente
        ranked_nodes.sort(key=lambda x: (x["priority"], -x.get("degree", 0)))

        # Poda por max_nodes y max_files
        selected_nodes = []
        selected_files: Set[str] = set()

        for n in ranked_nodes:
            sf = n.get("source_file", "")
            if len(selected_nodes) < self.max_nodes:
                if sf:
                    if len(selected_files) < self.max_files or sf in selected_files:
                        selected_nodes.append(n)
                        selected_files.add(sf)
                else:
                    selected_nodes.append(n)

        # Filtrar edges para incluir solo nodos seleccionados
        selected_ids = {n["id"] for n in selected_nodes if "id" in n}
        selected_edges = [e for e in edges if e["source"] in selected_ids and e["target"] in selected_ids]

        return {
            "nodes": selected_nodes,
            "edges": selected_edges,
            "files": list(selected_files)
        }


class ContextFormatter:
    """Formateador de bloques Markdown explicables con anclas de línea."""

    @staticmethod
    def format(pruned_subgraph: Dict[str, Any], target_info: Dict[str, Any]) -> str:
        nodes = pruned_subgraph.get("nodes", [])
        edges = pruned_subgraph.get("edges", [])
        files = pruned_subgraph.get("files", [])

        target_file = target_info.get("file") or "N/A"
        target_symbol = target_info.get("symbol") or "N/A"

        callers = []
        callees = []
        imports = []

        for e in edges:
            rel = e.get("relation")
            src = e.get("source")
            tgt = e.get("target")
            if rel in ("calls", "indirect_call"):
                callers.append(f"{src} ➔ {tgt}")
            elif rel in ("imports", "imports_from"):
                imports.append(f"{src} ➔ {tgt}")

        nodes_str = []
        for n in nodes:
            lbl = n.get("label", "")
            sf = n.get("source_file", "")
            sl = n.get("source_location", "")
            anchor = f" [{sf}#{sl}]" if sf and sl else ""
            nodes_str.append(f"- **{lbl}**{anchor} (Prioridad {n.get('priority', 5)})")

        formatted_parts = [
            "### 🕸️ Graphify AST Subgraph Context",
            f"**Target File**: `{target_file}`",
            f"**Target Symbol**: `{target_symbol}`",
            "\n**Selected AST Symbols**:",
            "\n".join(nodes_str) if nodes_str else "- Ningún nodo específico",
            "\n**Direct Callers / Callees**:",
            "\n".join([f"- {c}" for c in callers[:5]]) if callers else "- Sin llamadas directas en subgrafo",
            "\n**Dependencies / Imports**:",
            "\n".join([f"- {i}" for i in imports[:5]]) if imports else "- Sin importaciones directas en subgrafo",
            f"\n**Affected Workspace Files**: {', '.join(files[:6]) if files else 'N/A'}"
        ]

        full_text = "\n".join(formatted_parts)

        # Truncado estricto por presupuesto de tokens (1500 max)
        max_chars = 1500 * 4
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n\n*(Subgrafo podado por límite de 1500 tokens)*"

        return full_text


class GraphContextEngine:
    """Motor principal modular de recuperación contextual guiado por grafo AST (SPEC-013)."""

    def __init__(self, graph_path: Optional[str] = None, max_tokens: int = 1500):
        self.graph_path = graph_path
        self.max_tokens = max_tokens
        self.cache_manager = GraphCacheManager.get_instance(graph_path)
        self.target_extractor = TargetExtractor(self.cache_manager)
        self.subgraph_retriever = SubgraphRetriever(self.cache_manager)
        self.context_budgeter = ContextBudgeter(max_tokens=max_tokens)
        self.context_formatter = ContextFormatter()

    def extract_target(self, user_goal: str) -> Dict[str, Any]:
        return self.target_extractor.extract(user_goal)

    def get_subgraph(self, target_symbol: Optional[str] = None, target_file: Optional[str] = None, depth: int = 1, task_type: str = "FEATURE") -> Dict[str, Any]:
        target_info = {"symbol": target_symbol, "file": target_file}
        return self.subgraph_retriever.retrieve(target_info, depth=depth, task_type=task_type)

    def rank_nodes(self, target_symbol: Optional[str] = None, target_file: Optional[str] = None) -> List[Dict[str, Any]]:
        subgraph = self.get_subgraph(target_symbol=target_symbol, target_file=target_file)
        pruned = self.context_budgeter.rank_and_prune(subgraph)
        return pruned.get("nodes", [])

    def build_context(self, user_goal: str, task_type: str = "FEATURE") -> str:
        """Construye el contexto acotado para AgentPipeline con fallback tolerante a fallos."""
        start_time = time.time()
        try:
            if not self.cache_manager.load():
                logging.info("[Graphify RAG] status=fallback reason=graph_file_missing")
                return "GRAFO AST GRAPHIFY: Subgrafo no disponible (archivo graphify-out/graph.json no encontrado), usando contexto de fallback."

            target_info = self.target_extractor.extract(user_goal)
            if not target_info.get("file") and not target_info.get("symbol"):
                logging.info(f"[Graphify RAG] status=fallback reason=target_not_found target='{user_goal[:40]}'")
                return f"GRAFO AST GRAPHIFY: status=fallback reason=target_not_found | Archivos de workspace activos."

            depth = 2 if task_type in ("REFACTOR", "DEBUG") else 1
            raw_subgraph = self.subgraph_retriever.retrieve(target_info, depth=depth, task_type=task_type)
            pruned_subgraph = self.context_budgeter.rank_and_prune(raw_subgraph)
            formatted = self.context_formatter.format(pruned_subgraph, target_info)

            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            nodes_cnt = len(pruned_subgraph.get("nodes", []))
            edges_cnt = len(pruned_subgraph.get("edges", []))
            files_cnt = len(pruned_subgraph.get("files", []))
            tokens_est = len(formatted) // 4

            logging.info(f"[Graphify RAG] status=success target='{target_info.get('symbol') or target_info.get('file')}' nodes={nodes_cnt} edges={edges_cnt} files={files_cnt} tokens={tokens_est} latency={elapsed_ms}ms")
            return formatted

        except Exception as e:
            logging.warning(f"[Graphify RAG] status=fallback reason=exception error='{e}'")
            return f"GRAFO AST GRAPHIFY: status=fallback reason=exception ({e}) | Usando contexto por defecto."
