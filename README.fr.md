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
7h45  planificateur → aggregate_feeds.py → feeds-digest.md (+ .json + .log)
8h00  tâche LLM      → lit le digest, dédoublonne via l'historique, te livre la veille
```

Voir [`docs/how-it-works.md`](docs/how-it-works.md) pour le détail.

## Contenu

| Chemin | Rôle |
|--------|------|
| `aggregate_feeds.py` | L'agrégateur. Aucun chemin en dur ; portable. |
| `feeds.fr.example.txt` | Liste de flux FR/francophones (copier vers `feeds.txt`). |
| `feeds.en.example.txt` | Liste de flux EN/internationaux (copier vers `feeds.txt`). |
| `prompts/` | Le prompt de la tâche planifiée, FR + EN, avec guide d'installation. |
| `scheduler/` | macOS (launchd), Linux (cron/systemd), Windows (Task Scheduler). |
| `docs/how-it-works.md` | Pourquoi le digest local existe et comment tout s'enchaîne. |

## Démarrage rapide (exemple macOS)

```bash
# 1. Récupérer le code
git clone https://github.com/apatrem/rss-news-watch.git ~/bin/rss-news-watch
cd ~/bin/rss-news-watch

# 2. venv Python + dépendance (le Python macOS/Homebrew est « externally-managed »)
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt

# 3. Choisir une liste de flux
cp feeds.fr.example.txt feeds.txt      # ou feeds.en.example.txt

# 4. Premier test — écrit feeds-digest.md / .json / .log ici
./venv/bin/python aggregate_feeds.py

# 5. Vérifier le log et corriger toute URL en ERROR/EMPTY dans feeds.txt
cat feeds-digest.log
```

Puis planifie (lancement auto à 7h45) :

```bash
sed "s|{{REPO_DIR}}|$HOME/bin/rss-news-watch|g" \
  scheduler/macos-launchd.plist.template \
  > ~/Library/LaunchAgents/com.rss-news-watch.plist
launchctl load ~/Library/LaunchAgents/com.rss-news-watch.plist
# tester tout de suite, sans attendre 7h45 :
launchctl start com.rss-news-watch
```

Linux / Windows : voir [`scheduler/`](scheduler/).

## Brancher la tâche LLM

Ouvre [`prompts/README.md`](prompts/README.md), renseigne `{{YOUR_NAME}}` et
`{{DIGEST_DIR}}` dans le prompt FR ou EN, et colle-le dans la tâche planifiée de
ton assistant (règle le planning 8h00 là-bas). Le dossier connecté doit inclure
le repo pour que la tâche puisse lire `feeds-digest.md`.

## Personnaliser les flux

`feeds.txt` = une ligne `Nom | URL` ; les commentaires `#` et lignes vides sont
ignorés. Ajoute/retire librement, relance le script et vérifie
`feeds-digest.log` — chaque flux rapporte `OK`, `ERROR` ou `EMPTY`. Pour
resserrer la fenêtre : `--hours 24`.

## Notes

- Le Mac/PC doit être allumé à 7h45 pour que le planificateur déclenche ; s'il
  dort, le job se lance au réveil (launchd) ou au prochain créneau (systemd
  `Persistent`, Windows « exécuter si manqué »).
- Un flux cassé ne bloque jamais les autres — il est simplement journalisé.
- `feeds.txt`, les digests, logs et ton historique de dédoublonnage sont
  git-ignorés : personnels ou régénérés, non partagés.

## Licence

[MIT](LICENSE).
