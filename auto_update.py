from datetime import datetime
import json


def get_data():
    try:
        with open('last_update.json', mode='r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print('No last_update.json')
        update_date()
    return data

def update_date():
    with open('last_update.json', mode='w') as f:
        data = {'last_date': datetime.today().strftime('%Y-%m-%d')}
        json.dump(data, f)

def check_if_updated():
    data = get_data()
    print(data)

    today = datetime.today().strftime('%Y-%m-%d')
    print(today)
    print(data['last_date'])
    if today > data['last_date']:
        return False
    else:
        return True

def check_if_week_passed():
    current_week = datetime.today().isocalendar()[1]
    data = get_data()
    print(data['last_date'])
    updated_week = datetime.strptime(data['last_date'], "%Y-%m-%d").isocalendar()[1]
    if current_week > updated_week:
        return True
    else:
        return False


# print(check_if_updated())
# update_date()
# print(check_if_updated())
# print(datetime.today().strftime('%Y-%m-%d'))
# print(check_if_week_passed())
# print(datetime.strptime('2025-12-07', "%Y-%m-%d").isocalendar()[1])
# print(datetime.strptime('2025-12-08', "%Y-%m-%d").isocalendar()[1])