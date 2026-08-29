"""
Task Router for classifying user prompts into task types.
"""
import unicodedata
from typing import Any

from .task_types import TaskClassification, TaskType


def strip_accents(text: str) -> str:
    """Normalize diacritics / accents from text while preserving original text."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class TaskRouter:
    """Classifies incoming prompts into task types."""

    CHAT_KEYWORDS = {
        strip_accents(kw) for kw in {
            "hola", "hi", "hello", "saludos", "buenas", "ayuda", "ayudame",
            "explica", "explicame", "describe", "dime", "cual es", "que es",
            "como funciona", "cual es la", "que significa", "puede explicar",
            "me puedes ayudar", "por favor", "gracias", "buen dia", "buenas tardes",
            "responde unicamente", "solo responde", "contesta", "responder", "decirme"
        }
    }

    ACTION_KEYWORDS = {
        strip_accents(kw) for kw in {
            "crea", "crear", "escribe", "escribir", "modifica", "modificar",
            "borra", "borrar", "elimina", "eliminar", "mueve", "mover",
            "renombra", "renombrar", "lee", "leer", "ejecuta", "ejecutar",
            "corre", "correr", "compila", "compilar", "build", "buildea",
            "instala", "instalar", "actualiza", "actualizar", "fix", "arregla",
            "añade", "añadir", "agrega", "agregar", "inserta", "insertar",
            "comentario", "cambia", "cambiar", "ejecutalo", "ejecutala"
        }
    }

    FEATURE_KEYWORDS = {
        strip_accents(kw) for kw in {
            "implementa", "implementar", "construye", "construir",
            "desarrolla", "desarrollar", "crea un sistema", "crear un sistema",
            "desarrollar un sistema", "agregar funcionalidad", "soporte para",
            "capacidad para", "nuevo sistema", "sistema para", "plataforma para",
            "aplicacion para", "aplicacion", "aplicacion web", "sistema web",
            "api para", "microservicio", "arquitectura", "endpoint", "feature"
        }
    }

    RECOVERY_KEYWORDS = {
        strip_accents(kw) for kw in {
            "recupera", "recuperar", "arregla", "arreglar", "restaura",
            "restaurar", "emergencia", "emergente", "roto", "rota", "fallado",
            "falla", "error critico", "error grave", "sistema no funciona",
            "no funciona", "crash", "crasheo", "refactoriza", "refactorizar",
            "warnings", "linter warnings", "warning"
        }
    }

    def classify(self, prompt: str, context: dict[str, Any] = None) -> TaskClassification:
        """
        Classify a user prompt into a task type.

        Args:
            prompt: The user's input prompt
            context: Additional context about the session

        Returns:
            TaskClassification with type, confidence, and reasoning

        Raises:
            ValueError: If classification confidence is too low
        """
        context = context or {}

        # Extract indicators from prompt
        indicators = self._extract_indicators(prompt)

        # Apply decision rules
        task_type = self._apply_decision_rules(indicators)

        # Calculate confidence
        confidence = self._calculate_confidence(indicators, task_type)

        # Generate reason
        reason = self._generate_classification_reason(indicators, task_type)

        return TaskClassification(
            task_type=task_type,
            confidence=confidence,
            classification_reason=reason,
            metadata=indicators
        )

    def _extract_indicators(self, prompt: str) -> dict[str, Any]:
        """
        Extract classification indicators from prompt with accent normalization and negative action detection.

        Returns:
            Dictionary of indicator names and values
        """
        prompt_normalized = strip_accents(prompt.lower())

        # Prohibiciones primarias sobre creación/modificación/ejecución general
        primary_negative_phrases = (
            "sin modificar", "sin tocar", "sin crear", "no modifiques",
            "no crees nada", "no crees archivos", "no crees ningun archivo",
            "no abras terminal", "sin herramientas", "no ejecutes ninguna herramienta",
            "no ejecutes herramientas", "no ejecutes ningun comando", "no ejecutes comandos",
            "no crees, modifiques", "no hagas nada"
        )

        # Prohibiciones secundarias acotadas exclusivamente a verificadores (pytest, unittest, ruff, ast)
        secondary_verifier_phrases = (
            "no ejecutes pytest", "no ejecutes unittest", "no ejecutes ruff",
            "no ejecutes ast", "no ejecutes analisis ast", "no ejecutes tests",
            "no ejecutes pruebas", "no hagas replanificacion", "sin pytest",
            "sin unittest", "sin ruff", "sin ast", "sin tests", "sin pruebas"
        )

        has_primary_negatives = any(neg in prompt_normalized for neg in primary_negative_phrases)

        # Buscar si el prompt solicita explícitamente acciones primarias positivas (p. ej. "crea action_final.py", "ejecuta python")
        has_positive_action_keywords = any(kw in prompt_normalized for kw in self.ACTION_KEYWORDS)
        has_positive_feature_keywords = any(kw in prompt_normalized for kw in self.FEATURE_KEYWORDS)
        has_positive_recovery_keywords = any(kw in prompt_normalized for kw in self.RECOVERY_KEYWORDS)

        # Una acción primaria es válida si hay palabras clave de acción y no hay prohibición primaria global
        has_action = (has_positive_action_keywords and not has_primary_negatives) or (
            has_positive_action_keywords and any(k in prompt_normalized for k in ("ejecuta python", "crea unicamente", "crea el archivo", "ejecutalo"))
        )

        has_conversation = (
            any(kw in prompt_normalized for kw in self.CHAT_KEYWORDS) or has_primary_negatives
        ) and not (has_action or has_positive_feature_keywords)

        indicators = {
            "has_conversation_words": has_conversation,
            "has_action_keywords": has_action,
            "has_feature_keywords": has_positive_feature_keywords,
            "has_recovery_keywords": has_positive_recovery_keywords,
            "has_ui_keywords": any(
                kw in prompt_normalized for kw in {"ui", "interface", "ventana", "window", "pantalla"}
            ),
            "has_negative_actions": has_primary_negatives,
            "prompt_length": len(prompt),
            "word_count": len(prompt.split())
        }

        return indicators

    def _apply_decision_rules(self, indicators: dict[str, Any]) -> TaskType:
        """
        Apply decision rules to determine task type.

        Returns:
            The determined TaskType
        """
        has_feature = indicators.get("has_feature_keywords", False)
        has_action = indicators.get("has_action_keywords", False)
        has_conversation = indicators.get("has_conversation_words", False)
        has_recovery = indicators.get("has_recovery_keywords", False)

        if has_recovery:
            return TaskType.RECOVERY

        if has_feature:
            return TaskType.FEATURE

        if has_action:
            return TaskType.ACTION

        if has_conversation:
            return TaskType.CHAT

        # Default to CHAT if no action or feature keywords exist
        return TaskType.CHAT

    def _calculate_confidence(self, indicators: dict[str, Any], task_type: TaskType) -> float:
        """
        Calculate confidence score for classification.

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Boost confidence for clear indicators
        if task_type == TaskType.CHAT:
            if indicators.get("has_conversation_words"):
                confidence += 0.3
            if not indicators.get("has_action_keywords"):
                confidence += 0.2

        elif task_type == TaskType.ACTION:
            if indicators.get("has_action_keywords"):
                confidence += 0.3
            if not indicators.get("has_feature_keywords"):
                confidence += 0.2

        elif task_type == TaskType.FEATURE:
            if indicators.get("has_feature_keywords"):
                confidence += 0.3
            if not indicators.get("has_recovery_keywords"):
                confidence += 0.2

        elif task_type == TaskType.RECOVERY:
            if indicators.get("has_recovery_keywords"):
                confidence += 0.3

        # Reduce confidence for ambiguous cases
        has_multiple_indicators = sum([
            indicators.get("has_conversation_words", False),
            indicators.get("has_action_keywords", False),
            indicators.get("has_feature_keywords", False),
            indicators.get("has_recovery_keywords", False)
        ]) > 1

        if has_multiple_indicators:
            confidence -= 0.1

        return min(max(confidence, 0.1), 0.95)

    def _generate_classification_reason(self, indicators: dict[str, Any], task_type: TaskType) -> str:
        """
        Generate human-readable reason for classification.

        Returns:
            Reason string explaining the classification
        """
        reasons = []

        if task_type == TaskType.CHAT:
            if indicators.get("has_conversation_words"):
                reasons.append("conversational keywords detected")

        elif task_type == TaskType.ACTION:
            if indicators.get("has_action_keywords"):
                reasons.append("action keywords detected")
            if not indicators.get("has_feature_keywords"):
                reasons.append("no feature scope detected")

        elif task_type == TaskType.FEATURE:
            if indicators.get("has_feature_keywords"):
                reasons.append("feature implementation keywords detected")

        elif task_type == TaskType.RECOVERY and indicators.get("has_recovery_keywords"):
            reasons.append("recovery keywords detected")

        reasons.append(f"confidence: {indicators.get('has_conversation_words', False)}")

        return "; ".join(reasons) if reasons else "default classification"
