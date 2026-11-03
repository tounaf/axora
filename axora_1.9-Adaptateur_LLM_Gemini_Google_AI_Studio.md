# Axora — Adaptateur LLM Google Gemini & Google AI Studio (Tokens Gratuits)

**Version :** 1.9
**Statut :** Documentation technique et guide de configuration de l'API Google Gemini
**Composants :** `src/axora/llm/provider.py` (`GeminiLLMAdapter`), `src/axora/config.py`

---

## 1. Pourquoi l'Adaptateur Google Gemini (Google AI Studio) ?

Google AI Studio propose un accès direct et gratuit aux modèles multimodaux de dernière génération de Google :
- `gemini-1.5-flash` : Vitesse d'exécution ultra-rapide, fenêtre de contexte massive (1 million de tokens) et raisonnement structuré de pointe.
- `gemini-2.0-flash` : Dernière génération avec prise en charge native des appels d'outils et latence réduite.
- `gemini-1.5-pro` : Raisonnement complexe et analyse approfondie.

Google AI Studio fournit un point d'accès compatible OpenAI (`https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`), ce qui permet une intégration native et performante dans la boucle décisionnelle d'Axora.

---

## 2. Procédure d'Obtention d'une Clé API Google AI Studio Gratuite

1. Rendez-vous sur le portail officiel de Google AI Studio : [https://aistudio.google.com/](https://aistudio.google.com/)
2. Connectez-vous avec votre compte Google.
3. Cliquez sur le bouton bleu **"Get API key"** dans le menu de gauche.
4. Cliquez sur **"Create API key"** (dans un projet Google Cloud existant ou un nouveau projet gratuit).
5. Copiez votre clé API commençant par `AIzaSy...`.

---

## 3. Configuration dans Axora (`.env`)

Ajoutez ou modifiez les variables suivantes dans votre fichier `.env` :

```env
# Sélection du Fournisseur LLM Gemini
LLM_PROVIDER=gemini

# Clé API Google AI Studio
GEMINI_API_KEY=AIzaSy_votre_cle_api_ici

# URL Endpoint compatible OpenAI de Google AI Studio
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai

# Modèle Gemini recommandé (Gratuit & Ultra-rapide)
GEMINI_MODEL=gemini-1.5-flash
```

---

## 4. Test et Vérification

### 4.1 Lancer le CLI Axora avec Gemini

```bash
PYTHONPATH=src python3 -m axora.cli
```

Vous devriez observer le bandeau suivant :
```text
============================================================
   AXORA INTERACTIVE CLI — From intent to action.
============================================================
[*] Loaded Provider: gemini
[*] Loaded Model:    gemini-1.5-flash
[*] Semantic Model:  gestion_paroissiale (v0.2)
[*] Registered Tools: ['discover_model', 'query_data', 'create_record', 'update_record']
------------------------------------------------------------
```

### 4.2 Lancer l'API FastAPI et le Dashboard Web

```bash
# Démarrer le serveur API & Dashboard
PYTHONPATH=src uvicorn axora.main:app --host 0.0.0.0 --port 8000
```

Accédez ensuite à l'interface graphique :
- **Dashboard Web interactif** : [http://localhost:8000/ui](http://localhost:8000/ui)
- **Frontend Next.js** : [http://localhost:3000](http://localhost:3000)

---

*Documentation générée pour Axora v1.9.*
