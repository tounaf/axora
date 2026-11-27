# Axora — Adaptateur LLM Local Ollama & Llama 3

**Version :** 1.10  
**Statut :** Documentation technique et guide d'utilisation de l'adaptateur local Ollama (Llama 3)  
**Composants :** `src/axora/llm/provider.py` (`OllamaLLMAdapter`), `src/axora/config.py`

---

## 1. Pourquoi l'Adaptateur Local Ollama ?

[Ollama](https://ollama.com/) permet d'exécuter des modèles de langage open-source directement sur votre machine locale (CPU / GPU) sans aucune dépendance réseau externe ni coût de consommation d'API :

- **Confidentialité totale :** Aucune donnée métier ni invite ne quitte votre machine.
- **Zéro coût de token :** Exécution illimitée en local.
- **Compatibilité standard :** Ollama expose un point d'accès compatible OpenAI (`http://localhost:11434/v1/chat/completions`).
- **Support de Llama 3 :** Prise en charge native de `llama3:latest` (8B) ou versions dérivées avec sorties JSON structurées et appels d'outils.

---

## 2. Prérequis & Installation d'Ollama

### 2.1 Télécharger et installer Ollama

Sur Linux :
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2.2 Télécharger le modèle Llama 3

Téléchargez le modèle Llama 3 (8B) :
```bash
ollama run llama3
```

Vérifiez que le modèle est bien présent :
```bash
ollama list
```
Sortie attendue :
```text
NAME             ID              SIZE      MODIFIED
llama3:latest    365c0bd3c000    4.7 GB    ...
```

---

## 3. Configuration dans Axora (`.env`)

Pour utiliser Ollama avec Axora, configurez les variables d'environnement suivantes dans votre fichier `.env` :

```env
# Sélection du Fournisseur LLM Ollama
LLM_PROVIDER=ollama

# Point d'accès local Ollama (compatible OpenAI)
OLLAMA_BASE_URL=http://localhost:11434/v1

# Modèle Ollama local cible
OLLAMA_MODEL=llama3:latest

# Clé API optionnelle (Ollama n'exige pas d'authentification par défaut)
OLLAMA_API_KEY=ollama
```

---

## 4. Architecture et Fonctionnement

La classe `OllamaLLMAdapter` implémente le protocole `LLMAdapter` d'Axora :

```text
[Prompt Utilisateur] 
         │
         ▼
[Agent Loop / Runtime] 
         │
         ▼
[OllamaLLMAdapter]
         │ (HTTP POST JSON vers http://localhost:11434/v1/chat/completions)
         ▼
[Ollama Daemon (Llama 3 Local)]
         │
         ▼ (Retour JSON ou Tool Calls)
[parse_agent_decision_from_json]
         │
         ▼
[AgentDecision: call_tool | final_answer | ask_user]
```

### Fonctionnalités clés :
- **Prise en charge de Llama 3 sans erreur 400 :** Dans Ollama, le modèle `llama3:latest` (Llama 3.0) ne supporte pas le paramètre API OpenAI `tools` (qui lève une erreur `400 does not support tools`). Axora injecte dynamiquement la description complète et le schéma des outils disponibles directement dans le prompt système (`Available tools: ...`).
- **Format JSON strict (`response_format: {"type": "json_object"}`) :** Force Llama 3 à produire un schéma JSON valide pour `AgentDecision` (`call_tool` ou `final_answer`).
- **Détection des Tool Calls :** Supporte aussi bien les `tool_calls` au format function-calling que la sérialisation JSON directe.
- **Repli automatique sécurisé (*Fail-safe*) :** En cas d'indisponibilité ou d'arrêt du daemon Ollama local, l'adaptateur bascule automatiquement sur `MockLLMAdapter` pour préserver la continuité de service des tests ou du développement.

---

## 5. Vérification & Tests

### 5.1 Lancer les tests automatisés

```bash
PYTHONPATH=src pytest tests/test_llm_adapter.py -k ollama -v
```

Tous les tests unitaires et le test live (si Ollama tourne en local) sont validés :
```text
tests/test_llm_adapter.py::test_get_llm_adapter_factory_ollama PASSED
tests/test_llm_adapter.py::test_ollama_llm_adapter_custom_model PASSED
tests/test_llm_adapter.py::test_ollama_llm_adapter_unreachable_fallback PASSED
tests/test_llm_adapter.py::test_ollama_llm_adapter_mock_http_tool_call PASSED
tests/test_llm_adapter.py::test_ollama_llm_adapter_mock_http_json_content PASSED
tests/test_llm_adapter.py::test_ollama_llm_adapter_error_logging PASSED
tests/test_llm_adapter.py::test_ollama_llm_adapter_live_call PASSED
```

### 5.2 Lancer le CLI Axora avec Ollama

```bash
LLM_PROVIDER=ollama PYTHONPATH=src python3 -m axora.cli
```

Le CLI affichera :
```text
============================================================
   AXORA INTERACTIVE CLI — From intent to action.
============================================================
[*] Loaded Provider: ollama
[*] Loaded Model:    llama3:latest
[*] Semantic Model:  gestion_paroissiale (v0.2)
[*] Registered Tools: ['discover_model', 'query_data', 'create_record', 'update_record']
------------------------------------------------------------
```

### 5.3 Lancer l'API FastAPI et le Dashboard Web

```bash
LLM_PROVIDER=ollama PYTHONPATH=src uvicorn axora.main:app --host 0.0.0.0 --port 8000
```

---

**Axora — From intent to action.**
