import threading
import multiprocessing
import time

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
    from Betway import Betway
    from splinter import Browser

    ts = time.time()

    driver = Browser()
    #driver = Browser('phantomjs', load_images=False, wait_time=5)
    bm1 = Leon(driver)
    bm1.load(); bm1.save()
    bm2 = WilliamHill(driver)
    bm2.load(); bm2.save()
    bm3 = BetOnline(driver)
    bm3.load(); bm3.save()
    bm4 = Betway(driver)
    bm4.load(); bm4.save()
    driver.quit()
    check_forks((bm1, bm2, bm3, bm4))
    
    print time.time() - ts

    '''
    ts = time.time()

    driver1 = Browser()
    driver2 = Browser()
    driver3 = Browser()

    bm1 = Leon(driver=driver1)
    bm2 = WilliamHill(driver=driver2)
    bm3 = BetOnline(driver=driver3)

    Th1 = threading.Thread(target=bm1.load)
    Th2 = threading.Thread(target=bm2.load)
    Th3 = threading.Thread(target=bm3.load)
    #Th1 = multiprocessing.Process(target=bm1.load)
    #Th2 = multiprocessing.Process(target=bm2.load)
    #Th3 = multiprocessing.Process(target=bm3.load)

    Th1.start()
    Th2.start()
    Th3.start()

    Th1.join()
    Th2.join()
    Th3.join()
        
    driver1.quit()
    driver2.quit()
    driver3.quit()

    check_forks((bm1, bm2, bm3)) 
    print time.time() - ts
   
    '''


    





