import json
from random import choice

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from datacenter.models import Commendation, Schoolkid, Lesson, Chastisement, Mark


COMMENDATIONS_FILEPATH = 'possible_commendations.json'


def find_schoolkid(schoolkid_name) -> Schoolkid:
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
        return schoolkid
    except Schoolkid.MultipleObjectsReturned:
        print('Найдено несколько учеников, необходимо уточнить ФИО ученика.')
    except Schoolkid.ObjectDoesNotExist:
        print('Ничего не найдено. Проверьте, правильно ли вы указали имя ученика.')


def create_commendation(schoolkid, subject_title):
    lessons = Lesson.objects.filter(year_of_study=schoolkid.year_of_study,
                                    group_letter=schoolkid.group_letter,
                                    subject__title__exact=subject_title)
    if not lessons:
        print('Уроки не обнаружены, название предмета написано без ошибок?')
    else:
        last_lesson = lessons.order_by('date').last()
        try:
            with open(commendations_file, encoding='utf8') as json_file:
                data = json.load(json_file)
                possible_commendations = data.get('commendations')
                commendation_text = choice(possible_commendations)
        except FileNotFoundError:
            commendation_text = input(f'Файл {commendations_file} не обнаружен. Введите текст похвалы: ')
        Commendation.objects.create(text=commendation_text,
                                    created=last_lesson.date,
                                    schoolkid=schoolkid,
                                    subject=last_lesson.subject,
                                    teacher=last_lesson.teacher)
        print(f'Похвала от учителя {last_lesson.teacher.full_name} за последний урок добавлена!')


def remove_chastisements(schoolkid):
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    if not chastisements:
        print('Замечаний нет!')
    else:
        chastisements.delete()
        print('Замечания удалены!')


def fix_marks(schoolkid):
    bad_marks = Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3])
    if not bad_marks:
        print('Плохих оценок не обнаружено. Молодец!')
    else:
        print(f'Плохих оценок: {bad_marks.count()}. Сейчас исправим!')
        bad_marks.update(points=5)
        print('Плохие оценки исправлены!')
