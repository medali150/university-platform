# 📊 Guide d'Importation en Masse (Bulk Import)

## Fichiers Excel Créés

### ✅ Fichiers Disponibles

1. **`students_import_template.xlsx`** - Template pour importer des étudiants
2. **`teachers_import_template.xlsx`** - Template pour importer des enseignants

---

## 📋 Structure des Fichiers

### Students Template

**Feuilles incluses:**
- **Students** - Données des étudiants à importer
- **Available Groups** - Liste de tous les groupes disponibles
- **Instructions** - Guide d'utilisation

**Colonnes requises:**
| Colonne | Description | Obligatoire | Exemple |
|---------|-------------|-------------|---------|
| `nom` | Nom de famille | ✅ Oui | Khalil |
| `prenom` | Prénom | ✅ Oui | Sarah |
| `email` | Email unique | ✅ Oui | sarah.khalil@student.com |
| `groupe_nom` | Nom du groupe (doit exister) | ✅ Oui | L3 GL Groupe 1 |
| `password` | Mot de passe | ⚠️ Optionnel | Student123 (défaut) |

### Teachers Template

**Feuilles incluses:**
- **Teachers** - Données des enseignants à importer
- **Available Departments** - Liste de tous les départements disponibles
- **Instructions** - Guide d'utilisation

**Colonnes requises:**
| Colonne | Description | Obligatoire | Exemple |
|---------|-------------|-------------|---------|
| `nom` | Nom de famille | ✅ Oui | Ben Ali |
| `prenom` | Prénom | ✅ Oui | Ahmed |
| `email` | Email unique | ✅ Oui | ahmed.benali@university.com |
| `departement_nom` | Nom du département (doit exister) | ✅ Oui | technologie d'Informatique |
| `password` | Mot de passe | ⚠️ Optionnel | Teacher123 (défaut) |

---

## 🚀 Comment Utiliser

### Méthode 1: Via l'Interface Admin Panel (Recommandé)

1. **Ouvrir le fichier Excel**
   - Ouvrez `students_import_template.xlsx` ou `teachers_import_template.xlsx`

2. **Vérifier les valeurs valides**
   - Consultez la feuille "Available Groups" ou "Available Departments"
   - Les noms doivent correspondre **exactement** (sensible à la casse)

3. **Remplir les données**
   - Modifiez les données dans la feuille principale
   - Ne modifiez PAS les en-têtes de colonnes
   - Assurez-vous que les emails sont uniques

4. **Sauvegarder le fichier**

5. **Importer via Admin Panel**
   - Connectez-vous au Admin Panel
   - Allez à "Bulk Import"
   - Sélectionnez le fichier Excel
   - Cliquez sur "Importer"

### Méthode 2: Via API (Avancé)

```bash
# Pour les étudiants
curl -X POST "http://localhost:8000/admin/bulk-import/students" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@students_import_template.xlsx"

# Pour les enseignants
curl -X POST "http://localhost:8000/admin/bulk-import/teachers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@teachers_import_template.xlsx"
```

---

## ⚠️ Points Importants

### ✅ À Faire

- ✅ Vérifier que les groupes/départements existent avant l'import
- ✅ Utiliser des emails uniques pour chaque utilisateur
- ✅ Respecter exactement les noms de groupes/départements (sensible à la casse)
- ✅ Garder les en-têtes de colonnes intacts
- ✅ Sauvegarder le fichier au format .xlsx ou .xls

### ❌ À Éviter

- ❌ Modifier les noms des colonnes
- ❌ Utiliser des emails déjà existants
- ❌ Utiliser des groupes/départements qui n'existent pas
- ❌ Laisser des champs obligatoires vides
- ❌ Sauvegarder dans un autre format (CSV, TXT, etc.)

---

## 📋 Groupes Actuellement Disponibles

```
✅ L3 GL Groupe 1 (Licence 3 - Génie Logiciel)
✅ L3 GL Groupe 2 (Licence 3 - Génie Logiciel)
✅ M1 IA Groupe 1 (Master 1 - Intelligence Artificielle)
```

## 📋 Départements Actuellement Disponibles

```
✅ technologie d'Informatique
✅ génie mécanique
✅ génie électrique
✅ génie cevil
```

---

## 🔍 Résolution des Problèmes

### Erreur: "Group not found"
**Solution:** Vérifiez que le nom du groupe correspond exactement à ceux listés dans la feuille "Available Groups"

### Erreur: "Email already exists"
**Solution:** L'email est déjà utilisé par un autre utilisateur. Utilisez un email différent.

### Erreur: "Missing required columns"
**Solution:** Assurez-vous que toutes les colonnes requises sont présentes et correctement nommées.

### Erreur: "Failed to read Excel file"
**Solution:** 
- Vérifiez que le fichier est au format .xlsx ou .xls
- Assurez-vous que le fichier n'est pas corrompu
- Essayez de le ré-enregistrer avec Excel

---

## 📊 Exemple de Résultat d'Import

```json
{
  "success": true,
  "message": "Import completed. Created: 5, Skipped: 0",
  "details": {
    "total": 5,
    "created": 5,
    "skipped": 0,
    "errors": []
  }
}
```

---

## 🔄 Regénérer les Templates

Pour regénérer les templates avec les données actuelles de la base:

```bash
cd api
python create_excel_templates.py
```

---

## 📞 Support

Pour toute question ou problème:
- Consultez les logs du backend pour plus de détails
- Vérifiez la feuille "Instructions" dans le fichier Excel
- Contactez l'administrateur système

---

**Dernière mise à jour:** 2 Décembre 2025
