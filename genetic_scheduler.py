import random
import pandas as pd
import matplotlib.pyplot as plt

POPULATION_SIZE = 10
GENERATIONS = 10
MUTATION_RATE = 0.1

def preprocess_data(classes, subjects, teachers):
    subjects['Department'] = subjects['Department'].astype(str)
    classes['Department'] = classes['Department'].astype(str)

    teacher_subjects = {}
    for _, row in teachers.iterrows():
        teacher = row['Teacher']
        subject = row['Subject']
        department = row['Department']
        if teacher not in teacher_subjects:
            teacher_subjects[teacher] = []
        teacher_subjects[teacher].append((subject, department))

    return teacher_subjects, subjects

def create_individual(teacher_subjects, subjects):
    schedule = []
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
    timeslots_per_day = {'Senin': list(range(1, 10)), 'Selasa': list(range(1, 10)), 'Rabu': list(range(1, 10)),
                         'Kamis': list(range(1, 10)), 'Jumat': list(range(1, 6)), 'Sabtu': list(range(1, 7))}

    classes_list = ['12 IPA 1', '12 IPA 2', '12 IPA 3', '12 IPA 4', '12 IPA 5',
                    '12 IPA 6', '12 IPA 7', '12 IPS 1', '12 IPS 2', '12 IPS 3', '12 Agama']

    for class_name in classes_list:
        for day in days:
            for timeslot in timeslots_per_day[day]:
                subject_row = subjects.sample(n=1).iloc[0]
                subject = subject_row['Subject']
                department = subject_row['Department']
                valid_teachers = [teacher for teacher, subjects_list in teacher_subjects.items()
                                  if any(subj == subject and dept == department for subj, dept in subjects_list)]
                if valid_teachers:
                    teacher = random.choice(valid_teachers)
                    schedule.append((day, subject, class_name, teacher, timeslot))
    return schedule

def fitness(schedule):
    conflicts = 0
    teacher_timeslot = {}
    class_timeslot = {}

    for entry in schedule:
        day, subject, class_id, teacher, timeslot = entry

        teacher_slot_key = (teacher, day, timeslot)
        if teacher_slot_key in teacher_timeslot:
            conflicts += 1
        else:
            teacher_timeslot[teacher_slot_key] = 1

        class_slot_key = (class_id, day, timeslot)
        if class_slot_key in class_timeslot:
            conflicts += 1
        else:
            class_timeslot[class_slot_key] = 1

    return 1 / (1 + conflicts)

def selection(population):
    return sorted(population, key=lambda x: fitness(x), reverse=True)[:2]

def crossover(parent1, parent2):
    cut = random.randint(1, min(len(parent1), len(parent2)) - 1)
    return parent1[:cut] + parent2[cut:]

def mutate(individual):
    if random.random() < MUTATION_RATE:
        idx = random.randint(0, len(individual) - 1)
        days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
        new_day = random.choice(days)
        new_timeslot = random.randint(1, 9)
        individual[idx] = (new_day, individual[idx][1], individual[idx][2], individual[idx][3], new_timeslot)
    return individual

def plot_convergence(best, avg, worst, save_path='static/chart.png'):
    plt.figure(figsize=(10, 6))
    plt.plot(best, label='Best Fitness', color='green')
    plt.plot(avg, label='Average Fitness', color='blue')
    plt.plot(worst, label='Worst Fitness', color='red')
    plt.xlabel('Generation')
    plt.ylabel('Fitness Value')
    plt.title('Grafik Konvergensi Algoritma Genetika')
    plt.legend()
    plt.grid()
    plt.savefig(save_path)
    plt.close()

def genetic_algorithm(teacher_subjects, subjects):
    population = [create_individual(teacher_subjects, subjects) for _ in range(POPULATION_SIZE)]
    best_fitness, avg_fitness, worst_fitness = [], [], []

    for _ in range(GENERATIONS):
        fitness_values = [fitness(ind) for ind in population]
        best_fitness.append(max(fitness_values))
        avg_fitness.append(sum(fitness_values) / len(fitness_values))
        worst_fitness.append(min(fitness_values))
        parents = selection(population)
        new_population = [mutate(crossover(parents[0], parents[1])) for _ in range(POPULATION_SIZE)]
        population = new_population

    plot_convergence(best_fitness, avg_fitness, worst_fitness)
    return max(population, key=fitness)

def run_scheduler(file_data):
    random.seed(42)
    classes = file_data['classes']
    subjects = file_data['subjects']
    teachers = file_data['teachers']
    teacher_subjects, subjects = preprocess_data(classes, subjects, teachers)
    best_schedule = genetic_algorithm(teacher_subjects, subjects)
    df = pd.DataFrame(best_schedule, columns=['Day', 'Subject', 'Class', 'Teacher', 'Timeslot'])
    return df, 'chart.png'