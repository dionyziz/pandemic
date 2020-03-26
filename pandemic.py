from random import random, randint, choice
import itertools

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

NUM_CITIES = 10
NUM_HOUSEHOLDS_PER_CITY = 100
MAX_PEOPLE_PER_HOUSEHOLD = 6
AVG_SCHOOL_POPULATION = 20

PROB_HOUSEHOLD_SPREAD = 0.1
PROB_CITY_SPREAD = 0.0001
PROB_SCHOOL_SPREAD = 0.04
PROB_CHILD = 0.2

PROB_TRAVEL = 3 / 365
MAX_DAYS_ABROAD = 10

def spread(population, prob):
    for person in population:
        if person.infected:
            for other in population:
                r = random()
                if r < prob:
                    other.infected = True

class Group:
    def __init__(self):
        self.people = []
        self.prob_infection = 0
        self.name = ''
        self.child_groups = []

    def remove_from_group(self, person):
        self.people.remove(person)

    def from_groups(self, groups):
        self.child_groups = groups
        for group in groups:
            self.people.extend(group.people)

    def integrate(self):
        spread(self.people, self.prob_infection)

    def count_infected(self):
        # print('Population: ' + str(len(self.people)))
        return len([1 for person in self.people if person.infected])

class Person:
    def __init__(self, universe):
        self.infected = False
        self.universe = None
        self.origin_city = self.city = None
        self.traveling = False
        self.max_days_abroad = 0
        r = random()
        self.child = r < PROB_CHILD

    def integrate(self):
        if not self.traveling:
            r = random()
            if r < PROB_TRAVEL:
                # Departs to trip
                self.origin_city = self.city
                self.origin_city.remove_from_group(self)
                self.max_days_abroad = randint(1, MAX_DAYS_ABROAD)
                self.days_abroad = 0
                self.traveling = True
                self.city = choice(universe.cities)
                self.city.people.append(self)
                print('Departing to trip of duration ' + str(self.max_days_abroad))
        else:
            self.days_abroad += 1
            if self.days_abroad >= self.max_days_abroad:
                print('Returning from trip of duration ' + str(self.max_days_abroad))
                # Returns from trip
                self.traveling = False
                self.city.remove_from_group(self)
                self.city = self.origin_city
                self.city.people.append(self)

class Universe:
    def __init__(self):
        self.groups = []
        self.people = []
        self.cities = []

    def create_group(self):
        group = Group()
        self.groups.append(group)
        return group

    def create_person(self):
        person = Person(self)
        self.people.append(person)
        return person

    def integrate(self):
        for group in self.groups:
            group.integrate()

        for person in self.people:
            person.integrate()

def create_city_schools(universe, city, households):
    city_children_population = len([1 for person in city.people if person.child])
    num_schools = city_children_population // AVG_SCHOOL_POPULATION

    schools = []
    for k in range(num_schools):
        school = universe.create_group()
        school.prob_infection = PROB_SCHOOL_SPREAD
        schools.append(school)

    for household in households:
        school_num = randint(0, num_schools - 1)
        for person in household.people:
            if person.child:
                schools[school_num].people.append(person)

def create_city(universe):
    city = universe.create_group()
    city.name = 'City ' + str(i)
    city.prob_infection = PROB_CITY_SPREAD
    households = []
    for k in range(NUM_HOUSEHOLDS_PER_CITY):
        household = universe.create_group()
        household.name = 'Household ' + str(k)
        household.prob_infection = PROB_HOUSEHOLD_SPREAD
        num_people_in_household = randint(1, MAX_PEOPLE_PER_HOUSEHOLD)
        for k in range(num_people_in_household):
            person = universe.create_person()
            person.city = city
            household.people.append(person)
        households.append(household)
    city.from_groups(households)

    create_city_schools(universe, city, households)

    return city

universe = Universe()
country = universe.create_group()
country.name = 'Greece'
for i in range(NUM_CITIES):
    city = create_city(universe)
    universe.cities.append(city)
country.from_groups(universe.cities)

# Patient 0
universe.people[0].infected = True
# print('People in city: ' + str(len(country.child_groups[0].people)))
# print(country.child_groups[0].count_infected())
# print('People in country: ' + str(len(country.people)))
# print(country.count_infected())

NUM_DAYS = 60
daily_infections = []
for t in range(NUM_DAYS):
    print('Day ' + str(t) + ': ' + str(country.count_infected()))
    daily_infections.append(country.count_infected())
    universe.integrate()

t = np.arange(0.0, NUM_DAYS, 1)

fig, ax = plt.subplots()
ax.plot(t, daily_infections)

ax.set(xlabel='days', ylabel='infections',
       title='Country infections per day')
ax.grid()

plt.show()
