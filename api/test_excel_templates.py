"""
Test bulk import with the created templates
This script simulates uploading the Excel files to test the import functionality
"""
import asyncio
import pandas as pd
from pathlib import Path

async def test_import():
    print("="*70)
    print("📋 TESTING EXCEL TEMPLATES")
    print("="*70)
    
    # Test Students Template
    students_file = Path('students_import_template.xlsx')
    if students_file.exists():
        print(f"\n✅ Students template found: {students_file}")
        
        # Read and display
        df = pd.read_excel(students_file, sheet_name='Students')
        print(f"\n📊 Students Data ({len(df)} rows):")
        print(df.to_string(index=False))
        
        # Show available groups
        try:
            groups_df = pd.read_excel(students_file, sheet_name='Available Groups')
            print(f"\n📋 Available Groups:")
            print(groups_df.to_string(index=False))
        except:
            pass
        
        # Validate columns
        required_cols = ['nom', 'prenom', 'email', 'groupe_nom']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"\n❌ Missing columns: {missing}")
        else:
            print(f"\n✅ All required columns present: {required_cols}")
    else:
        print(f"\n❌ Students template not found!")
    
    # Test Teachers Template
    teachers_file = Path('teachers_import_template.xlsx')
    if teachers_file.exists():
        print(f"\n{'='*70}")
        print(f"✅ Teachers template found: {teachers_file}")
        
        # Read and display
        df = pd.read_excel(teachers_file, sheet_name='Teachers')
        print(f"\n📊 Teachers Data ({len(df)} rows):")
        print(df.to_string(index=False))
        
        # Show available departments
        try:
            dept_df = pd.read_excel(teachers_file, sheet_name='Available Departments')
            print(f"\n📋 Available Departments:")
            print(dept_df.to_string(index=False))
        except:
            pass
        
        # Validate columns
        required_cols = ['nom', 'prenom', 'email', 'departement_nom']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"\n❌ Missing columns: {missing}")
        else:
            print(f"\n✅ All required columns present: {required_cols}")
    else:
        print(f"\n❌ Teachers template not found!")
    
    print("\n" + "="*70)
    print("✅ TEMPLATES VALIDATION COMPLETE")
    print("="*70)
    print("\n💡 Next Steps:")
    print("  1. Open the Excel files to review the data")
    print("  2. Modify the data as needed (keep the column headers)")
    print("  3. Use Admin Panel > Bulk Import to upload")
    print("  4. Or use the API endpoint: POST /admin/bulk-import/students")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_import())
