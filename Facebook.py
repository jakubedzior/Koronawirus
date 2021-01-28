from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


print("Opening facebook...")

post = '''

Jeśli sposób w jaki skonstruowany jest wykres nie jest dość czytelny, opisuję go bardziej poniżej.

-----

Wykres słupkowy ukazuje faktyczne, oficjalne dane. Wykres przerywany, naniesiony na wykres słupkowy to uśrednione dane (z 7 okolicznych dni), aby były bardziej czytelne.

Pionowa ciemno-szara kreska jest w miejscu, gdzie kończą się dane (dzień obecny) i zaczynają przewidywania na najbliższy miesiąc.

Zacieniowany obszar wokół głównej osi przewidywań to niepewność przewidywań. Zależy głównie od tego, jak bardzo zmienne są dane.

Przewidywania są utworzone na podstawie wykresów - to znaczy, że mogą wcale się nie sprawdzić, jeśli np. zmieni się sytuacja w kraju. 
Przewidywania nie przewidzą sytuacji nieprzewidywalnych 😉, polecam więc traktować je orientacyjnie.

Źródło danych:
https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/Poland_medical_cases
A konkretnie (bo Wikipedię prawie codziennie uzupełniam nowymi danymi z Ministerstwa Zdrowia):
https://twitter.com/MZ_GOV_PL

Kod programu do tworzenia wykresów:
https://github.com/jakubedzior/MyPortfolio/tree/master/Koronawirus'''


copy(post)

driver = webdriver.Chrome()
driver.get('https://www.facebook.com')
delay = 10

email = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
    (By.ID, 'email')))
my_email = os.environ.get('my_email')
email.send_keys(my_email)

password = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
    (By.ID, 'pass')))
my_password = os.environ.get('my_pass_90')
password.send_keys(my_password)

try:
    login_button = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
        (By.ID, 'u_0_d')))
    login_button.click()
except:
    pass

os.startfile(os.getcwd()+'\\'+'png')

# try:
#     post_area = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
#         (By.CLASS_NAME, 'm9osqain.a5q79mjw')))
#     post_area.click()

#     post_text_box= WebDriverWait(driver, delay).until(EC.presence_of_element_located(
#         (By.CLASS_NAME, 'll8tlv6m.o6r2urh6.j83agx80.buofh1pr.datstx6m.l9j0dhe7.oh7imozk')))
#     post_text_box.click()

#     hotkey('ctrl', 'v', interval=0.1)
# except TimeoutException:
#     print('Class names not matching.')
# except ElementNotInteractableException:
#     print('Element not iterable')
