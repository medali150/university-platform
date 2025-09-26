# Guide de Dépannage - Erreur lors de la création du compte

## 🔍 Diagnostic des Erreurs

### Étape 1: Vérifier la configuration Firebase

1. **Allez sur [Firebase Console](https://console.firebase.google.com/)**
2. **Sélectionnez votre projet `universety-79411`**

### Étape 2: Vérifier Authentication

1. **Menu gauche → Authentication**
2. **Onglet "Sign-in method"**
3. **Vérifiez que "Email/Password" est ACTIVÉ** ✅

### Étape 3: Configurer Firestore (si vous voulez la version complète)

1. **Menu gauche → Firestore Database**
2. **Si pas encore créé → "Create database"**
3. **Choisir "Start in test mode"** (permet lectures/écritures pendant 30 jours)
4. **Sélectionner une région** (ex: europe-west)

## 🧪 Tests à effectuer

### Test 1: Inscription simple (sans Firestore)
- Aller à `http://localhost:3000/register-simple`
- Cette version n'utilise que Firebase Auth (pas de base de données)

### Test 2: Inscription complète (avec Firestore)
- Aller à `http://localhost:3000/register-complete`
- Cette version sauvegarde le profil dans Firestore

### Test 3: Connexion avec compte existant
- Aller à `http://localhost:3000/login`
- Tester avec un compte créé dans Firebase Console

## 🔧 Solutions aux erreurs courantes

### Erreur: "operation-not-allowed"
**Solution:** Email/Password pas activé dans Firebase Console
- Authentication → Sign-in method → Email/Password → Enable

### Erreur: "Missing or insufficient permissions"
**Solution:** Règles Firestore trop restrictives
- Firestore Database → Rules → Remplacer par:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### Erreur: "weak-password"
**Solution:** Mot de passe trop court
- Utilisez au moins 6 caractères

### Erreur: "invalid-email"
**Solution:** Format email invalide
- Vérifiez le format: exemple@domain.com

### Erreur de réseau
**Solution:** Problème de connexion
- Vérifiez votre connexion internet
- Vérifiez que Firebase n'est pas bloqué par un firewall

## 📧 Comptes de test

Créez ces comptes pour tester :

```
Email: test@example.com
Mot de passe: test123456
Prénom: Test
Nom: User
```

## 🛠️ Commandes de dépannage

```bash
# Redémarrer l'application
cd apps/web
npm run dev

# Vérifier les logs dans la console du navigateur
# F12 → Console → Rechercher les erreurs Firebase
```

## 📱 Pages disponibles pour tester

- `/login` - Connexion
- `/register-simple` - Inscription basique (Firebase Auth seulement)
- `/register-complete` - Inscription complète (Firebase Auth + Firestore)
- `/` - Page d'accueil (après connexion)

## 🚨 Si rien ne fonctionne

1. **Vérifiez la console du navigateur** (F12 → Console)
2. **Copiez le message d'erreur exact**
3. **Vérifiez que votre projet Firebase existe et est accessible**
4. **Essayez de créer un utilisateur directement dans Firebase Console**