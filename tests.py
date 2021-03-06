import time

def text_content(a):
    type_a = type(a)
    if type_a == list:
        if len(a) == 1:
            return a[0].text_content()
        else:
            return [text_content(i) for i in a]
    elif type_a == dict:
        new_dict = dict()
        for key, value in a.items():
            try:
                new_dict[key] = text_content(value)
            except AttributeError:
                new_dict[key] = value
        return new_dict
    else:
        return a.text_content()

def get(a, s):
    if type(a) == list:
        if len(a) == 1:
            return a[0].get(s)
        else:
            return [i.get(s) for i in a]
    else:
        return a.get(s)

def cssselect(a, sel):
    if type(a) == list:
        if len(a) == 1:
            r = a[0].cssselect(sel)
            if len(r) == 0: 
                print 'Warning: "%s"' % sel
            if len(r) == 1:
                return r[0]
            else:
                return r
        else:
            return [cssselect(i, sel) for i in a]
    else:
        r = a.cssselect(sel)
        if len(r) == 0:
            print 'Warning: "%s"' % sel
        if len(r) == 1:
            return r[0]
        else:
            return r

def screenshot(driver, i=[0]):
    i[0] += 1
    driver.driver.save_screenshot('%d.png' % i[0])

def wait(driver):
    while True:
        js_ready = driver.evaluate_script("document.readyState") == 'complete'
        try:
            jquery_ready = driver.evaluate_script("jQuery.active") == 0
        except:
            jquery_ready = True
        finally:
            if js_ready and jquery_ready:
                break
            time.sleep(0.05)

def visit(driver, url):
    driver.visit(url)

def click(driver, selector):
    btn = driver.find_by_css(selector)
    try:
        btn.mouse_over(); time.sleep(0.05)
        btn.click()
    except AttributeError:
        btn[0].mouse_over(); time.sleep(0.05)
        btn[0].click()        

def check_all(driver, selector):
    btns = driver.find_by_css(selector)
    for btn in btns:
        time.sleep(0.1)
        btn.click()



