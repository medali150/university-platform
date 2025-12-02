"""
Create Excel template files for bulk import
"""
import asyncio
import pandas as pd
from prisma import Prisma
from pathlib import Path

async def create_templates():
    db = Prisma()
    await db.connect()
    
    print("📊 Creating Excel Templates...")
    print("="*60)
    
    try:
        # Get groups from database
        groups = await db.groupe.find_many(
            include={
                "niveau": {
                    "include": {
                        "specialite": True
                    }
                }
            }
        )
        
        # Get departments from database
        departments = await db.departement.find_many()
        
        print(f"\n✅ Found {len(groups)} groups")
        print(f"✅ Found {len(departments)} departments")
        
        # Create Students Template
        print("\n📝 Creating students_import_template.xlsx...")
        
        # Use real group names
        group_names = [g.nom for g in groups[:5]] if groups else ['L3 GL Groupe 1']
        while len(group_names) < 5:
            group_names.append(group_names[0])
        
        students_data = {
            'nom': ['Khalil', 'Mansour', 'Jebali', 'Saidi', 'Bouaziz'],
            'prenom': ['Sarah', 'Ali', 'Amira', 'Mohamed', 'Yasmine'],
            'email': [
                'test.student1@student.com',
                'test.student2@student.com',
                'test.student3@student.com',
                'test.student4@student.com',
                'test.student5@student.com'
            ],
            'groupe_nom': group_names,
            'password': ['Student123', 'Student123', 'Student123', 'Student123', 'Student123']
        }
        
        students_df = pd.DataFrame(students_data)
        
        # Create help sheet with available groups
        if groups:
            groups_help_data = {
                'Nom du Groupe': [g.nom for g in groups],
                'Niveau': [g.niveau.nom if g.niveau else 'N/A' for g in groups],
                'Spécialité': [g.niveau.specialite.nom if g.niveau and g.niveau.specialite else 'N/A' for g in groups]
            }
            groups_help_df = pd.DataFrame(groups_help_data)
        
        # Save students template
        students_file = Path('students_import_template.xlsx')
        with pd.ExcelWriter(students_file, engine='openpyxl') as writer:
            students_df.to_excel(writer, index=False, sheet_name='Students')
            if groups:
                groups_help_df.to_excel(writer, index=False, sheet_name='Available Groups')
                
                # Add instructions sheet
                instructions_data = {
                    'Instructions': [
                        '1. Fill in student information in the "Students" sheet',
                        '2. nom: Student last name (Required)',
                        '3. prenom: Student first name (Required)',
                        '4. email: Student email address (Required, must be unique)',
                        '5. groupe_nom: Group name - MUST match exactly from "Available Groups" sheet (Required)',
                        '6. password: Student password (Optional, default: Student123)',
                        '',
                        'Important:',
                        '- Check the "Available Groups" sheet for valid group names',
                        '- Group names are case-sensitive and must match exactly',
                        '- Emails must be unique across all users',
                        '- Do not modify column headers'
                    ]
                }
                instructions_df = pd.DataFrame(instructions_data)
                instructions_df.to_excel(writer, index=False, sheet_name='Instructions')
        
        print(f"  ✅ Created: {students_file.absolute()}")
        
        # Create Teachers Template
        print("\n📝 Creating teachers_import_template.xlsx...")
        
        # Use real department names
        dept_names = [d.nom for d in departments[:3]] if departments else ['Informatique']
        while len(dept_names) < 3:
            dept_names.append(dept_names[0])
        
        teachers_data = {
            'nom': ['Ben Ali', 'Trabelsi', 'Gharbi'],
            'prenom': ['Ahmed', 'Fatma', 'Karim'],
            'email': [
                'test.teacher1@university.com',
                'test.teacher2@university.com',
                'test.teacher3@university.com'
            ],
            'departement_nom': dept_names,
            'password': ['Teacher123', 'Teacher123', 'Teacher123']
        }
        
        teachers_df = pd.DataFrame(teachers_data)
        
        # Create help sheet with available departments
        if departments:
            dept_help_data = {
                'Nom du Département': [d.nom for d in departments]
            }
            dept_help_df = pd.DataFrame(dept_help_data)
        
        # Save teachers template
        teachers_file = Path('teachers_import_template.xlsx')
        with pd.ExcelWriter(teachers_file, engine='openpyxl') as writer:
            teachers_df.to_excel(writer, index=False, sheet_name='Teachers')
            if departments:
                dept_help_df.to_excel(writer, index=False, sheet_name='Available Departments')
                
                # Add instructions sheet
                instructions_data = {
                    'Instructions': [
                        '1. Fill in teacher information in the "Teachers" sheet',
                        '2. nom: Teacher last name (Required)',
                        '3. prenom: Teacher first name (Required)',
                        '4. email: Teacher email address (Required, must be unique)',
                        '5. departement_nom: Department name - MUST match exactly from "Available Departments" sheet (Required)',
                        '6. password: Teacher password (Optional, default: Teacher123)',
                        '',
                        'Important:',
                        '- Check the "Available Departments" sheet for valid department names',
                        '- Department names are case-sensitive and must match exactly',
                        '- Emails must be unique across all users',
                        '- Do not modify column headers'
                    ]
                }
                instructions_df = pd.DataFrame(instructions_data)
                instructions_df.to_excel(writer, index=False, sheet_name='Instructions')
        
        print(f"  ✅ Created: {teachers_file.absolute()}")
        
        print("\n" + "="*60)
        print("✅ Excel templates created successfully!")
        print("\n📋 Available Groups:")
        for group in groups:
            spec = group.niveau.specialite.nom if group.niveau and group.niveau.specialite else 'N/A'
            niveau = group.niveau.nom if group.niveau else 'N/A'
            print(f"  - {group.nom} ({niveau} - {spec})")
        
        print("\n📋 Available Departments:")
        for dept in departments:
            print(f"  - {dept.nom}")
        
        print("\n💡 Usage:")
        print("  1. Open the Excel file")
        print("  2. Check the 'Available Groups/Departments' sheet for valid values")
        print("  3. Fill in the data in the main sheet")
        print("  4. Upload via Admin Panel > Bulk Import")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(create_templates())
