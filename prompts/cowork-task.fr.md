---
name: veille-actu
description: Veille d'actualité à partir d'un digest RSS local — tech & IA, économie, politique, science, actu générale, agents IA de codage. Quotidienne ou quelques fois par semaine.
---

<!--
  MODÈLE À PERSONNALISER avant de le coller dans ta tâche planifiée.
  Remplace :
    {{YOUR_NAME}}   → ton prénom
    {{DIGEST_DIR}}  → chemin ABSOLU du dépôt, où run-briefing.sh écrit les digests,
                      ex. /Users/toi/bin/rss-news-watch
    {{SCHEDULE}}    → quand la tâche tourne, ex. « chaque matin » ou « le lundi et le jeudi matin »
  Ce dossier doit être accessible/connecté à ton assistant (Cowork, etc.).
  Garde run-briefing.sh planifié CHAQUE JOUR sur ta machine, quel que soit {{SCHEDULE}}.
-->

Prépare la veille d'actualité de {{YOUR_NAME}} ({{SCHEDULE}}), en français. Date du jour à récupérer via bash si besoin.

=== ÉTAPE 0 — QUELLE MATIÈRE EST DISPONIBLE ? (À FAIRE EN PREMIER) ===
Le digest RSS ne peut être produit QUE sur la machine de {{YOUR_NAME}} (accès réseau aux flux). Tu ne peux pas le régénérer. La machine produit un digest par jour ; la veille peut tourner moins souvent : trouver plusieurs digests non consommés est NORMAL.

  {{DIGEST_DIR}}/digests/AAAA-MM-JJ-HHMM.md / .json / .log   ← digests horodatés, conservés jusqu'à consommation
  {{DIGEST_DIR}}/extras/AAAA-MM-JJ-HHMM/                      ← matière optionnelle produite par des hooks (s'il y en a)
  {{DIGEST_DIR}}/feeds-digest.md                              ← copie du dernier run seulement
  {{DIGEST_DIR}}/state.json                                   ← last_briefing_ok = date du dernier briefing que TU as réellement produit
Le nettoyage est fait par run-briefing.sh, jamais par toi. Ne supprime RIEN dans ce dossier.

Via bash, dans cet ordre :
1. Lis state.json → `last_briefing_ok`. S'il est absent, prends la date la plus récente de news-watch-history.md.
2. Liste digests/*.md et retiens ceux dont l'horodatage est POSTÉRIEUR à last_briefing_ok : les digests NON CONSOMMÉS.
3. Choisis le mode :

  A. AUCUN digest non consommé, et le plus récent a plus de ~24 h
     → rien de neuf. Ne fais PAS la veille (pas de WebSearch, pas d'écriture dans l'historique, pas d'accusé). Affiche UNIQUEMENT :

     ---
     ⚠️ **Veille non lancée — aucun digest RSS non consommé** (le plus récent date du <date>).
     Le digest doit être régénéré sur ta machine (je n'ai pas accès réseau aux flux). Lance ceci dans un terminal, puis relance la veille :

     ```bash
     cd {{DIGEST_DIR}}
     ./run-briefing.sh
     ```
     ---

  B. AU MOINS 1 digest non consommé → VEILLE (cas normal). Suis la suite.

=== VEILLE SUR UN OU PLUSIEURS JOURS ===
Objectif : couvrir en UN briefing tout ce qui s'est passé depuis le précédent, sans noyer {{YOUR_NAME}}.
- Lis TOUS les digests non consommés, du plus ancien au plus récent. Ils sont gros (~200 ko) : procède par section avec grep/sed, ne charge jamais un fichier entier.
- DÉDOUBLONNE entre digests : une même URL sur deux jours = une puce. Un sujet qui a évolué sur plusieurs jours = UNE puce qui raconte l'état final, pas la chronologie.
- Volume : 2-3 puces par domaine pour un seul digest, 4-6 pour plusieurs.
- Regroupe par THÈME, jamais par jour. Titre : « Veille du <date du plus ancien digest non consommé> au <date du jour> » (une seule date pour un seul digest).
- PLAFOND 5 JOURS : au-delà, ne garde que ce qui a encore de la valeur aujourd'hui (décisions, chiffres, sorties de versions, sujets en cours) ; écarte les dépêches périmées et les « on saura demain » déjà tranchés. Signale-le en une ligne en tête.
- Si des jours n'ont aucun digest (machine éteinte), dis-le en fin de briefing : ils sont irrécupérables, les flux RSS ne les portent plus.
- Dans l'historique, chaque news garde SA date (celle du digest d'origine), pas la date du jour.

=== ENTRÉE PRIORITAIRE : LES DIGESTS LOCAUX ===
- Source principale pour les éditeurs que tu ne peux pas fetcher (Le Monde, Les Échos, Courrier international, Alternatives Économiques, The Economist, Politico, FT, Mediapart, Quanta, Ars Technica…).
- Le digest ne remplace pas ton jugement : sélectionne, vérifie, hiérarchise. WebSearch pour approfondir ou vérifier.
- Si extras/<stamp>/ existe, lis d'abord son fichier README ou STATUS : il peut contenir des textes intégraux ou des données produits par les hooks de {{YOUR_NAME}}. Attribue chaque fait au titre qui l'a effectivement rapporté.

=== DIVERSITÉ DES SOURCES (règle souple) ===
- À pertinence comparable, privilégie une source pas encore citée dans ce briefing.
- Évite de citer le même titre plus de ~2-3 fois, sauf si l'info le justifie vraiment.
- La pertinence prime : scoop ou traitement nettement meilleur → prends-le quand même.

=== SANTÉ DES FLUX ===
Lis les digests/<stamp>.log des digests consommés. Si une ligne porte « ERROR » ou « EMPTY », ajoute TOUT À LA FIN une courte section « ⚠️ Flux RSS en erreur » (flux + motif) et rappelle que l'URL se corrige dans feeds.txt. Sinon, n'écris rien à ce sujet.

=== ÉVITER LES RÉPÉTITIONS (AVANT et APRÈS) ===
Journal : {{DIGEST_DIR}}/news-watch-history.md (crée-le s'il manque).
1. AU DÉBUT : lis-le. Il liste les news déjà couvertes (date, titre court, URL).
2. SÉLECTION (souple) : n'écarte une info QUE si elle a déjà été rapportée à l'identique sans élément nouveau. Développement nouveau → « Suivi : ». En cas de doute → inclus.
3. À LA FIN : ajoute une ligne par news rapportée : « - [AAAA-MM-JJ] titre court — URL ». UNE ligne par news, jamais de bloc multi-lignes (le fichier est relu en entier à chaque run et doit rester greppable). Deux phrases autorisées quand tu as lu un texte intégral, pour garder les chiffres clés.
4. ARCHIVAGE (ne supprime jamais de ligne) : les lignes de plus de 30 jours sortent du journal et sont AJOUTÉES à archives/news-watch-history-AAAA-MM.md, selon le mois de LEUR date (crée-le avec un titre « # Archive de la veille — AAAA-MM »). Script python en lecture-écriture : écris d'abord l'archive, vérifie le nombre de lignes, puis seulement retire-les du journal. Ne lis jamais les archives pendant une veille.

=== ÉTAPE FINALE — ACCUSÉ DE RÉCEPTION (OBLIGATOIRE, mode B seulement) ===
C'est ce qui autorise run-briefing.sh à purger les digests consommés. Oublié : ils s'accumulent. Écrit à tort : de la matière non lue est perdue. À faire EN DERNIER, après l'écriture de l'historique ; si celle-ci a échoué, n'écris PAS l'accusé.

```bash
cd {{DIGEST_DIR}}
python3 - <<'PY'
import json, os, datetime as dt, tempfile
p = "state.json"
d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
now = dt.datetime.now().replace(microsecond=0).isoformat()
d["last_briefing_window"] = {"from": d.get("last_briefing_ok", ""), "to": now}
d["last_briefing_ok"] = now
fd, tmp = tempfile.mkstemp(dir=".")
with os.fdopen(fd, "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2); fh.write("\n")
os.replace(tmp, p)
print("ack:", now)
PY
```

=== CONTENU ===
Domaines : 1. Tech & IA  2. Économie  3. Politique (France + international)  4. Science  5. Actualité générale  6. Agents IA de codage (section dédiée).

Complète au besoin par WebSearch ; tu peux aussi fetcher directement ces flux tech ouverts : Techmeme (https://www.techmeme.com/feed.xml), Ars Technica (https://feeds.arstechnica.com/arstechnica/index), Next (https://next.ink/feed), Blog du Modérateur (https://www.blogdumoderateur.com/feed).

SECTION « AGENTS IA DE CODAGE » :
(a) Sorties et mises à jour de modèles et d'outils de codage agentique sur la période couverte (Claude, OpenAI, Gemini, Mistral, DeepSeek, Qwen… / Claude Code, Codex, Cursor, Copilot, Windsurf, Cline, Aider…) : version, date, nouveautés ; vérifie via les changelogs officiels.
(b) Incidents de sécurité touchant ces outils (extensions ou paquets malveillants, fuites), avec ce qu'il faut vérifier.
(c) Outils, skills et astuces pratiques, toujours avec le lien. Rien de neuf → 1-2 références durables plutôt qu'inventer.

Note paywall : pour les titres payants, utilise le titre et le chapô du digest et vérifie via une source ouverte. Ne rapporte jamais un fait invérifiable ; signale les faits issus du seul chapô.

Vérifie faits, dates, chiffres, versions, noms.

Format (dans le chat ; seuls le journal, les archives et state.json sont des fichiers) :
- Titre « Veille du … au … ».
- « L'essentiel » : 5-7 lignes en tête (plusieurs digests) ou 3 lignes (un seul).
- Une section par domaine, « Agents IA de codage » à part. Puces : fait clé + précision courte + source liée ; préfixe « Suivi : » si besoin.
- « À surveiller » : échéances datées des jours suivants repérées dans la matière.
- « Sources » en fin, puis « ⚠️ Flux RSS en erreur » seulement si nécessaire.

Concis et factuel. Si un domaine n'a rien (après dédoublonnage souple), une ligne plutôt qu'inventer.
