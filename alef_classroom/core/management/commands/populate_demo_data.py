from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from classroom.models import Classroom, ClassroomMember, Announcement
from assignment.models import Assignment, AssignmentSubmission


class Command(BaseCommand):
    help = 'Populate database with demo data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')
        else:
            self.stdout.write(f'Admin user already exists: {admin_user.username}')

        # Create teachers
        teachers = []
        teacher_names = [
            ('John', 'Doe'),
            ('Sarah', 'Wilson'),
            ('Michael', 'Brown'),
        ]
        for i, (first, last) in enumerate(teacher_names, 1):
            teacher, created = User.objects.get_or_create(
                username=f'teacher{i}',
                defaults={
                    'email': f'teacher{i}@example.com',
                    'first_name': first,
                    'last_name': last,
                    'role': User.Role.TEACHER,
                }
            )
            if created:
                teacher.set_password('teacher123')
                teacher.save()
                self.stdout.write(f'Created teacher: {teacher.username}')
            else:
                self.stdout.write(f'Teacher already exists: {teacher.username}')
            teachers.append(teacher)

        # Create students
        students = []
        student_names = [
            ('Alice', 'Smith'),
            ('Bob', 'Johnson'),
            ('Carol', 'Williams'),
            ('David', 'Jones'),
            ('Emma', 'Garcia'),
            ('Frank', 'Miller'),
            ('Grace', 'Davis'),
            ('Henry', 'Rodriguez'),
        ]
        for i, (first, last) in enumerate(student_names, 1):
            student, created = User.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@example.com',
                    'first_name': first,
                    'last_name': last,
                    'role': User.Role.STUDENT,
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                self.stdout.write(f'Created student: {student.username}')
            else:
                self.stdout.write(f'Student already exists: {student.username}')
            students.append(student)

        # Create classrooms
        classroom_data = [
            ('Introduction to Python', 'Learn Python programming from basics to advanced concepts', 'CS101'),
            ('Web Development with Django', 'Build web applications using Django framework', 'CS201'),
            ('Data Science Fundamentals', 'Introduction to data analysis and visualization', 'CS301'),
            ('Advanced JavaScript', 'Master JavaScript for modern web development', 'CS102'),
            ('Database Design', 'Learn SQL and database design principles', 'CS202'),
        ]

        classrooms = []
        for i, (name, desc, section) in enumerate(classroom_data):
            classroom, created = Classroom.objects.get_or_create(
                name=name,
                section=section,
                defaults={
                    'description': desc,
                    'creator': teachers[i % len(teachers)],
                }
            )
            if created:
                self.stdout.write(f'Created classroom: {classroom.name}')
            else:
                self.stdout.write(f'Classroom already exists: {classroom.name}')
            classrooms.append(classroom)

            # Add teacher as member
            ClassroomMember.objects.get_or_create(
                classroom=classroom,
                user=classroom.creator,
                defaults={'role': ClassroomMember.Role.TEACHER}
            )

            # Add students to classroom (distribute students across classrooms)
            for j, student in enumerate(students):
                if (i + j) % 2 == 0:
                    ClassroomMember.objects.get_or_create(
                        classroom=classroom,
                        user=student,
                        defaults={'role': ClassroomMember.Role.STUDENT}
                    )

            # Create announcements
            for ann_num in range(2):
                Announcement.objects.get_or_create(
                    classroom=classroom,
                    title=f'Announcement {ann_num + 1}: {name}',
                    defaults={
                        'author': classroom.creator,
                        'content': f'Important update for {name}. Please read carefully and let me know if you have any questions.'
                    }
                )

            # Create assignments
            for assign_num in range(3):
                assignment, created = Assignment.objects.get_or_create(
                    classroom=classroom,
                    title=f'Assignment {assign_num + 1}',
                    defaults={
                        'description': f'Complete this assignment for {name}. Submit your work before the deadline.',
                        'due_date': timezone.now() + timedelta(days=7 + assign_num * 7),
                        'created_by': classroom.creator,
                    }
                )

                # Create submissions from enrolled students
                for student in students:
                    if ClassroomMember.objects.filter(classroom=classroom, user=student).exists():
                        if (student.id + assign_num) % 3 != 0:  # Not all students submit
                            AssignmentSubmission.objects.get_or_create(
                                assignment=assignment,
                                student=student,
                                defaults={
                                    'submitted_at': timezone.now() - timedelta(days=assign_num),
                                    'content': f'Submission from {student.first_name} for {assignment.title}'
                                }
                            )

        self.stdout.write(self.style.SUCCESS('\nDemo data created successfully!'))
        self.stdout.write('\nDemo credentials:')
        self.stdout.write('Admin: admin / admin123')
        for i in range(1, len(teachers) + 1):
            self.stdout.write(f'Teacher {i}: teacher{i} / teacher123')
        for i in range(1, len(students) + 1):
            self.stdout.write(f'Student {i}: student{i} / student123')
