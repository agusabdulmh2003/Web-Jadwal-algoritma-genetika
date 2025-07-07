import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.2
TIMESLOTS = {
    1: "07:00 - 08:30",
    2: "08:30 - 10:00",
    3: "10:30 - 12:00",
    4: "13:00 - 14:30",
    5: "14:30 - 16:00"
}

def preprocess_data(classes, subjects, teachers, timeslots):
    # Pastikan semua kelas memiliki department
    classes['Department'] = classes['Department'].astype(str)
    subjects['Department'] = subjects['Department'].astype(str)
    
    # Mapping teacher to subjects and departments
    teacher_subjects = {}
    for _, row in teachers.iterrows():
        teacher = row['Teacher']
        subject = row['Subject']
        department = row['Department']
        if teacher not in teacher_subjects:
            teacher_subjects[teacher] = []
        teacher_subjects[teacher].append((subject, department))
    
    # Kelas lengkap MAN 3 Cilacap
    all_classes = [
        'X IPA 1', 'X IPA 2', 'X IPA 3', 'X IPA 4', 'X IPA 5',
        'X IPS 1', 'X IPS 2', 'X IPS 3', 'X Agama',
        'XI IPA 1', 'XI IPA 2', 'XI IPA 3', 'XI IPA 4', 
        'XI IPS 1', 'XI IPS 2', 'XI IPS 3', 'XI Agama',
        'XII IPA 1', 'XII IPA 2', 'XII IPA 3', 'XII IPA 4',
        'XII IPS 1', 'XII IPS 2', 'XII IPS 3', 'XII Agama'
    ]
    
    return teacher_subjects, subjects, all_classes

def create_individual(teacher_subjects, subjects, classes_list):
    schedule = []
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
    
    for class_name in classes_list:
        # Tentukan jurusan berdasarkan nama kelas
        if "IPA" in class_name:
            department = "IPA"
        elif "IPS" in class_name:
            department = "IPS"
        else:
            department = "Agama"
        
        for day in days:
            # Sabtu hanya sampai jam 12:00 (3 slot)
            max_slot = 5 if day != 'Sabtu' else 3
            
            for timeslot in range(1, max_slot + 1):
                # Filter mata pelajaran berdasarkan jurusan kelas
                class_subjects = subjects[subjects['Department'] == department]
                
                if not class_subjects.empty:
                    subject_row = class_subjects.sample(n=1).iloc[0]
                    subject = subject_row['Subject']
                    
                    # Cari guru yang cocok
                    valid_teachers = []
                    for teacher, subj_list in teacher_subjects.items():
                        for subj, dept in subj_list:
                            if subj == subject and dept == department:
                                valid_teachers.append(teacher)
                    
                    if valid_teachers:
                        teacher = random.choice(valid_teachers)
                    else:
                        # Jika tidak ada guru, pilih random
                        teacher = random.choice(list(teacher_subjects.keys()))
                    
                    # Tentukan ruangan berdasarkan mata pelajaran
                    if "Lab" in subject or "Praktikum" in subject:
                        room = "Lab " + subject.split()[0]
                    elif "Olahraga" in subject:
                        room = "Lapangan Olahraga"
                    elif "Agama" in subject:
                        room = "Ruang Agama"
                    else:
                        room = f"Ruang {class_name}"
                    
                    # Tambahkan entri jadwal dengan semua atribut
                    schedule.append((day, timeslot, class_name, department, subject, teacher, room))
    
    return schedule

def fitness(schedule):
    conflicts = 0
    teacher_schedule = {}
    class_schedule = {}
    
    for entry in schedule:
        day, timeslot, class_name, _, _, teacher, _ = entry
        teacher_key = (teacher, day, timeslot)
        class_key = (class_name, day, timeslot)
        
        # Cek konflik guru
        if teacher_key in teacher_schedule:
            conflicts += 1
        else:
            teacher_schedule[teacher_key] = True
        
        # Cek konflik kelas
        if class_key in class_schedule:
            conflicts += 1
        else:
            class_schedule[class_key] = True
            
    return 1 / (1 + conflicts)

