#!/usr/bin/env python3
"""
Script to add sample groups, subjects (matières), and specialities to the database
"""
import asyncio
from prisma import Prisma

async def add_sample_data():
    """Add comprehensive sample data for testing"""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🏗️ Adding sample data to the database...")
        
        # First, get existing departments
        print("\n1️⃣ Checking existing departments...")
        departments = await prisma.departement.find_many()
        print(f"   Found {len(departments)} departments:")
        for dept in departments:
            print(f"   • {dept.nom} (ID: {dept.id})")
        
        if not departments:
            print("   ❌ No departments found! Please create departments first.")
            return
        
        informatique_dept = next((d for d in departments if "Informatique" in d.nom), departments[0])
        print(f"   ✅ Using department: {informatique_dept.nom}")
        
        # 2. Add more specialities
        print("\n2️⃣ Adding specialities...")
        specialities_to_add = [
            {"nom": "Intelligence Artificielle", "id_departement": informatique_dept.id},
            {"nom": "Cybersécurité", "id_departement": informatique_dept.id},
            {"nom": "Développement Web", "id_departement": informatique_dept.id},
            {"nom": "Systèmes Embarqués", "id_departement": informatique_dept.id}
        ]
        
        created_specialities = []
        for spec_data in specialities_to_add:
            # Check if speciality already exists
            existing = await prisma.specialite.find_first(
                where={
                    "nom": spec_data["nom"],
                    "id_departement": spec_data["id_departement"]
                }
            )
            
            if existing:
                print(f"   ⚠️ Spécialité '{spec_data['nom']}' already exists")
                created_specialities.append(existing)
            else:
                speciality = await prisma.specialite.create(data=spec_data)
                print(f"   ✅ Created speciality: {speciality.nom}")
                created_specialities.append(speciality)
        
        # Get all specialities (existing + new)
        all_specialities = await prisma.specialite.find_many(
            where={"id_departement": informatique_dept.id}
        )
        print(f"   📊 Total specialities: {len(all_specialities)}")
        
        # 3. Add levels for each speciality
        print("\n3️⃣ Adding levels...")
        levels_data = [
            "Licence 1", "Licence 2", "Licence 3", 
            "Master 1", "Master 2"
        ]
        
        created_levels = []
        for speciality in all_specialities:
            for level_name in levels_data:
                # Check if level already exists
                existing_level = await prisma.niveau.find_first(
                    where={
                        "nom": level_name,
                        "id_specialite": speciality.id
                    }
                )
                
                if existing_level:
                    print(f"   ⚠️ Level '{level_name}' already exists for {speciality.nom}")
                    created_levels.append(existing_level)
                else:
                    level = await prisma.niveau.create(
                        data={
                            "nom": level_name,
                            "id_specialite": speciality.id
                        }
                    )
                    print(f"   ✅ Created level: {level_name} for {speciality.nom}")
                    created_levels.append(level)
        
        # 4. Add groups for each level
        print("\n4️⃣ Adding groups...")
        groups_per_level = ["Groupe A", "Groupe B", "Groupe C"]
        
        created_groups = []
        for level in created_levels:
            for group_name in groups_per_level:
                full_group_name = f"{group_name}"
                
                # Check if group already exists
                existing_group = await prisma.groupe.find_first(
                    where={
                        "nom": full_group_name,
                        "id_niveau": level.id
                    }
                )
                
                if existing_group:
                    print(f"   ⚠️ Group '{full_group_name}' already exists for {level.nom}")
                    created_groups.append(existing_group)
                else:
                    group = await prisma.groupe.create(
                        data={
                            "nom": full_group_name,
                            "id_niveau": level.id
                        }
                    )
                    print(f"   ✅ Created group: {full_group_name} for {level.nom}")
                    created_groups.append(group)
        
        # 5. Get teachers
        print("\n5️⃣ Getting teachers...")
        teachers = await prisma.enseignant.find_many(
            where={"id_departement": informatique_dept.id}
        )
        print(f"   Found {len(teachers)} teachers in {informatique_dept.nom}")
        
        if not teachers:
            print("   ❌ No teachers found! Creating sample teacher...")
            teacher = await prisma.enseignant.create(
                data={
                    "nom": "Dupont",
                    "prenom": "Jean",
                    "email": "jean.dupont@univ.edu",
                    "id_departement": informatique_dept.id
                }
            )
            teachers = [teacher]
            print(f"   ✅ Created teacher: {teacher.prenom} {teacher.nom}")
        
        # 6. Add subjects for each speciality
        print("\n6️⃣ Adding subjects (matières)...")
        
        subjects_by_speciality = {
            "Génie Logiciel": [
                "Architecture Logicielle", "Tests et Qualité", "Gestion de Projet",
                "UML et Modélisation", "Développement Agile"
            ],
            "Intelligence Artificielle": [
                "Machine Learning", "Deep Learning", "Vision par Ordinateur",
                "Traitement du Langage Naturel", "Réseaux de Neurones"
            ],
            "Cybersécurité": [
                "Cryptographie", "Sécurité Réseau", "Audit de Sécurité",
                "Éthique et Droit", "Forensique Numérique"
            ],
            "Développement Web": [
                "HTML/CSS Avancé", "JavaScript Moderne", "Frameworks Frontend",
                "Backend Development", "Bases de Données Web"
            ],
            "Systèmes Embarqués": [
                "Programmation C/C++", "Microcontrôleurs", "IoT",
                "Temps Réel", "Électronique Numérique"
            ],
            "Réseaux et Télécommunications": [
                "Protocoles Réseau", "Administration Système", "Cloud Computing",
                "Virtualisation", "Sécurité Réseau"
            ]
        }
        
        created_subjects = []
        for speciality in all_specialities:
            spec_subjects = subjects_by_speciality.get(speciality.nom, [
                f"Matière 1 - {speciality.nom}",
                f"Matière 2 - {speciality.nom}",
                f"Matière 3 - {speciality.nom}"
            ])
            
            for subject_name in spec_subjects:
                # Check if subject already exists
                existing_subject = await prisma.matiere.find_first(
                    where={
                        "nom": subject_name,
                        "id_specialite": speciality.id
                    }
                )
                
                if existing_subject:
                    print(f"   ⚠️ Subject '{subject_name}' already exists")
                    created_subjects.append(existing_subject)
                else:
                    # Assign teacher (round-robin)
                    teacher = teachers[len(created_subjects) % len(teachers)]
                    
                    subject = await prisma.matiere.create(
                        data={
                            "nom": subject_name,
                            "id_specialite": speciality.id,
                            "id_enseignant": teacher.id
                        }
                    )
                    print(f"   ✅ Created subject: {subject_name} (Teacher: {teacher.prenom} {teacher.nom})")
                    created_subjects.append(subject)
        
        # 7. Add sample rooms
        print("\n7️⃣ Adding sample rooms...")
        rooms_to_add = [
            {"code": "A101", "type": "LECTURE", "capacite": 50},
            {"code": "A102", "type": "LECTURE", "capacite": 30},
            {"code": "B201", "type": "LAB", "capacite": 25},
            {"code": "B202", "type": "LAB", "capacite": 20},
            {"code": "C301", "type": "EXAM", "capacite": 100},
            {"code": "D401", "type": "OTHER", "capacite": 15}
        ]
        
        created_rooms = []
        for room_data in rooms_to_add:
            # Check if room already exists
            existing_room = await prisma.salle.find_first(
                where={"code": room_data["code"]}
            )
            
            if existing_room:
                print(f"   ⚠️ Room '{room_data['code']}' already exists")
                created_rooms.append(existing_room)
            else:
                room = await prisma.salle.create(data=room_data)
                print(f"   ✅ Created room: {room.code} ({room.type}, {room.capacite} places)")
                created_rooms.append(room)
        
        # 8. Final summary
        print("\n📊 Final Summary:")
        final_counts = await asyncio.gather(
            prisma.specialite.count(where={"id_departement": informatique_dept.id}),
            prisma.niveau.count(),
            prisma.groupe.count(),
            prisma.matiere.count(),
            prisma.enseignant.count(where={"id_departement": informatique_dept.id}),
            prisma.salle.count()
        )
        
        speciality_count, level_count, group_count, subject_count, teacher_count, room_count = final_counts
        
        print(f"   🏫 Department: {informatique_dept.nom}")
        print(f"   📚 Specialities: {speciality_count}")
        print(f"   🎓 Levels: {level_count}")
        print(f"   👥 Groups: {group_count}")
        print(f"   📖 Subjects: {subject_count}")
        print(f"   👨‍🏫 Teachers: {teacher_count}")
        print(f"   🏛️ Rooms: {room_count}")
        
        print("\n✅ Sample data creation completed successfully!")
        print("\n💡 You can now test the timetable creation with this data.")
        
    except Exception as e:
        print(f"❌ Error during sample data creation: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(add_sample_data())