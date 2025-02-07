# Application web "Travel Order Resolver"

## 📌 Introduction

Ce projet est une application web permettant de rechercher des trajets de train, soit par la saisie classique, soit par la voix via un prompt interactif. Il est développé avec React, TypeScript, Vite et TailwindCSS.

## 🚀 Technologies utilisées

- **React** (Framework Frontend)
- **TypeScript** (Typage statique pour JavaScript)
- **Vite** (Bundler et serveur de développement rapide)
- **TailwindCSS** (Framework CSS)
- **ESLint** (Outil d'analyse statique du code)

## 📂 Structure du projet

```
web/
├── src/                   # Dossier source du projet
│   ├── components/        # Composants React
│   │   ├── RouteInput.tsx
│   │   ├── RouteDisplay.tsx
│   │   ├── ui/            # Composants UI réutilisables
│   │       ├── ...
│   ├── hooks/             # Hooks personnalisés
│   ├── pages/             # Pages principales du projet
│   ├── lib/               # Fonctions utilitaires
│   ├── App.tsx            # Composant racine de l'application
│   ├── main.tsx           # Point d'entrée principal
│   ├── index.css          # Styles globaux
├── package.json           # Dépendances et scripts du projet
├── tsconfig.json          # Configuration TypeScript
├── vite.config.ts         # Configuration de Vite
├── tailwind.config.ts     # Configuration de TailwindCSS
├── eslint.config.js       # Configuration ESLint
├── postcss.config.js      # Configuration PostCSS
├── README.md              # Documentation du projet
```

## 📥 Installation

### 1️⃣ Prérequis

- **Node.js** (Dernière version recommandée)
- **npm** ou **yarn**

### 2️⃣ Installation des dépendances

```sh
npm install
# ou
yarn install
```

## 🏃 Lancement du projet

Pour exécuter l'application en mode développement :

```sh
npm run dev
# ou
yarn dev
```

L'application sera accessible via `http://localhost:5173/` (ou un autre port indiqué par Vite).

## ⚙️ Développement

### 📌 Composants

Le projet est structuré avec des **composants réutilisables** situés dans `src/components/`. Certains composants d'UI sont déjà disponibles pour une utilisation simplifiée.

### 📌 Pages

Les pages principales de l'application sont situées dans `src/pages/`, avec un point d'entrée défini dans `Index.tsx`.

### 📌 Hooks personnalisés

Les **hooks** personnalisés sont regroupés dans `src/hooks/`. Exemples :
- `use-mobile.tsx` : Détection des appareils mobiles.
- `use-toast.ts` : Gestion des notifications toast.

## 🚀 Déploiement

Pour builder l'application :

```sh
npm run build
# ou
yarn build
```

Les fichiers de production seront générés dans le dossier `dist/`.
