def academic_year_number():
    from datetime import datetime, timedelta

    september_1st = datetime(datetime.now().year, 9, 1)

    september_1st -= timedelta(days=6)
    while september_1st.weekday() != 0:  # 0 - понедельник
        september_1st += timedelta(days=1)

    difference = datetime.now() - september_1st

    week_number = (difference.days // 7) + 1

    return week_number
