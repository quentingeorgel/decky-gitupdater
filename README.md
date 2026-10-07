# Decky Git Updater

> Un plugin [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) qui met à jour d'autres plugins Decky directement depuis leurs releases GitHub — sans attendre la mise à jour du store officiel.

Inspiré d'[Obtainium](https://github.com/ImranR98/Obtainium) sur Android.

---

## ✨ Fonctionnalités

- 📋 **Liste de dépôts au format texte** — un dépôt par ligne, simple à éditer
- 🔍 **Résolution des releases sans quota API** — utilise la redirection 302 de GitHub, aucune clé API nécessaire
- 📦 **Installation automatique** depuis les assets `.zip` des releases
- 🔔 **Détection des mises à jour** disponibles en un clic
- 🎯 **Tags épinglés** — verrouillez une version précise avec `owner/repo@v1.2.3`
- 🏷️ **Nom de dossier personnalisé** — utile quand le nom du repo diffère du nom du plugin avec `owner/repo#nom_dossier`
- 💬 **Commentaires** — toute ligne commençant par `#` est ignorée

---

## 📥 Installation

1. Téléchargez le dernier `decky-gitupdater.zip` depuis les [Releases](../../releases)
2. Sur le Steam Deck : **Decky Loader** → ⚙️ **Paramètres** → **Install Plugin from ZIP**
3. Sélectionnez le fichier téléchargé
4. Redémarrez Decky Loader si nécessaire

---

## 🚀 Utilisation

Ouvrez le panneau **Git Updater** depuis le menu Decky (icône 🎮 → onglet Decky).

### Format de la liste

Collez votre liste de dépôts dans la zone de texte, **une ligne par dépôt** :

```
# Commentaire (ligne ignorée)
owner/repo
owner/repo@v1.2.3
owner/repo#nom_dossier_local
owner/repo@v1.2.3#nom_dossier_local
```

### Syntaxe détaillée

| Format | Signification |
|---|---|
| `owner/repo` | Récupère la **dernière release** de ce dépôt |
| `owner/repo@v1.2.3` | **Épingle** le tag `v1.2.3` (aucune mise à jour automatique proposée tant que vous ne changez pas le tag) |
| `owner/repo#mon_plugin` | Force le nom du **dossier local** dans `~/homebrew/plugins/` |
| `owner/repo@v1.2.3#mon_plugin` | Combinaison des deux |

### Exemple concret

```
# Plugins Decky connus
SteamDeckHomebrew/decky-plugin-template

# Plugin avec nom de dossier différent du repo
someuser/decky-cool-plugin#CoolPlugin

# Version figée
anotheruser/decky-stable@v1.0.0
```

### Étapes

1. Collez votre liste
2. Cliquez **Sauvegarder & vérifier**
3. Les plugins avec une mise à jour disponible affichent un bouton **Mettre à jour → vX.Y.Z**
4. Cliquez dessus pour installer la nouvelle version

Le plugin compare la version locale (lue dans `~/homebrew/plugins/<nom>/plugin.json`) avec le tag distant.

---

## ⚠️ Avertissements de sécurité

**Ce plugin télécharge et installe du code depuis GitHub sans aucune vérification de signature.**

- ✅ N'ajoutez **que des dépôts de confiance** que vous pouvez inspecter
- ✅ Le plugin tourne avec les **privilèges root** de Decky Loader (flag `root` dans `plugin.json`) pour pouvoir écrire dans `~/homebrew/plugins/`
- ✅ Une mise à jour peut **casser** un plugin si la nouvelle version n'est pas compatible avec votre version de SteamOS ou de Decky Loader
- ✅ L'auteur du dépôt GitHub peut modifier son code à tout moment — ce que vous installez aujourd'hui n'est pas garanti identique demain

**Recommandation** : privilégiez les tags épinglés (`owner/repo@v1.2.3`) pour les plugins critiques, et vérifiez manuellement les changements avant de sauter de version.

---

## 🛠️ Développement

### Prérequis

- Node.js ≥ 20
- pnpm ≥ 9
- Git

### Cloner et builder

```bash
git clone https://github.com/<VOTRE_USER>/decky-gitupdater.git
cd decky-gitupdater
pnpm install
pnpm run build
```

### Générer un ZIP installable localement

```bash
./build.sh
```

Le ZIP est créé dans `dist-zip/decky-gitupdater.zip`. Installez-le via **Decky Loader → Paramètres → Install Plugin from ZIP**.

### Structure du projet

```
decky-gitupdater/
├── .github/workflows/
│   └── release.yml         # CI : build + release auto sur tag v*
├── src/
│   ├── index.tsx           # Frontend React (UI Decky)
│   └── types.d.ts
├── build.sh                # Script de build local
├── main.py                 # Backend Python (logique GitHub + install)
├── plugin.json             # Manifeste Decky
├── package.json
├── rollup.config.js
└── tsconfig.json
```

### Architecture

- **`main.py`** : backend Python exposé à l'UI via `@decky/api`. Gère la lecture/écriture des dépôts, la résolution des releases GitHub, le téléchargement et l'extraction des ZIP.
- **`src/index.tsx`** : frontend React utilisant `@decky/ui`. Affiche la liste des plugins, leur état, et les boutons de mise à jour.

---

## 📦 Publication d'une nouvelle version

```bash
git tag v0.1.1
git push origin v0.1.1
```

GitHub Actions va automatiquement :
1. Installer les dépendances
2. Builder le frontend
3. Créer `decky-gitupdater.zip`
4. Publier une release GitHub avec le ZIP attaché

Les utilisateurs peuvent ensuite mettre à jour via votre plugin lui-même (ajoutez `<VOTRE_USER>/decky-gitupdater` dans la liste).

---

## 🐛 Limitations connues

- **Scraping HTML** de la page de release pour trouver les assets `.zip` — si GitHub change son markup, ça casse. Une migration vers l'API GraphQL/JSON avec token serait plus robuste.
- **Pas de vérification de signature** — pas d'équivalent de la signature APK d'Obtainium sur SteamOS.
- **Un seul asset `.zip`** par release — le premier trouvé dans la page est utilisé.
- **Pas de notification système** — l'état des mises à jour est visible uniquement dans le panneau Decky.
- **Le flag `root` empêche la soumission au store officiel** — Decky refuse les plugins auto-update pour des raisons de sécurité.

---

## 🤝 Contribution

Les contributions sont bienvenues. Ouvrez une issue pour discuter d'une fonctionnalité ou d'un bug avant de soumettre une PR.

1. Fork le projet
2. Créez une branche (`git checkout -b feature/ma-feature`)
3. Committez (`git commit -m "Add: ma feature"`)
4. Pushez (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

---

## 📄 Licence

[MIT](LICENSE)

---

## 🙏 Remerciements

- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) — pour la plateforme et le template de plugin
- [Obtainium](https://github.com/ImranR98/Obtainium) — pour l'inspiration
- La communauté Steam Deck Homebrew
