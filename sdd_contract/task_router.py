"""
Task Router for classifying user prompts into task types.
"""
import re
from typing import Dict, Any

from .task_types import TaskType, TaskClassification
from .task_contract import (
    ChatTaskContract, ActionTaskContract, 
    FeatureTaskContract, RecoveryTaskContract
)


class TaskRouter:
    """Classifies incoming prompts into task types."""
    
    # Keywords for each task type
    CHAT_KEYWORDS = {
        "hola", "hi", "hello", "saludos", "buenas", "ayuda", "ayudame",
        "explica", "explicame", "describe", "dime", "cual es", "que es",
        "como funciona", "cual es la", "que significa", "puede explicar",
        "me puedes ayudar", "por favor", "gracias", "buen dia", "buenas tardes"
    }
    
    ACTION_KEYWORDS = {
        "crea", "crear", "escribe", "escribir", "modifica", "modificar",
        "borra", "borrar", "elimina", "eliminar", "mueve", "mover",
        "renombra", "renombrar", "lee", "leer", "ejecuta", "ejecutar",
        "corre", "correr", "compila", "compilar", "build", "buildea",
        "instala", "instalar", "actualiza", "actualizar", "fix", "arregla"
    }
    
    FEATURE_KEYWORDS = {
        "implementa", "implementar", "construye", "construir", "agrega",
        "agregar", "añade", "añadir", "desarrolla", "desarrollar",
        "crea un sistema", "crear un sistema", "haz un", "crear un",
        "desarrollar un sistema", "agregar funcionalidad",
        "soporte para", "capacidad para"
    }
    
    RECOVERY_KEYWORDS = {
        "recupera", "recuperar", "arregla", "arreglar", "restaura",
        "restaurar", "emergencia", "emergente", "roto", "rota", "roto",
        "fallado", "falla", "error critico", "error grave",
        "sistema no funciona", "no funciona", "crash", "crasheo"
    }
    
    def classify(self, prompt: str, context: Dict[str, Any] = None) -> TaskClassification:
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
    
    def _extract_indicators(self, prompt: str) -> Dict[str, Any]:
        """
        Extract classification indicators from prompt.
        
        Returns:
            Dictionary of indicator names and values
        """
        prompt_lower = prompt.lower()
        
        indicators = {
            "has_conversation_words": any(
                kw in prompt_lower for kw in self.CHAT_KEYWORDS
            ),
            "has_action_keywords": any(
                kw in prompt_lower for kw in self.ACTION_KEYWORDS
            ),
            "has_feature_keywords": any(
                kw in prompt_lower for kw in self.FEATURE_KEYWORDS
            ),
            "has_recovery_keywords": any(
                kw in prompt_lower for kw in self.RECOVERY_KEYWORDS
            ),
            "has_ui_keywords": any(
                kw in prompt_lower for kw in {"ui", "interface", "ventana", "window", "pantalla"}
            ),
            "prompt_length": len(prompt),
            "word_count": len(prompt.split())
        }
        
        return indicators
    
    def _apply_decision_rules(self, indicators: Dict[str, Any]) -> TaskType:
        """
        Apply decision rules to determine task type.
        
        Returns:
            The determined TaskType
        """
        # Priority order: RECOVERY > FEATURE > ACTION > CHAT
        # RECOVERY: Recovery keywords present
        if indicators.get("has_recovery_keywords", False):
            return TaskType.RECOVERY
        
        # FEATURE: Feature keywords present, not just single action
        has_feature = indicators.get("has_feature_keywords", False)
        has_action = indicators.get("has_action_keywords", False)
        has_conversation = indicators.get("has_conversation_words", False)
        
        if has_feature and not (has_action and not has_conversation):
            return TaskType.FEATURE
        
        # ACTION: Single action keywords, no feature scope
        if has_action and not has_conversation:
            return TaskType.ACTION
        
        # CHAT: Conversation keywords, no actions
        if has_conversation and not has_action:
            return TaskType.CHAT
        
        # Default: Default to FEATURE for ambiguous cases
        return TaskType.FEATURE
    
    def _calculate_confidence(self, indicators: Dict[str, Any], task_type: TaskType) -> float:
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
    
    def _generate_classification_reason(self, indicators: Dict[str, Any], task_type: TaskType) -> str:
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
        
        elif task_type == TaskType.RECOVERY:
            if indicators.get("has_recovery_keywords"):
                reasons.append("recovery keywords detected")
        
        reasons.append(f"confidence: {indicators.get('has_conversation_words', False)}")
        
        return "; ".join(reasons) if reasons else "default classification"
