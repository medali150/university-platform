import pandas as pd

# Create teacher template with correct department name
data = {
    'nom': ['Benali', 'Mansouri', 'Khelifi'],
    'prenom': ['Ahmed', 'Fatima', 'Karim'],
    'email': [
        'ahmed.benali@university.com',
        'fatima.mansouri@university.com',
        'karim.khelifi@university.com'
    ],
    'departement_nom': [
        "Technologie d'Informatique",
        "Technologie d'Informatique",
        "Technologie d'Informatique"
    ],
    'password': ['Teacher123', 'Teacher123', 'Teacher123']
}

df = pd.DataFrame(data)
df.to_excel('teachers_template_FINAL.xlsx', index=False)
print('Teacher template updated successfully with department: Technologie d\'Informatique')