def selection(population):
    return sorted(population, key=lambda x: fitness(x), reverse=True)[:2]

def crossover(parent1, parent2):
    if len(parent1) != len(parent2):
        return parent1
    
    child = []
    for i in range(len(parent1)):
        if random.random() > 0.5:
            child.append(parent1[i])
        else:
            child.append(parent2[i])
    return child

def mutate(individual, teacher_subjects):
    if random.random() < MUTATION_RATE:
        idx = random.randint(0, len(individual) - 1)
        day, timeslot, class_name, department, subject, teacher, room = individual[idx]
        
        # Mutasi guru
        if random.random() < 0.3:
            valid_teachers = [t for t, subjs in teacher_subjects.items() 
                             if any(s[0] == subject for s in subjs)]
            if valid_teachers:
                teacher = random.choice(valid_teachers)
        
        # Mutasi timeslot (pastikan Sabtu hanya sampai slot 3)
        if random.random() < 0.2:
            max_slot = 5 if day != 'Sabtu' else 3
            timeslot = random.randint(1, max_slot)
        
        individual[idx] = (day, timeslot, class_name, department, subject, teacher, room)
    return individual

def plot_convergence(best, avg, worst, save_path='static/chart.png'):
    plt.figure(figsize=(10, 6))
    plt.plot(best, label='Fitness Terbaik', color='green')
    plt.plot(avg, label='Rata-rata Fitness', color='blue')
    plt.plot(worst, label='Fitness Terburuk', color='red')
    plt.xlabel('Generasi')
    plt.ylabel('Nilai Fitness')
    plt.title('Perkembangan Algoritma Genetika')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()

def genetic_algorithm(teacher_subjects, subjects, classes_list):
    population = [create_individual(teacher_subjects, subjects, classes_list) for _ in range(POPULATION_SIZE)]
    best_fitness = []
    avg_fitness = []
    worst_fitness = []
    
    for gen in range(GENERATIONS):
        fitness_scores = [fitness(ind) for ind in population]
        best_fitness.append(max(fitness_scores))
        avg_fitness.append(sum(fitness_scores) / len(fitness_scores))
        worst_fitness.append(min(fitness_scores))
        
        parents = selection(population)
        new_generation = []
        
        for _ in range(POPULATION_SIZE):
            parent1, parent2 = random.sample(parents, 2)
            child = crossover(parent1, parent2)
            child = mutate(child, teacher_subjects)
            new_generation.append(child)
            
        population = new_generation
    
    plot_convergence(best_fitness, avg_fitness, worst_fitness)
    return max(population, key=fitness)

def run_scheduler(file_data):
    random.seed(42)
    classes = file_data['classes']
    subjects = file_data['subjects']
    teachers = file_data['teachers']
    timeslots = file_data['timeslots']
    
    teacher_subjects, subjects, classes_list = preprocess_data(
        classes, subjects, teachers, timeslots
    )
    
    best_schedule = genetic_algorithm(teacher_subjects, subjects, classes_list)
    
    # Buat DataFrame jadwal dengan kolom yang benar
    schedule_df = pd.DataFrame(best_schedule, columns=[
        'Hari', 'Timeslot', 'Kelas', 'Jurusan', 'Mata Pelajaran', 'Guru', 'Ruangan'
    ])
    
    # Konversi timeslot ke format waktu
    schedule_df['Waktu'] = schedule_df['Timeslot'].map(TIMESLOTS)
    
    # Urutkan kolom untuk tampilan
    schedule_df = schedule_df[['Hari', 'Waktu', 'Kelas', 'Jurusan', 'Mata Pelajaran', 'Guru', 'Ruangan']]
    
    # Simpan hasil ke file
    os.makedirs('static', exist_ok=True)
    schedule_df.to_csv('static/schedule.csv', index=False)
    
    return schedule_df, 'chart.png'