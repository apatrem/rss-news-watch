---
name: veille-quotidienne-8h
description: Veille d'actualité quotidienne à 8h00 : tech & IA, économie, politique, science, actu générale, avec sources prioritaires.
---

<!--
  MODÈLE À PERSONNALISER avant de le coller dans ta tâche planifiée.
  Remplace :
    {{YOUR_NAME}}   → ton prénom
    {{DIGEST_DIR}}  → le dossier où aggregate_feeds.py écrit le digest,
                      ex. /Users/toi/bin/rss-news-watch  (chemin ABSOLU)
  Ce dossier doit être accessible/connecté à ton assistant (Cowork, etc.).
-->

Prépare une veille d'actualité quotidienne pour {{YOUR_NAME}}, en français. Date du jour à récupérer via bash si besoin.

=== ENTRÉE PRIORITAIRE : DIGEST RSS LOCAL ===
Un script sur la machine de {{YOUR_NAME}} agrège ses flux RSS (y compris les journaux que tu ne peux pas fetcher) et écrit un digest local. AVANT de chercher sur le web, lis :
{{DIGEST_DIR}}/feeds-digest.md
(version structurée : feeds-digest.json dans le même dossier)
- S'il existe : source principale pour les éditeurs (Le Monde, Mediapart, Les Échos, Courrier International, Alternatives Économiques, The Economist, Politico, FT, Rest of World, JDN, Usine Digitale, Usine Nouvelle, Quanta, CNRS, Scientific American, Ars Technica).
- Vérifie sa fraîcheur (en-tête « RSS Digest — <date> »). S'il a plus de ~24h ou est absent, signale-le en une ligne et bascule sur WebSearch.
- Le digest ne remplace pas ton jugement : sélectionne, vérifie, hiérarchise. Pour approfondir un titre, tu peux le WebSearcher.

=== DIVERSITÉ DES SOURCES (règle souple) ===
Vise la variété des sources dans le briefing, sans rigidité :
- À pertinence comparable, privilégie une source encore NON citée dans ce briefing plutôt que d'en reprendre une déjà utilisée.
- Évite de citer la même marque (ex. « Le Monde », « Les Échos ») plus de ~2 fois sur l'ensemble du briefing, sauf si l'info le justifie vraiment.
- Sur un même sujet couvert par plusieurs sources, alterne les origines d'un jour à l'autre plutôt que de revenir toujours à la même.
- EXCEPTION : la pertinence prime. S'il s'agit d'un scoop, d'une info exclusive ou nettement mieux traitée par une source déjà citée, prends-la quand même — la diversité est une préférence, pas un plafond dur.
Note : Le Monde tend à ressortir partout car c'est la seule source généraliste FR couvrant les 5 domaines ; compense en puisant activement dans les sources plus spécialisées (Les Échos/Alt. Éco pour l'éco, Politico pour la politique UE, Quanta/CNRS pour la science, etc.).

=== SANTÉ DES FLUX (à signaler) ===
Lis aussi : {{DIGEST_DIR}}/feeds-digest.log
Repère toute ligne « ERROR » ou « EMPTY ». S'il y en a, ajoute TOUT À LA FIN une courte section « ⚠️ Flux RSS en erreur » : nom du flux + motif (ex. « ERROR HTTP 403 », « EMPTY »), et rappelle que {{YOUR_NAME}} peut corriger l'URL dans feeds.txt du même dossier. Si aucun flux en erreur, n'écris rien à ce sujet.

=== ÉVITER LES RÉPÉTITIONS (AVANT et APRÈS la veille) ===
Journal persistant : {{DIGEST_DIR}}/historique-veille.md
- Crée le dossier/fichier si absent (mkdir -p). Si le chemin n'est pas accessible en écriture, crée un sous-dossier dédié dans le dossier connecté disponible ; signale en fin de veille où il a été écrit.
1. AU DÉBUT : lis le journal. Il liste les news déjà couvertes (date, titre court, URL).
2. SÉLECTION : règle SOUPLE, en cas de doute privilégie l'inclusion.
   - Écarte une info SEULEMENT si déjà rapportée à l'identique ET sans élément nouveau.
   - Développement nouveau sur un sujet déjà traité → inclus en « Suivi : » avec ce qui est nouveau.
   - Neuf → inclus. Quasi-doublon ambigu → INCLUS (éventuellement « Suivi : »).
3. À LA FIN : append (sans écraser) une entrée datée « - [AAAA-MM-JJ] titre court — URL » par news rapportée. Élague > 30 jours.

=== CONTENU DE LA VEILLE ===
Domaines : 1. Tech & IA  2. Économie  3. Politique (France + international)  4. Science  5. Actualité générale  6. Agents IA de codage (section dédiée).

Le digest local couvre la plupart des sources. Complète au besoin par WebSearch, et fetche directement ces flux tech si utile : Techmeme (https://www.techmeme.com/feed.xml), Ars Technica (https://feeds.arstechnica.com/arstechnica/index), Next (https://next.ink/feed), Sifted (https://sifted.eu/feed), Blog du Modérateur (https://www.blogdumoderateur.com/feed).

SECTION « AGENTS IA DE CODAGE » — chaque jour :
(a) Sorties/MAJ de modèles et outils de codage agentique (24-48h) : modèles/versions (Claude, OpenAI, Gemini, Mistral, DeepSeek, Qwen…) et outils (Claude Code, Cursor, Copilot, Windsurf, Cline, Aider, Devin…). Version, date, nouveautés ; vérifie via blogs/changelogs officiels. Techmeme = bonne porte d'entrée.
(b) Outils, « skills », astuces pratiques pour développeurs avec agents IA, avec lien direct. Sources : GitHub Trending, Hacker News, dépôts de skills/agents, blogs officiels. Toujours le lien. Rien de neuf → 1-2 ressources de référence durables plutôt qu'inventer.

Note paywall : Mediapart, Les Échos, The Economist, FT, Next, Sifted, Alt. Économiques sont payants. Si contenu complet inaccessible, utilise titre/chapô (le digest les fournit) et vérifie via une source ouverte. Ne rapporte jamais un fait invérifiable.

Par domaine : 2-3 infos marquantes, vérifiées, non déjà rapportées. Vérifie faits, dates, chiffres, versions, noms.

Format (dans le chat ; seuls le journal et le digest sont des fichiers) :
- Titre avec la date du jour.
- Une section par domaine (titre court en gras), « Agents IA de codage » distincte.
- 2-3 puces/section : fait clé + courte précision, source liée. Préfixe « Suivi : » les développements déjà traités.
- Section « Sources » en fin.
- Puis, SI ET SEULEMENT SI des flux sont en erreur, la section « ⚠️ Flux RSS en erreur ».

Concis et factuel. Si un domaine n'a rien (après dédoublonnage souple), une ligne plutôt qu'inventer.
