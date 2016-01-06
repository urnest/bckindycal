import datetime
import calendar

def prevMonth(y,m):
    assert 1<=m and m<=12,m
    if m==1:
        return y-1,12
    return y,m-1

def nextMonth(y,m):
    assert 1<=m and m<=12,m
    if m==12:
        return y+1,1
    return y,m+1

def calendarWeeks(firstMonth,lastMonth):
    '''return list of weeks covering specified months %(firstMonth)s to %(lastMonth)s, with each week being a 7-item tuple, each item either None or a datetime.date'''
    '''firstMonth and lastMonth are like (2015,12)'''
    emptyWeek=[None,None,None,None,None,None,None]
    result=[emptyWeek[:]]
    m=firstMonth
    while m <= lastMonth:
        mc=calendar.Calendar(6).monthdayscalendar(*m)
        for week in mc:
            if result[-1][-1]:
                result.append(emptyWeek[:])
                pass
            for i,day in enumerate(week):
                if day:
                    result[-1][i]=result[-1][i] or \
                                   datetime.date(m[0],m[1],day)
                    pass
                pass
            pass
        m=nextMonth(*m)
        pass
    return [ tuple(_) for _ in result ]

def typename(x):
    if type(x) is types.ObjectType:
        return x.__class__.__name__
    return type(x).__name__

def termWeekName(weekNumber, termNumber):
    '''return week name for week %(weekNumber)s of term %(termNumber)s'''
    assert weekNumber is None or weekNumber >= 1, weekNumber
    assert termNumber >= 1, termNumber
    if weekNumber is None:
        return ''
    if weekNumber == 1:
        return 'Term %(termNumber)s\nweek %(weekNumber)s'%vars()
    return 'week %(weekNumber)s'%vars()

    
def weekNames(month, termNumber, termStart, termEnd):
    '''return list of term week names for month %(month)s'''
    '''month like (2016,12), termStart, termEnd are datetime.date'''
    assert termNumber >= 1, termNumber
    assert isinstance(termStart,datetime.date),typename(termStart)
    assert isinstance(termEnd,datetime.date),typename(termEnd)
    
    cweeks=calendarWeeks(prevMonth(termStart.year,termStart.month),
                         nextMonth(termEnd.year,termEnd.month))
    tweeks=[w for w in cweeks[1:-1]
            if w[-1] >= termStart and w[0] <= termEnd]
    tweeksdict={}
    for i,w in enumerate(tweeks):
        for d in w:
            tweeksdict[d]=i+1
            pass
        pass
    mweeks=calendarWeeks(month,month)
    result=[tweeksdict.get(w[0] or w[-1], None)
            for w in mweeks]
    result=[termWeekName(n,termNumber) for n in result]
    return result

def test1():
    x=calendarWeeks( (2016,1), (2016,2) )
    assert x[0]==(None, None, None, None, None, datetime.date(2016, 1, 1), datetime.date(2016, 1, 2)), (x[0],x)
    assert x[5]==(datetime.date(2016, 1, 31), datetime.date(2016, 2, 1), datetime.date(2016, 2, 2), datetime.date(2016, 2, 3), datetime.date(2016, 2, 4), datetime.date(2016, 2, 5), datetime.date(2016, 2, 6)), (x[5],x)
    assert x[9]==(datetime.date(2016, 2, 28), datetime.date(2016, 2, 29), None, None, None, None, None), (x[9],x)
    pass

def test2():
    x=calendarWeeks( (2016,4), (2016,5) )
    assert x[4][6]==datetime.date(2016,4,30),(x[4][6],x)
    assert x[5][0]==datetime.date(2016,5,1), (x[5][0],x)
    pass

def test3():
    x=weekNames( (2016,1),
                 1,
                 datetime.date(2016,1,25),
                 datetime.date(2016,3,25) )
    assert x==['', '', '', '', 'Term 1\nweek 1', 'week 2'], x
    x=weekNames( (2016,2),
                 1,
                 datetime.date(2016,1,25),
                 datetime.date(2016,3,25) )
    assert x==['week 2', 'week 3', 'week 4', 'week 5', 'week 6'], x
    x=weekNames( (2016,3),
                 1,
                 datetime.date(2016,1,25),
                 datetime.date(2016,3,25) )
    assert x==['week 6', 'week 7', 'week 8', 'week 9', ''], x
    pass

if __name__=='__main__':
    test1()
    test2()
    test3()
    pass
