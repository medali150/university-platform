# University App - Application Next.js avec Firebase Auth + Firestore

Cette application Next.js utilise TypeScript, Firebase Authentication et Firestore Database pour gérer la connexion et les données des utilisateurs.

## Structure du projet

```
apps/web/
├── app/
│   ├── globals.css              # Styles globaux
│   ├── layout.tsx              # Layout principal
│   ├── page.tsx                # Page d'accueil (protégée)
│   ├── login/
│   │   └── page.tsx            # Page de connexion
│   ├── register/
│   │   └── page.tsx            # Page d'inscription simple
│   └── register-complete/
│       └── page.tsx            # Page d'inscription complète
├── contexts/
│   └── AuthContext.tsx         # Contexte d'authentification
├── lib/
│   ├── firebase.ts             # Configuration Firebase
│   └── userService.ts          # Service pour gérer les profils utilisateurs
├── .env.local                  # Variables d'environnement
├── next.config.js              # Configuration Next.js
├── package.json                # Dépendances
└── tsconfig.json              # Configuration TypeScript
```

## Configuration Firebase dans la Console

### 1. Activer Authentication
1. Allez sur [Firebase Console](https://console.firebase.google.com/)
2. Sélectionnez votre projet `universety-79411`
3. Dans le menu de gauche, cliquez sur **Authentication**
4. Cliquez sur **Get Started** si ce n'est pas fait
5. Dans l'onglet **Sign-in method**, activez **Email/Password**

### 2. Activer Firestore Database
1. Dans le menu de gauche, cliquez sur **Firestore Database**
2. Cliquez sur **Create database**
3. Choisissez **Start in test mode** (pour commencer)
4. Sélectionnez une région (par exemple `europe-west`)

### 3. Ajouter des utilisateurs

#### Option A: Via la Console Firebase
1. Allez dans **Authentication > Users**
2. Cliquez sur **Add user**
3. Entrez email et mot de passe

#### Option B: Via l'application (Recommandé)
Utilisez les pages d'inscription de l'application :
- `/register` - Inscription simple (email/mot de passe)
- `/register-complete` - Inscription complète (avec nom, prénom, rôle)

## Types d'utilisateurs

L'application supporte 3 rôles :
- **Student** (Étudiant) - par défaut
- **Teacher** (Enseignant)
- **Admin** (Administrateur)

## Structure des données dans Firestore

Les profils utilisateurs sont stockés dans la collection `users` :

```json
{
  "uid": "firebase-user-id",
  "email": "user@example.com",
  "firstName": "Jean",
  "lastName": "Dupont",
  "role": "student",
  "createdAt": "2025-09-24T...",
  "updatedAt": "2025-09-24T..."
}
```

## Installation et Lancement

```bash
cd apps/web
npm install
npm run dev
```

## Pages disponibles

- **`/`** - Page d'accueil (protégée) - affiche le profil utilisateur
- **`/login`** - Page de connexion
- **`/register`** - Inscription simple
- **`/register-complete`** - Inscription complète avec profil
- **`/admin/login`** - 🔐 Connexion administrateur
- **`/admin/dashboard`** - 🔐 Dashboard administrateur (protégé)
- **`/test-api`** - Page de test pour l'API

## Exemples de données de test

Vous pouvez créer ces utilisateurs de test via `/register-complete` :

```
1. Étudiant:
   - Email: etudiant@test.com
   - Mot de passe: test123
   - Nom: Martin Dupont
   - Rôle: Étudiant

2. Enseignant:
   - Email: prof@test.com
   - Mot de passe: test123
   - Nom: Marie Dubois
   - Rôle: Enseignant

3. Administrateur:
   - Email: admin@test.com
   - Mot de passe: admin123
   - Nom: Admin Système
   - Rôle: Administrateur
   - ⚠️ Accès à la zone admin : /admin/login
```

## 🔐 Section Administrateur

### Accès Admin
- **Page de connexion** : `/admin/login`
- **Dashboard** : `/admin/dashboard` 
- **API Admin** : `/api/admin/check`

### Comptes Admin autorisés
- `admin@test.com`
- `admin@universety.com` 
- `admin@universety-79411.com`

### Fonctionnalités Admin
✅ **Dashboard sécurisé** avec statistiques  
✅ **Gestion des rôles** (admin, teacher, student)  
✅ **Test des APIs** intégré  
✅ **Création d'utilisateurs** via interface admin  
✅ **Protection des routes** par rôle  

Pour plus de détails, consultez `ADMIN_GUIDE.md`

## Fonctionnalités

✅ **Authentification Firebase** (email/mot de passe)  
✅ **Base de données Firestore** pour les profils utilisateurs  
✅ **Inscription complète** avec informations personnelles  
✅ **Gestion des rôles** (étudiant, enseignant, administrateur)  
✅ **Protection des routes** par authentification et rôle  
✅ **Zone Administrateur** sécurisée avec dashboard  
✅ **API REST** `/api/me` avec authentification token  
✅ **API Admin** `/api/admin/check` pour vérification des droits  
✅ **Affichage du profil** complet sur la page d'accueil  
✅ **Interface de test** pour les APIs  

## Technologies utilisées

- **Next.js 14** : Framework React
- **TypeScript** : Typage statique
- **Firebase Authentication** : Gestion de l'authentification
- **Firestore Database** : Base de données NoSQL
- **React Context** : Gestion de l'état d'authentification