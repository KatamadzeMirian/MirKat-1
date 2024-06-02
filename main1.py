import requests         # Для парсинга
from bs4 import BeautifulSoup         # Для парсинга
import time        #для работы со временем
import re  # для работы с текстом

# обьявление глобальных переменных
MassivURL = []  # Для хранения url
HtmlTarget = 'target_analiz.html'  # формируется для анализа оглавления раздела
PervoHod = True  #  определение первого цикла анализа
MassivKEY = ["emocratic", "epublic"]  # Для поиска ключевых слов на странице используем основу слов
HtmlAnaliz = "Analiz.html"  # формируется для анализа статьи
NameLogFail = "Log_analiz.txt"  # имя лог файла
URLTarget = "https://www.nytimes.com/section/politics" # url целевого адеса
NameUnik = "https://www.nytimes.com/2024"   # имя ссылок содержащих значение этой переменной
Nameheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} #  Что бы сайт не блокировал парсинг

# главная функция
def MainFun():

    # Функция вызова парсинга
    def call_function(function, duration_hours):
        duration_minutes = duration_hours * 60
        interval_minutes = 10

        for _ in range(duration_minutes // interval_minutes):
            function()
            time.sleep(interval_minutes * 60)

    # Функция для чтения содержимого HTML файла с указанием кодировки UTF-8
    def FunkRead(HtmlTarget):          # чтение html файла
        with open(HtmlTarget, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    # Функция поисков url
    def FunkFindUrl(Hcontent, NameUnik):
        pattern = r'"url":"(' + re.escape(NameUnik) + r'[^"]*)"'
        urls = re.findall(pattern, Hcontent)
        return_urls = list(set(urls))
        return return_urls

    # Функция парсинга
    def parsing():
        global PervoHod
        reaction = requests.get(URLTarget)
        if reaction.status_code == 200:
            Hcontent = reaction.text
            with open(HtmlTarget, "w", encoding="utf-8") as file:
                file.write(Hcontent)
            Hcontent = FunkRead(HtmlTarget)      # чтение html файла
            urls = FunkFindUrl(Hcontent, NameUnik)       # анализ html файла на наличие ссылок
            if urls:
                for url in urls:
                    if url not in MassivURL:         # если значения нет в массиве url, то добавить
                        if PervoHod == False:
                            ZapisVLog = (f"Новая статья: {url}")
                            Print = f"{(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))} -{ZapisVLog}"
                            with open(NameLogFail, "a") as file:
                                file.write(f"{Print}\n")

                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                            response = requests.get(url, headers=headers)
                            if response.status_code == 200:
                                Hcontent = response.text
                                with open(HtmlAnaliz, "w", encoding="utf-8") as file:
                                    file.write(Hcontent)
                                FunkAnalizURL()
                            else:
                                Print(f"Состояние: {response.status_code}.")

                            MassivURL.append(url)
                        else:
                            MassivURL.append(url)
                            ZapisVLog = (f"Источник на момент старта скрипта: {url}")
                            Print = f"{(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))} -{ZapisVLog}"
                            with open(NameLogFail, "a") as file:
                                file.write(f"{Print}\n")
                            response = requests.get(url, headers=Nameheaders)
                            if response.status_code == 200:
                                Hcontent = response.text
                                with open(HtmlAnaliz, "w", encoding="utf-8") as file:
                                    file.write(Hcontent)
                                FunkAnalizURL()
                            else:
                                print(f"Состояние: {response.status_code}.")
            PervoHod = False
        else:
            print(f"Состояние: {reaction.status_code}")

    # Функция для происка ключевых слов на странице URL
    def check_expressions_in_html(HtmlAnaliz, expressions):
        with open(HtmlAnaliz, "r", encoding="utf-8") as file:
            Hcontent = file.read()

        soup = BeautifulSoup(Hcontent, "html.parser")
        found_expressions = []
        for expression in expressions:
            if expression in soup.get_text():
                found_expressions.append(expression)

        return found_expressions

    def FunkAnalizURL():
        # Opening the html file utf-8 для поиска значений в кодировке Windows
        HTMLFile = open(HtmlAnaliz, "r", encoding="utf-8")
        located = check_expressions_in_html(HtmlAnaliz, MassivKEY)
        if located:
            for expression in located:
                index = HTMLFile.read()
                BS = BeautifulSoup(index, 'lxml')
                try:
                    TegNameStat = BS.find('meta', property='og:title')
                    nameStat = TegNameStat['content']
                    TegNameAnot = BS.find('meta', property='og:description')
                    anotac = TegNameAnot['content']
                    TegNameFuls = BS.find_all("meta", attrs={"name": "byl"})
                    # Извлекаем содержимое атрибута "content" для каждого найденного тега
                    for TegNameFul in TegNameFuls:
                        if "content" in TegNameFul.attrs:
                            autor = TegNameFul["content"]
                except:

                    ZapisVLog = (f"В статье имеется несколько ключевых параметров!")
                    Print = f"{(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))} -{ZapisVLog}"
                    with open(NameLogFail, "a") as file:
                        file.write(f"{Print}\n")
                ZapisVLog=(f"Статья подходит! Название статьия: {nameStat}, аннотация: {anotac}, автор: {autor}, ключевой параметр: {expression}!")
                Print = f"{(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))} -{ZapisVLog}"
                with open(NameLogFail, "a") as file:
                    file.write(f"{Print}\n")
    # Вызов функции parsing каждые 10 минут в течение 4 часов
    call_function(parsing, 4)

print("Скрипт начал работу!")
MainFun()
print("Скрипт завершил работу!")