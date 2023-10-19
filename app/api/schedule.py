def academic_year_number():
    from datetime import datetime, timedelta

    september_1st = datetime(datetime.now().year, 9, 1)

    september_1st -= timedelta(days=6)
    while september_1st.weekday() != 0:  # 0 - понедельник
        september_1st += timedelta(days=1)

    difference = datetime.now() - september_1st

    week_number = (difference.days // 7) + 1

    return week_number


# Проходим по всем записям и форматируем их недели
def weeks_split(schedule):
    for entry in schedule:
        weeks_list = entry.weeks.split(',')
        formatted_weeks = []

        current_range = [int(weeks_list[0])]
        for week_str in weeks_list[1:]:
            week = int(week_str)
            if week == current_range[-1] + 1:
                current_range.append(week)
            else:
                if len(current_range) == 1:
                    formatted_weeks.append(str(current_range[0]))
                else:
                    formatted_weeks.append(f"{current_range[0]}-{current_range[-1]}")
                current_range = [week]

        if len(current_range) == 1:
            formatted_weeks.append(str(current_range[0]))
        else:
            formatted_weeks.append(f"{current_range[0]}-{current_range[-1]}")

        entry.weeks = ', '.join(formatted_weeks)

    return schedule


def schedule_sort(schedule):
    # Определите порядок дней недели
    weekdays_order = ["Понедельник", "Вторник", "Среда",
                      "Четверг", "Пятница", "Суббота", "Воскресенье"]

    # Создайте функцию, которая будет использоваться для сортировки
    def custom_sort(entry):
        return weekdays_order.index(entry.day_of_week), entry.lesson_number

    # Сортируйте расписание с использованием пользовательской функции сортировки
    schedule_sorted = sorted(schedule, key=custom_sort)

    return schedule_sorted
