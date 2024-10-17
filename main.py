import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

def open_browser():
    """Инициализирует браузер Microsoft Edge."""
    service = Service(verbose=True)
    browser = webdriver.Edge(service=service)
    print("Браузер успешно открыт.")
    return browser

def search_wikipedia(query, browser):
    """Ищет запрос на Википедии и открывает соответствующую страницу."""
    browser.get("https://ru.wikipedia.org")
    search_box = browser.find_element(By.NAME, "search")
    search_box.send_keys(query + Keys.RETURN)

def list_paragraphs(browser, delay=3):
    """Автоматически выводит параграфы текущей статьи с паузой."""
    paragraphs = browser.find_elements(By.CSS_SELECTOR, "div.mw-parser-output > p")
    if not paragraphs:
        print("Параграфы не найдены.")
        return

    for i, para in enumerate(paragraphs):
        text = para.text.strip()
        if text:  # Пропускаем пустые параграфы
            print(f"\nПараграф {i + 1}:\n{text}")
            time.sleep(delay)  # Пауза перед следующим параграфом

def list_related_articles(browser):
    """Предлагает перейти на одну из связанных страниц."""
    try:
        # Повторный поиск элементов для устранения StaleElementReferenceException
        links = browser.find_elements(By.CSS_SELECTOR, "#bodyContent a")
    except StaleElementReferenceException:
        print("Ошибка: элементы обновились, выполняем повторный поиск...")
        links = browser.find_elements(By.CSS_SELECTOR, "#bodyContent a")

    valid_links = [
        link for link in links
        if link.get_attribute("href") and "/wiki/" in link.get_attribute("href")
           and not link.get_attribute("href").startswith("https://ru.wikipedia.org/wiki/Служебная:")
    ]

    if not valid_links:
        print("Связанные статьи не найдены.")
        return False

    print("\nСвязанные статьи:")
    for i, link in enumerate(valid_links[:10], 1):  # Ограничиваем выбор 10 статьями
        print(f"{i}. {link.text or 'Без названия'}")

    choice = input("Введите номер статьи для перехода или 'q' для возврата: ")
    if choice.isdigit() and 1 <= int(choice) <= len(valid_links):
        selected_link = valid_links[int(choice) - 1]
        try:
            url = selected_link.get_attribute("href")  # Получаем URL безопасно
            print(f"Переход на: {url}")
            browser.get(url)
            return True
        except StaleElementReferenceException:
            print("Ошибка: элемент больше недоступен.")
            return False

    return False

def navigate_article(browser):
    """Предлагает действия для текущей статьи."""
    while True:
        print("\nВыберите действие:")
        print("1. Листать параграфы текущей статьи")
        print("2. Перейти на связанную статью")
        print("3. Выйти из программы")

        choice = input("Введите номер действия: ")
        if choice == "1":
            list_paragraphs(browser)
        elif choice == "2":
            if not list_related_articles(browser):
                print("Нет доступных связанных статей.")
        elif choice == "3":
            print("Выход из программы...")
            break
        else:
            print("Неверный ввод. Пожалуйста, попробуйте снова.")

def main():
    browser = open_browser()
    try:
        query = input("Введите запрос для поиска на Википедии: ")
        search_wikipedia(query, browser)
        navigate_article(browser)
    finally:
        browser.quit()
        print("Браузер закрыт.")

if __name__ == "__main__":
    main()