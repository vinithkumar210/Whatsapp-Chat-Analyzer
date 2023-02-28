import re
import pandas as pd
def startsWithDateAndTime(s):
    # regex pattern for date.(Works only for android. IOS Whatsapp export format is different. Will update the code soon
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) (AM|PM) -'
    result = re.match(pattern, s)
    if result:
        return True
    return False
  
# Finds username of any given format.
def FindAuthor(s):
    patterns = [
        '([\w]+):',                        # First Name
        '([\w]+[\s]+[\w]+):',              # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',    # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',         # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',   # Mobile Number (US)
        '([\w]+)[\u263a-\U0001f999]+:',    # Name and Emoji              
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False

def getDataPoint(line):   
    splitLine = line.split(' - ') 
    dateTime = splitLine[0]
    date, time = dateTime.split(', ') 
    message = ' '.join(splitLine[1:])
    if FindAuthor(message): 
        splitMessage = message.split(': ') 
        author = splitMessage[0] 
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

parsedData = [] # List to keep track of data so it can be used by a Pandas dataframe
# Upload your file here
def preprocess(data):
    with open(data) as fp:
        fp.readline() # Skipping first line of the file because contains information related to something about end-to-end encryption
        messageBuffer = [] 
        date, time, author = None, None, None
        while True:
            line = fp.readline() 
            if not line: 
                break
            line = line.strip() 
            if startsWithDateAndTime(line): 
                if len(messageBuffer) > 0: 
                    parsedData.append([date, time, author, ' '.join(messageBuffer)]) 
                messageBuffer.clear() 
                date, time, author, message = getDataPoint(line) 
                messageBuffer.append(message) 
            else:
                messageBuffer.append(line)
    
    df = pd.DataFrame(parsedData, columns=['date', 'Time', 'user', 'message']) # Initialising a pandas Dataframe.
    df["date"] = pd.to_datetime(df["date"])
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
    