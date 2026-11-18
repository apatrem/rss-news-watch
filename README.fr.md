# rss-news-watch

Un petit kit pour une **veille d'actualité quotidienne produite par une tâche LLM
planifiée** — Claude Cowork, ChatGPT Tasks, ou tout assistant capable de tourner
sur planning et de lire un fichier.

Les assistants hébergés ne peuvent pas récupérer la plupart des flux RSS de
journaux (listes de blocage internes, pour raisons de licences). Un petit script
tourne donc **sur ta machine** — pas de blocage — agrège tes flux dans un
`feeds-digest.md` local, et ta tâche planifiée lit ce fichier chaque matin. Aucun
contournement ; juste un fichier posé chez toi.

> 🇬🇧 English version: [README.md](README.md)

```
7h30 chaque jour           planificateur → run-briefing.sh → aggregate_feeds.py → digests/<stamp>.md (+ .json + .log)
chaque jour ou 2×/semaine  tâche LLM     → lit tous les digests non consommés, dédoublonne, te livre la veille, accuse réception
```

**v2** (voir le [CHANGELOG](CHANGELOG.md)) : digests horodatés conservés jusqu'à
leur lecture par la tâche, wrapper robuste (attente réseau, nouvelles tentatives,
fenêtre adaptative, purge sûre), hooks optionnels, archivage de l'historique — et
la veille peut tourner moins souvent que la collecte (ex. lundi et jeudi).

Voir [`docs/how-it-works.md`](docs/how-it-works.md) pour le détail.

> **Tu veux l'utiliser ?** Fork le repo (ou clone puis réinitialise git) pour en
> avoir *ta* copie — puis édite `feeds.txt`, les placeholders du prompt et le
> planning librement.

## Contenu

| Chemin | Rôle |
|--------|------|
| `aggregate_feeds.py` | L'agrégateur. Aucun chemin en dur ; portable. |
| `run-briefing.sh` | Wrapper quotidien : attente réseau, nouvelles tentatives, fenêtre adaptative, purge des digests consommés, hooks. |
| `hooks/post-digest.d/` | Compléments optionnels lancés après chaque digest (README + exemple). |
| `feeds.fr.example.txt` | Liste de flux FR/francophones (copier vers `feeds.txt`). |
| `feeds.en.example.txt` | Liste de flux EN/internationaux (copier vers `feeds.txt`). |
| `prompts/` | Le prompt de la tâche planifiée, FR + EN, avec guide d'installation. |
| `scheduler/` | macOS (launchd), Linux (cron/systemd), Windows (Task Scheduler). |
| `docs/how-it-works.md` | Pourquoi le digest local existe et comment tout s'enchaîne. |

## Démarrage rapide (exemple macOS)

```bash
# 1. Récupérer le code (fork d'abord, puis clone ton fork pour committer tes
#    propres réglages de feeds.txt ; ou clone celui-ci et réinitialise git)
git clone https://github.com/apatrem/rss-news-watch.git ~/bin/rss-news-watch
cd ~/bin/rss-news-watch

# 2. venv Python + dépendance (le Python macOS/Homebrew est « externally-managed »)
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt

# 3. Choisir une liste de flux
cp feeds.fr.example.txt feeds.txt      # ou feeds.en.example.txt

# 4. Premier test — écrit digests/<stamp>.md (+ .json/.log) et feeds-digest.md ici
./run-briefing.sh

# 5. Vérifier les logs et corriger toute URL en ERROR/EMPTY dans feeds.txt
cat feeds-digest.log; tail run-briefing.log
```

Puis planifie (lancement auto à 7h30 — garde-le quotidien même si la veille tourne moins souvent) :

```bash
sed "s|{{REPO_DIR}}|$HOME/bin/rss-news-watch|g" \
  scheduler/macos-launchd.plist.template \
  > ~/Library/LaunchAgents/com.rss-news-watch.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rss-news-watch.plist
# tester tout de suite, sans attendre 7h30 :
launchctl kickstart gui/$(id -u)/com.rss-news-watch
```

Linux / Windows : voir [`scheduler/`](scheduler/).

## Brancher la tâche LLM

Ouvre [`prompts/README.md`](prompts/README.md), renseigne `{{YOUR_NAME}}`,
`{{DIGEST_DIR}}` et `{{SCHEDULE}}` dans le prompt FR ou EN, et colle-le dans la
tâche planifiée de ton assistant (règle son planning là-bas : chaque jour, ou par
exemple lundi et jeudi). Le dossier connecté doit inclure le dépôt : la tâche lit
`digests/` et écrit son accusé de réception dans `state.json`.

## Personnaliser les flux

`feeds.txt` = une ligne `Nom | URL` ; les commentaires `#` et lignes vides sont
ignorés. Ajoute/retire librement, relance le script et vérifie
`feeds-digest.log` — chaque flux rapporte `OK`, `ERROR` ou `EMPTY`. Pour
resserrer la fenêtre : `--hours 24`.

## Notes

- Le Mac/PC doit être allumé à 7h30 pour que le planificateur déclenche ; s'il
  dort, le job se lance au réveil (launchd) ou au prochain créneau (systemd
  `Persistent`, Windows « exécuter si manqué »). Un jour entièrement manqué est
  rattrapé par la veille suivante, dans la limite de ce que portent encore les
  flux (la fenêtre s'élargit jusqu'à 10 jours).
- Maintenance : `./run-briefing.sh --dry-run` (ce qui serait purgé) et
  `--purge-only`.
- Un flux cassé ne bloque jamais les autres — il est simplement journalisé.
- `feeds.txt`, les digests, extras, logs, `state.json`, ton historique et ses
  archives, tes hooks personnels, cookies et clés sont git-ignorés : personnels
  ou régénérés, jamais partagés.

## Licence

[MIT](LICENSE).
