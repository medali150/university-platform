import asyncio
from datetime import datetime, timedelta
from prisma import Prisma
import bcrypt
import random

# Initialize Prisma client
db = Prisma()

async def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def seed_database():
    """Seed the database with comprehensive test data"""
    await db.connect()
    print("🌱 Starting database seeding...")
    
    try:
        # Clear existing data
        print("🗑️ Clearing existing data...")
        # Delete in reverse order of dependencies
        await db.commentairesoumission.delete_many()
        await db.soumissiondevoir.delete_many()
        await db.rubrique.delete_many()
        await db.devoir.delete_many()
        await db.materielcours.delete_many()
        await db.commentaireannonce.delete_many()
        await db.annoncecours.delete_many()
        await db.reponsediscussion.delete_many()
        await db.discussion.delete_many()
        await db.presencecours.delete_many()
        await db.inscriptioncours.delete_many()
        await db.cours.delete_many()
        await db.eventcomment.delete_many()
        await db.eventreaction.delete_many()
        await db.evenement.delete_many()
        await db.relevenotes.delete_many()
        await db.moyenne.delete_many()
        await db.note.delete_many()
        await db.notification.delete_many()
        await db.message.delete_many()
        await db.chatai.delete_many()
        await db.evenementcalendrier.delete_many()
        await db.passwordresettoken.delete_many()
        await db.absence.delete_many()
        await db.emploitemps.delete_many()
        await db.matiere.delete_many()
        await db.chefdepartement.delete_many()
        await db.administrateur.delete_many()
        await db.utilisateur.delete_many()
        await db.etudiant.delete_many()
        await db.enseignant.delete_many()
        await db.groupe.delete_many()
        await db.niveau.delete_many()
        await db.specialite.delete_many()
        await db.salle.delete_many()
        await db.departement.delete_many()
        print("✅ Cleared existing data")
        
        # 1. Create Departments
        print("📚 Creating Departments...")
        dept_informatique = await db.departement.create({
            'nom': 'Informatique',
        })
        dept_mathematiques = await db.departement.create({
            'nom': 'Mathématiques',
        })
        dept_physique = await db.departement.create({
            'nom': 'Physique',
        })
        dept_electronique = await db.departement.create({
            'nom': 'Électronique',
        })
        print(f"✅ Created {4} departments")
        
        # 2. Create Specialties
        print("🎓 Creating Specialties...")
        spec_ia = await db.specialite.create({
            'nom': 'Intelligence Artificielle',
            'id_departement': dept_informatique.id,
        })
        spec_reseaux = await db.specialite.create({
            'nom': 'Réseaux et Télécommunications',
            'id_departement': dept_informatique.id,
        })
        spec_gl = await db.specialite.create({
            'nom': 'Génie Logiciel',
            'id_departement': dept_informatique.id,
        })
        spec_math_app = await db.specialite.create({
            'nom': 'Mathématiques Appliquées',
            'id_departement': dept_mathematiques.id,
        })
        spec_physique_app = await db.specialite.create({
            'nom': 'Physique Appliquée',
            'id_departement': dept_physique.id,
        })
        print(f"✅ Created {5} specialties")
        
        # 3. Create Levels
        print("📖 Creating Levels...")
        niveau_l1_ia = await db.niveau.create({
            'nom': 'Licence 1',
            'id_specialite': spec_ia.id,
        })
        niveau_l2_ia = await db.niveau.create({
            'nom': 'Licence 2',
            'id_specialite': spec_ia.id,
        })
        niveau_l3_ia = await db.niveau.create({
            'nom': 'Licence 3',
            'id_specialite': spec_ia.id,
        })
        niveau_l1_gl = await db.niveau.create({
            'nom': 'Licence 1',
            'id_specialite': spec_gl.id,
        })
        niveau_l2_gl = await db.niveau.create({
            'nom': 'Licence 2',
            'id_specialite': spec_gl.id,
        })
        niveau_l3_gl = await db.niveau.create({
            'nom': 'Licence 3',
            'id_specialite': spec_gl.id,
        })
        print(f"✅ Created {6} levels")
        
        # 4. Create Groups
        print("👥 Creating Groups...")
        groupe_l1_ia_g1 = await db.groupe.create({
            'nom': 'Groupe 1',
            'id_niveau': niveau_l1_ia.id,
        })
        groupe_l1_ia_g2 = await db.groupe.create({
            'nom': 'Groupe 2',
            'id_niveau': niveau_l1_ia.id,
        })
        groupe_l2_ia_g1 = await db.groupe.create({
            'nom': 'Groupe 1',
            'id_niveau': niveau_l2_ia.id,
        })
        groupe_l3_ia_g1 = await db.groupe.create({
            'nom': 'Groupe 1',
            'id_niveau': niveau_l3_ia.id,
        })
        groupe_l1_gl_g1 = await db.groupe.create({
            'nom': 'Groupe 1',
            'id_niveau': niveau_l1_gl.id,
        })
        groupe_l2_gl_g1 = await db.groupe.create({
            'nom': 'Groupe 1',
            'id_niveau': niveau_l2_gl.id,
        })
        print(f"✅ Created {6} groups")
        
        # 5. Create Rooms
        print("🏫 Creating Rooms...")
        salles = []
        room_types = ['LECTURE', 'LAB', 'EXAM']
        for i in range(1, 16):
            room_type = room_types[(i-1) % 3]
            salle = await db.salle.create({
                'code': f'A{i:02d}',
                'type': room_type,
                'capacite': 30 if room_type == 'LAB' else 60 if room_type == 'LECTURE' else 100,
            })
            salles.append(salle)
        print(f"✅ Created {len(salles)} rooms")
        
        # 6. Create Teachers
        print("👨‍🏫 Creating Teachers...")
        teacher_names = [
            ('Benali', 'Ahmed', 'ahmed.benali@univ.dz'),
            ('Mansouri', 'Fatima', 'fatima.mansouri@univ.dz'),
            ('Khelifi', 'Mohamed', 'mohamed.khelifi@univ.dz'),
            ('Brahimi', 'Sarah', 'sarah.brahimi@univ.dz'),
            ('Azzedine', 'Karim', 'karim.azzedine@univ.dz'),
            ('Mokrani', 'Leila', 'leila.mokrani@univ.dz'),
            ('Slimani', 'Rachid', 'rachid.slimani@univ.dz'),
            ('Amrani', 'Nadia', 'nadia.amrani@univ.dz'),
            ('Haddad', 'Omar', 'omar.haddad@univ.dz'),
            ('Belkacem', 'Samira', 'samira.belkacem@univ.dz'),
        ]
        
        enseignants = []
        teacher_users = []
        for nom, prenom, email in teacher_names:
            enseignant = await db.enseignant.create({
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'id_departement': random.choice([dept_informatique.id, dept_mathematiques.id, dept_physique.id]),
                'image_url': f'https://ui-avatars.com/api/?name={prenom}+{nom}&background=random',
            })
            enseignants.append(enseignant)
            
            # Create user for teacher
            teacher_user = await db.utilisateur.create({
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'role': 'TEACHER',
                'mdp_hash': await hash_password('password123'),
                'enseignant_id': enseignant.id,
            })
            teacher_users.append(teacher_user)
        print(f"✅ Created {len(enseignants)} teachers")
        
        # 7. Create Students
        print("👨‍🎓 Creating Students...")
        first_names = ['Ahmed', 'Mohamed', 'Fatima', 'Sarah', 'Karim', 'Leila', 'Rachid', 'Nadia', 
                       'Omar', 'Samira', 'Yassine', 'Amina', 'Bilal', 'Imane', 'Sofiane', 'Meriem',
                       'Walid', 'Rania', 'Hamza', 'Nesrine', 'Mehdi', 'Khadija', 'Tarek', 'Asma',
                       'Amine', 'Yasmine', 'Riad', 'Siham', 'Mourad', 'Salma']
        last_names = ['Benali', 'Mansouri', 'Khelifi', 'Brahimi', 'Azzedine', 'Mokrani', 'Slimani',
                      'Amrani', 'Haddad', 'Belkacem', 'Bouaziz', 'Cherif', 'Djelloul', 'Ferhat',
                      'Ghomari', 'Hadjadj', 'Idris', 'Kadri', 'Larbi', 'Makhlouf']
        
        etudiants = []
        groupes_list = [groupe_l1_ia_g1, groupe_l1_ia_g2, groupe_l2_ia_g1, groupe_l3_ia_g1, groupe_l1_gl_g1, groupe_l2_gl_g1]
        
        student_count = 0
        for groupe in groupes_list:
            # Get specialite and niveau for this group
            niveau = await db.niveau.find_unique(where={'id': groupe.id_niveau})
            spec_id = niveau.id_specialite
            
            for i in range(10):  # 10 students per group
                prenom = random.choice(first_names)
                nom = random.choice(last_names)
                email = f'{prenom.lower()}.{nom.lower()}{student_count}@etudiant.univ.dz'
                
                etudiant = await db.etudiant.create({
                    'nom': nom,
                    'prenom': prenom,
                    'email': email,
                    'id_groupe': groupe.id,
                    'id_specialite': spec_id,
                    'id_niveau': groupe.id_niveau,
                })
                etudiants.append(etudiant)
                
                # Create user for student
                await db.utilisateur.create({
                    'nom': nom,
                    'prenom': prenom,
                    'email': email,
                    'role': 'STUDENT',
                    'mdp_hash': await hash_password('password123'),
                    'etudiant_id': etudiant.id,
                })
                student_count += 1
        print(f"✅ Created {len(etudiants)} students")
        
        # 8. Create Admin User
        print("👤 Creating Admin User...")
        admin_user = await db.utilisateur.create({
            'nom': 'Admin',
            'prenom': 'System',
            'email': 'admin@univ.dz',
            'role': 'ADMIN',
            'mdp_hash': await hash_password('admin123'),
        })
        await db.administrateur.create({
            'id_utilisateur': admin_user.id,
            'niveau': 'SUPER_ADMIN',
        })
        print("✅ Created admin user")
        
        # 9. Create Department Head
        print("👔 Creating Department Head...")
        dept_head_user = await db.utilisateur.create({
            'nom': 'Benamar',
            'prenom': 'Farid',
            'email': 'farid.benamar@univ.dz',
            'role': 'DEPARTMENT_HEAD',
            'mdp_hash': await hash_password('password123'),
        })
        await db.chefdepartement.create({
            'id_utilisateur': dept_head_user.id,
            'id_departement': dept_informatique.id,
        })
        print("✅ Created department head")
        
        # 10. Create Subjects
        print("📚 Creating Subjects...")
        matieres = []
        subjects_data = [
            ('Algorithmique', 3.0, 'S1', dept_informatique.id, niveau_l1_ia.id, spec_ia.id, enseignants[0].id),
            ('Programmation Python', 3.0, 'S1', dept_informatique.id, niveau_l1_ia.id, spec_ia.id, enseignants[1].id),
            ('Bases de données', 2.5, 'S1', dept_informatique.id, niveau_l1_ia.id, spec_ia.id, enseignants[2].id),
            ('Mathématiques 1', 3.0, 'S1', dept_mathematiques.id, niveau_l1_ia.id, spec_ia.id, enseignants[3].id),
            ('Anglais Technique', 2.0, 'S1', dept_informatique.id, niveau_l1_ia.id, spec_ia.id, enseignants[4].id),
            ('Machine Learning', 4.0, 'S1', dept_informatique.id, niveau_l2_ia.id, spec_ia.id, enseignants[0].id),
            ('Réseaux Informatiques', 3.0, 'S1', dept_informatique.id, niveau_l2_ia.id, spec_ia.id, enseignants[1].id),
            ('Systèmes d\'exploitation', 3.0, 'S1', dept_informatique.id, niveau_l2_ia.id, spec_ia.id, enseignants[2].id),
            ('Deep Learning', 4.0, 'S1', dept_informatique.id, niveau_l3_ia.id, spec_ia.id, enseignants[0].id),
            ('Vision par Ordinateur', 3.5, 'S1', dept_informatique.id, niveau_l3_ia.id, spec_ia.id, enseignants[1].id),
            ('Développement Web', 3.0, 'S1', dept_informatique.id, niveau_l1_gl.id, spec_gl.id, enseignants[5].id),
            ('UML et Conception', 2.5, 'S1', dept_informatique.id, niveau_l2_gl.id, spec_gl.id, enseignants[6].id),
        ]
        
        for nom, coeff, sem, dept_id, niveau_id, spec_id, ens_id in subjects_data:
            matiere = await db.matiere.create({
                'nom': nom,
                'coefficient': coeff,
                'semester': sem,
                'id_departement': dept_id,
                'id_niveau': niveau_id,
                'id_specialite': spec_id,
                'id_enseignant': ens_id,
            })
            matieres.append(matiere)
        print(f"✅ Created {len(matieres)} subjects")
        
        # 11. Create Schedules
        print("📅 Creating Schedules...")
        base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        emplois = []
        
        for i in range(30):  # Create 30 schedule entries
            day_offset = i % 5  # Monday to Friday
            slot = i // 5  # Time slot
            
            date = base_date + timedelta(days=day_offset)
            heure_debut = date + timedelta(hours=slot * 2)
            heure_fin = heure_debut + timedelta(hours=2)
            
            emploi = await db.emploitemps.create({
                'date': date,
                'heure_debut': heure_debut,
                'heure_fin': heure_fin,
                'id_salle': random.choice(salles).id,
                'id_matiere': random.choice(matieres).id,
                'id_groupe': random.choice(groupes_list).id,
                'id_enseignant': random.choice(enseignants).id,
                'status': random.choice(['PLANNED', 'PLANNED', 'PLANNED', 'CANCELED']),
                'semester': 'S1',
                'week_day': day_offset + 1,
                'is_recurring': random.choice([True, False]),
            })
            emplois.append(emploi)
        print(f"✅ Created {len(emplois)} schedule entries")
        
        # 12. Create Absences
        print("📝 Creating Absences...")
        absences_count = 0
        for _ in range(50):
            emploi = random.choice(emplois)
            etudiant = random.choice(etudiants)
            
            await db.absence.create({
                'id_etudiant': etudiant.id,
                'id_emploitemps': emploi.id,
                'date_absence': emploi.date,
                'statut': random.choice(['unjustified', 'pending_review', 'justified', 'approved']),
                'motif': random.choice(['Maladie', 'Rendez-vous médical', 'Urgence familiale', None]),
            })
            absences_count += 1
        print(f"✅ Created {absences_count} absences")
        
        # 13. Create Courses
        print("📖 Creating Courses...")
        cours_list = []
        current_year = datetime.now().year
        
        course_data = [
            ('CS101', 'Introduction à la Programmation', 'Cours fondamental de programmation', '#3B82F6', enseignants[0].id, dept_informatique.id, spec_ia.id, niveau_l1_ia.id),
            ('CS201', 'Structures de Données', 'Étude approfondie des structures de données', '#10B981', enseignants[1].id, dept_informatique.id, spec_ia.id, niveau_l2_ia.id),
            ('CS301', 'Intelligence Artificielle Avancée', 'Techniques avancées en IA', '#F59E0B', enseignants[0].id, dept_informatique.id, spec_ia.id, niveau_l3_ia.id),
            ('CS102', 'Développement Web Full Stack', 'Création d\'applications web modernes', '#8B5CF6', enseignants[5].id, dept_informatique.id, spec_gl.id, niveau_l1_gl.id),
            ('CS202', 'Architecture Logicielle', 'Patterns et bonnes pratiques', '#EF4444', enseignants[6].id, dept_informatique.id, spec_gl.id, niveau_l2_gl.id),
        ]
        
        for code, nom, desc, couleur, ens_id, dept_id, spec_id, niveau_id in course_data:
            cours = await db.cours.create({
                'code': code,
                'nom': nom,
                'description': desc,
                'imageUrl': f'https://source.unsplash.com/800x600/?technology,education',
                'couleur': couleur,
                'id_enseignant': ens_id,
                'id_departement': dept_id,
                'id_specialite': spec_id,
                'id_niveau': niveau_id,
                'anneeAcademique': f'{current_year}-{current_year+1}',
                'semestre': 'S1',
                'capaciteMax': 60,
                'estActif': True,
                'estPublic': False,
                'codeInvitation': f'INV{code}',
                'dateDebut': datetime.now() - timedelta(days=30),
                'dateFin': datetime.now() + timedelta(days=90),
            })
            cours_list.append(cours)
        print(f"✅ Created {len(cours_list)} courses")
        
        # 14. Enroll Students in Courses
        print("📝 Enrolling Students in Courses...")
        enrollments_count = 0
        for cours in cours_list:
            # Enroll students from the same level
            cours_niveau = cours.id_niveau
            students_to_enroll = [e for e in etudiants if e.id_niveau == cours_niveau][:15]
            
            for etudiant in students_to_enroll:
                await db.inscriptioncours.create({
                    'id_cours': cours.id,
                    'id_etudiant': etudiant.id,
                    'statut': 'active',
                    'role': 'student',
                })
                enrollments_count += 1
        print(f"✅ Created {enrollments_count} course enrollments")
        
        # 15. Create Assignments
        print("📋 Creating Assignments...")
        devoirs_list = []
        for cours in cours_list:
            for i in range(3):  # 3 assignments per course
                devoir = await db.devoir.create({
                    'titre': f'Devoir {i+1} - {cours.nom}',
                    'description': f'Description du devoir {i+1}',
                    'instructions': 'Veuillez lire attentivement les instructions et soumettre votre travail avant la date limite.',
                    'id_cours': cours.id,
                    'type': random.choice(['assignment', 'quiz', 'project']),
                    'points': random.choice([20, 50, 100]),
                    'dateLimite': datetime.now() + timedelta(days=random.randint(7, 30)),
                    'dateDisponible': datetime.now() - timedelta(days=random.randint(1, 5)),
                    'autoriserSoumissionTardive': random.choice([True, False]),
                    'attemptsMax': random.choice([1, 2, 3]),
                    'afficherCorrection': True,
                    'detectionPlagiat': True,
                    'feedbackAI': True,
                })
                devoirs_list.append(devoir)
        print(f"✅ Created {len(devoirs_list)} assignments")
        
        # 16. Create Assignment Submissions
        print("📤 Creating Assignment Submissions...")
        submissions_count = 0
        for devoir in devoirs_list[:10]:  # Create submissions for first 10 assignments
            # Get enrolled students for this course
            enrollments = await db.inscriptioncours.find_many(
                where={'id_cours': devoir.id_cours},
                take=8
            )
            
            for enrollment in enrollments:
                if random.random() > 0.3:  # 70% submission rate
                    await db.soumissiondevoir.create({
                        'id_devoir': devoir.id,
                        'id_etudiant': enrollment.id_etudiant,
                        'contenu': 'Contenu de la soumission de l\'étudiant...',
                        'statut': random.choice(['submitted', 'graded', 'pending']),
                        'tentativeNumero': 1,
                        'estEnRetard': random.choice([True, False]),
                        'note': random.uniform(10, 20) if random.random() > 0.5 else None,
                        'noteMax': 20.0,
                        'feedback': 'Bon travail, continuez ainsi!' if random.random() > 0.5 else None,
                    })
                    submissions_count += 1
        print(f"✅ Created {submissions_count} assignment submissions")
        
        # 17. Create Course Announcements
        print("📢 Creating Course Announcements...")
        announcements_count = 0
        for cours in cours_list:
            # Get the teacher user for this course
            teacher_user = await db.utilisateur.find_first(
                where={'enseignant_id': cours.id_enseignant}
            )
            
            for i in range(random.randint(2, 5)):
                await db.annoncecours.create({
                    'titre': f'Annonce {i+1}',
                    'contenu': f'Ceci est une annonce importante pour le cours {cours.nom}. Veuillez la lire attentivement.',
                    'id_cours': cours.id,
                    'id_auteur': teacher_user.id,
                    'estEpingle': i == 0,
                    'autoriserCommentaires': True,
                })
                announcements_count += 1
        print(f"✅ Created {announcements_count} course announcements")
        
        # 18. Create Discussions
        print("💬 Creating Discussions...")
        discussions_count = 0
        for cours in cours_list:
            enrollments = await db.inscriptioncours.find_many(
                where={'id_cours': cours.id},
                take=3
            )
            
            # Get the teacher user for this course
            teacher_user = await db.utilisateur.find_first(
                where={'enseignant_id': cours.id_enseignant}
            )
            
            for enrollment in enrollments:
                # Get student user
                student_user = await db.utilisateur.find_first(
                    where={'etudiant_id': enrollment.id_etudiant}
                )
                
                discussion = await db.discussion.create({
                    'titre': f'Question sur {cours.nom}',
                    'contenu': 'J\'ai une question concernant le dernier cours...',
                    'id_cours': cours.id,
                    'id_auteur': student_user.id,
                    'nbVues': random.randint(5, 50),
                })
                discussions_count += 1
                
                # Add some replies
                for _ in range(random.randint(1, 3)):
                    await db.reponsediscussion.create({
                        'id_discussion': discussion.id,
                        'id_auteur': teacher_user.id,
                        'contenu': 'Voici ma réponse à votre question...',
                    })
        print(f"✅ Created {discussions_count} discussions")
        
        # 19. Create Grades
        print("📊 Creating Grades...")
        grades_count = 0
        current_year = f'{datetime.now().year}-{datetime.now().year+1}'
        
        for matiere in matieres[:6]:  # Create grades for first 6 subjects
            # Get students from the same level
            niveau = matiere.id_niveau
            students_for_grade = [e for e in etudiants if e.id_niveau == niveau][:10]
            
            for etudiant in students_for_grade:
                # Create multiple grades per student
                for grade_type in ['EXAM', 'CONTINUOUS', 'PRACTICAL']:
                    await db.note.create({
                        'valeur': round(random.uniform(8, 20), 2),
                        'type': grade_type,
                        'coefficient': 1.0 if grade_type == 'CONTINUOUS' else 2.0,
                        'id_etudiant': etudiant.id,
                        'id_matiere': matiere.id,
                        'id_enseignant': matiere.id_enseignant,
                        'semestre': 'SEMESTER_1',
                        'annee_scolaire': current_year,
                        'date_examen': datetime.now() - timedelta(days=random.randint(1, 30)),
                        'validee': True,
                        'observation': 'Bon travail' if random.random() > 0.5 else None,
                    })
                    grades_count += 1
        print(f"✅ Created {grades_count} grades")
        
        # 20. Create Averages
        print("📈 Creating Averages...")
        averages_count = 0
        for matiere in matieres[:6]:
            niveau = matiere.id_niveau
            students_for_avg = [e for e in etudiants if e.id_niveau == niveau][:10]
            
            for etudiant in students_for_avg:
                await db.moyenne.create({
                    'id_etudiant': etudiant.id,
                    'id_matiere': matiere.id,
                    'semestre': 'SEMESTER_1',
                    'annee_scolaire': current_year,
                    'moyenne_matiere': round(random.uniform(10, 18), 2),
                    'rang': random.randint(1, 10),
                    'validee': True,
                })
                averages_count += 1
        print(f"✅ Created {averages_count} averages")
        
        # 21. Create Events
        print("🎉 Creating Events...")
        events_data = [
            ('Journée Portes Ouvertes', 'event', 'Découvrez notre université', 'Campus Principal'),
            ('Conférence sur l\'IA', 'conference', 'Experts en intelligence artificielle', 'Amphithéâtre A'),
            ('Hackathon 2024', 'competition', 'Compétition de programmation', 'Laboratoire Informatique'),
            ('Cérémonie de Remise des Diplômes', 'ceremony', 'Félicitations aux diplômés', 'Grande Salle'),
            ('Séminaire Cybersécurité', 'seminar', 'Protection des données', 'Salle de Conférence'),
        ]
        
        for titre, type_evt, desc, lieu in events_data:
            evenement = await db.evenement.create({
                'titre': titre,
                'type': type_evt,
                'description': desc,
                'date': datetime.now() + timedelta(days=random.randint(10, 60)),
                'lieu': lieu,
                'id_createur': admin_user.id,
            })
        print(f"✅ Created {len(events_data)} events")
        
        # 22. Create Notifications
        print("🔔 Creating Notifications...")
        notifications_count = 0
        for etudiant in etudiants[:20]:  # Create notifications for first 20 students
            # Get student user
            student_user = await db.utilisateur.find_first(
                where={'etudiant_id': etudiant.id}
            )
            
            for i in range(random.randint(2, 5)):
                await db.notification.create({
                    'userId': student_user.id,
                    'type': random.choice(['info', 'warning', 'success', 'error']),
                    'title': 'Nouvelle notification',
                    'message': f'Vous avez une nouvelle notification #{i+1}',
                    'isRead': random.choice([True, False]),
                })
                notifications_count += 1
        print(f"✅ Created {notifications_count} notifications")
        
        # 23. Create Course Materials
        print("📚 Creating Course Materials...")
        materials_count = 0
        for cours in cours_list:
            for i in range(random.randint(3, 7)):
                await db.materielcours.create({
                    'titre': f'Chapitre {i+1}',
                    'description': f'Matériel de cours pour le chapitre {i+1}',
                    'id_cours': cours.id,
                    'type': random.choice(['pdf', 'video', 'link', 'document']),
                    'fichierUrl': f'https://example.com/files/chapter{i+1}.pdf',
                    'fichierNom': f'chapter{i+1}.pdf',
                    'fichierTaille': random.randint(100000, 5000000),
                    'fichierType': 'application/pdf',
                    'ordre': i,
                    'estPublie': True,
                    'estTelechargeable': True,
                })
                materials_count += 1
        print(f"✅ Created {materials_count} course materials")
        
        # 24. Create Calendar Events
        print("📅 Creating Calendar Events...")
        calendar_count = 0
        for etudiant in etudiants[:15]:
            # Get student user
            student_user = await db.utilisateur.find_first(
                where={'etudiant_id': etudiant.id}
            )
            
            for i in range(random.randint(2, 4)):
                date_debut = datetime.now() + timedelta(days=random.randint(1, 30))
                await db.evenementcalendrier.create({
                    'titre': f'Événement {i+1}',
                    'description': 'Description de l\'événement',
                    'id_utilisateur': student_user.id,
                    'dateDebut': date_debut,
                    'dateFin': date_debut + timedelta(hours=2),
                    'estJourneeComplete': False,
                    'type': random.choice(['exam', 'meeting', 'deadline', 'event']),
                    'couleur': random.choice(['#3B82F6', '#10B981', '#F59E0B', '#EF4444']),
                })
                calendar_count += 1
        print(f"✅ Created {calendar_count} calendar events")
        
        # 25. Create Messages
        print("💌 Creating Messages...")
        messages_count = 0
        for _ in range(30):
            sender_student = random.choice(etudiants)
            receiver_teacher = random.choice(enseignants)
            
            # Get users
            sender_user = await db.utilisateur.find_first(
                where={'etudiant_id': sender_student.id}
            )
            receiver_user = await db.utilisateur.find_first(
                where={'enseignant_id': receiver_teacher.id}
            )
            
            await db.message.create({
                'id_expediteur': sender_user.id,
                'id_destinataire': receiver_user.id,
                'contenu': 'Bonjour, j\'ai une question concernant le cours...',
            })
            messages_count += 1
        print(f"✅ Created {messages_count} messages")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Departments: 4")
        print(f"   - Specialties: 5")
        print(f"   - Levels: 6")
        print(f"   - Groups: 6")
        print(f"   - Rooms: {len(salles)}")
        print(f"   - Teachers: {len(enseignants)}")
        print(f"   - Students: {len(etudiants)}")
        print(f"   - Subjects: {len(matieres)}")
        print(f"   - Schedules: {len(emplois)}")
        print(f"   - Absences: {absences_count}")
        print(f"   - Courses: {len(cours_list)}")
        print(f"   - Enrollments: {enrollments_count}")
        print(f"   - Assignments: {len(devoirs_list)}")
        print(f"   - Submissions: {submissions_count}")
        print(f"   - Announcements: {announcements_count}")
        print(f"   - Discussions: {discussions_count}")
        print(f"   - Grades: {grades_count}")
        print(f"   - Averages: {averages_count}")
        print(f"   - Events: {len(events_data)}")
        print(f"   - Notifications: {notifications_count}")
        print(f"   - Course Materials: {materials_count}")
        print(f"   - Calendar Events: {calendar_count}")
        print(f"   - Messages: {messages_count}")
        print("\n🔑 Login Credentials:")
        print("   Admin: admin@univ.dz / admin123")
        print("   Department Head: farid.benamar@univ.dz / password123")
        print("   Teacher: ahmed.benali@univ.dz / password123")
        print("   Student: (any student email) / password123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_database())
