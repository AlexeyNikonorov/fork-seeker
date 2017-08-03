from itertools import product

#def f(k1, k2, k3):
#    return k1 + k2 + k3 - (k1-1)*(k2-1)*(k3-1)
def f(k1, k2, k3):
    return 1./k1 + 1./k2 + 1./k3

def _max(k):
    k_max = 0
    for ki in k:
        if type(ki) == str:
            continue
        elif ki > k_max:
            k_max = ki
    return k_max

def analyze(events):
    home = []
    draw = []
    away = []

    for event in events:
        k1 = event['bet home']
        k2 = event['bet draw']
        k3 = event['bet away']
        R = f(k1, k2, k3)
        print '%s: %.2f' % (event.bookmaker, R,)
        home.append(k1)
        draw.append(k2)
        away.append(k3)
    
    k1_best = _max(home)
    k2_best = _max(draw)
    k3_best = _max(away)
    
    R_best = f(k1_best, k2_best, k3_best)

    print 'best posible: %.2f\n' % R_best
    return R_best

def find_(Ii, L):
    s = [Ii]
    for Li in L:
        try:
            j = Li.index(Ii)
        except ValueError:
            continue
        else:
            s.append(Li.pop(j))
    if len(s) > 1:
        return s
    else:
        return None

def same_events(bookmakers):
    L = []
    for bm in bookmakers:
        events = []
        for day_events in bm.events.values():
            events += day_events
        L.append(events)
    for k in range(len(L)):
        I = L.pop(0)
        for i in range(len(I)):
            Ii = I.pop(0)
            s = find_(Ii, L)
            if not s:
                I.append(Ii)
            else:
                yield s
        L.append(I)

def check_forks(bookmakers):
    forks = []
    Rs = []
    i = 0
    for events in same_events(bookmakers):
        i += 1
        event_label = 'Event #%d' % i
        print '%s%s%s' % ('_'*10, event_label, '_'*10,)
        for j, event in enumerate(events):
            print '%d) %s:' % (j+1, event.bookmaker)
            print event

        try:
            R = analyze(events)
            Rs.append(R)
            if R < 1:
                forks.append((R, events))
        except TypeError:
            continue

    print '_'*20
    print '%d events checked' % i
    print '%d forks found' % len(forks)
    if i != 0:
        print 'best result: %.2f\n\n' % min(Rs)

    for i, (R, forked) in enumerate(forks):
        print '%sFork #%d%s' % ('_'*10, i+1, '_'*10)
        for j, event in enumerate(forked):
            print '%d) %s:' % (j+1, event.bookmaker)
            print event
            print '%.2f' % R

if __name__ == '__main__':
    from Leon import Leon
    from WilliamHill import WilliamHill
    from BetOnline import BetOnline
    from splinter import Browser

    driver = Browser()
    print 'Leon loading'
    bm1 = Leon(driver)
    bm1.load()
    print bm1
    print 'WilliamHill loading'
    bm2 = WilliamHill(driver)
    bm2.load()
    print bm2
    print 'BetOnline loading'
    bm3 = BetOnline(driver)
    bm3.load()
    print bm3
    print 'Done:'

    bm1.save()
    bm2.save()
    bm3.save()

    check_forks((bm1, bm2, bm3))






