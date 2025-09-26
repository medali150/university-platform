# 🔐 Guide d'Administration - University App

## Vue d'ensemble

L'application dispose maintenant d'une section administrative complète avec authentification sécurisée et gestion des rôles.

## 🏗️ Structure Admin

```
apps/web/
├── app/admin/
│   ├── page.tsx                 # Page d'accueil admin (redirection)
│   ├── login/
│   │   └── page.tsx            # Connexion administrateur
│   └── dashboard/
│       └── page.tsx            # Dashboard administrateur
├── app/api/admin/
│   └── check/
│       └── route.ts            # API de vérification des droits admin
├── hooks/
│   └── useAdmin.ts             # Hook pour la gestion des rôles admin
└── ADMIN_GUIDE.md              # Ce guide
```

## 🚀 Accès à la section Admin

### URLs principales :
- **Login Admin :** `http://localhost:3000/admin/login`
- **Dashboard Admin :** `http://localhost:3000/admin/dashboard`
- **API Admin :** `http://localhost:3000/api/admin/check`

### Depuis l'application :
1. **Page d'accueil** → Bouton "🔐 Zone Admin"
2. **Page de connexion** → Lien "🔐 Connexion Administrateur"
3. **URL directe** → `/admin`

## 👤 Comptes Administrateur

### Création d'un compte admin :

1. **Via inscription complète** :
   - Aller à `/register-complete`
   - Choisir le rôle "Administrateur"
   - Remplir les informations

2. **Comptes de test recommandés** :
   ```
   Email: admin@test.com
   Mot de passe: admin123
   Nom: Admin Système
   Rôle: Administrateur
   ```

3. **Emails autorisés par défaut** :
   - `admin@test.com`
   - `admin@universety.com`
   - `admin@universety-79411.com`

## 🔒 Vérification des Droits

### Méthodes de vérification :

1. **Par profil Firestore** : Vérification du champ `role: 'admin'`
2. **Par email autorisé** : Liste des emails administrateur
3. **Fallback sécurisé** : Si Firestore n'est pas disponible

### Hook `useAdmin` :
```typescript
const { adminUser, isAdmin, loading, role } = useAdmin();

if (isAdmin) {
  // Utilisateur admin
}
```

## 🎛️ Fonctionnalités du Dashboard Admin

### Informations affichées :
- ✅ **Profil admin** : Nom, email, UID, rôle
- ✅ **Statistiques** : Nombre d'utilisateurs par rôle (simulé)
- ✅ **Test API** : Intégration avec `/api/me`
- ✅ **Actions** : Création d'utilisateurs, tests

### Actions disponibles :
- 🧪 **Tester API /api/me** : Test direct depuis le dashboard
- 📊 **Page de test complète** : Redirection vers `/test-api`
- 👥 **Créer un utilisateur** : Redirection vers `/register-complete`

## 🛡️ Sécurité

### Protection des routes :
```typescript
useEffect(() => {
  if (!loading && !isAdmin) {
    router.push('/admin/login');
  }
}, [isAdmin, loading, router]);
```

### Vérifications multiples :
1. **Client-side** : Hook `useAdmin` pour l'UI
2. **API-side** : Vérification du token Firebase
3. **Role-based** : Contrôle par rôle Firestore

## 🧪 Tests Admin

### Test d'accès :

1. **Connexion normale** :
   ```bash
   curl -X GET http://localhost:3000/admin/login
   ```

2. **Test API admin** :
   ```bash
   curl -X GET http://localhost:3000/api/admin/check \
     -H "Authorization: Bearer VOTRE_TOKEN" \
     -H "Content-Type: application/json"
   ```

3. **Via interface web** :
   - Connectez-vous sur `/admin/login`
   - Testez le dashboard sur `/admin/dashboard`

### Réponse API admin attendue :
```json
{
  "ok": true,
  "message": "Droits administrateur vérifiés",
  "admin": true,
  "permissions": [
    "read:users",
    "write:users", 
    "delete:users",
    "read:analytics",
    "admin:dashboard"
  ],
  "timestamp": "2025-09-24T15:30:45.123Z",
  "environment": "development"
}
```

## 🔧 Configuration

### Variables d'environnement :
- Utilise la même config Firebase que l'app principale
- Pas de configuration supplémentaire requise

### Personnalisation des admins :
```typescript
// Dans useAdmin.ts et AdminLoginPage.tsx
const adminEmails = [
  'admin@test.com',
  'admin@universety.com',
  'votre-email-admin@domain.com'
];
```

## 🚨 Dépannage

### Problème : "Accès refusé"
1. Vérifiez que votre compte a le rôle "admin" dans Firestore
2. Vérifiez que votre email est dans la liste des admins autorisés
3. Reconnectez-vous pour actualiser les permissions

### Problème : "Cet email n'a pas les droits administrateur"
- Ajoutez votre email à la liste `adminEmails` dans `AdminLoginPage.tsx`

### Problème : Dashboard non accessible
- Vérifiez votre connexion internet
- Vérifiez que l'app Next.js fonctionne sur `localhost:3000`
- Consultez la console du navigateur pour les erreurs

## 🎯 Prochaines étapes

1. **Créez un compte admin** via `/register-complete`
2. **Testez la connexion** sur `/admin/login`  
3. **Explorez le dashboard** sur `/admin/dashboard`
4. **Testez l'API admin** avec le token récupéré
5. **Personnalisez** selon vos besoins

---

## 📞 Support

- **Interface de test** : `/test-api`
- **Documentation API** : `TEST_API.md`
- **Console navigateur** : F12 pour les logs détaillés