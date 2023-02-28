import re
import pandas as pd

def preprocess(data):
    # pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    # messages = re.split(pattern, data)[1:]
    # dates = re.findall(pattern, data)

    # df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # # convert message_date type
    # df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')

    # df.rename(columns={'message_date': 'date'}, inplace=True)

    # users = []
    # messages = []
    # for message in df['user_message']:
    #     entry = re.split('([\w\W]+?):\s', message)
    #     if entry[1:]:  # user name
    #         users.append(entry[1])
    #         messages.append(" ".join(entry[2:]))
    #     else:
    #         users.append('group_notification')
    #         messages.append(entry[0])

    # df['user'] = users
    # df['message'] = messages
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [AP]M) - (.*?): ((?:.*?\n)*?.*?)\n(?=\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [AP]M -|$)"

    # Extract messages with headers using the regular expression pattern
    matches = re.findall(pattern, data, re.DOTALL)

    # Convert the matches into a pandas DataFrame
    df = pd.DataFrame(matches, columns=['date', 'user', 'message'])

    # Convert the timestamp column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %I:%M %p')

    # Filter out group notification messages
    df = df[~df['user'].str.contains('(added|created)')]

    # Split the sender column into two columns: users and group
    users = []
    groups = []
    for sender in df['user']:
        if ' - ' in sender:
            entry = sender.split(' - ')
            users.append(entry[0])
            groups.append(entry[1])
        else:
            users.append('group_notification')
            groups.append('')
    df['sender'] = users
    df['group'] = groups
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df