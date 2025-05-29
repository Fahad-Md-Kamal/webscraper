import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="function")
def driver():
    service = Service(executable_path="./chromedriver")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("http://www.python.org")
    yield driver
    driver.quit()

# def test_title_contains_python(driver):
#     assert "Python" in driver.title

# @pytest.mark.parametrize("query", ["selenium", "flask", "numpy", "pandas", "matplotlib", "requests", "pytest", "beautifulsoup", "tensorflow", "keras", "scikit-learn", "django", "sqlalchemy", "sqlparse", "pylint", "unittest", "pytest", "fastapi", "pydantic"])
# def test_search_query_extended(driver, query):
#     elem = driver.find_element(By.NAME, "q")
#     elem.clear()
#     elem.send_keys(query)
#     elem.send_keys(Keys.RETURN)
#     assert "No results found." not in driver.page_source

# def test_navigation_to_about(driver):
#     about_link = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.LINK_TEXT, "About"))
#     )
#     about_link.click()
#     assert "About Python" in driver.title

# @pytest.mark.parametrize(
#     "xpath,expected_title",
#     [
#         ("//a[text()='About']", "About Python"),
#         ("//a[text()='Documentation']", "Our Documentation"),
#         ("//a[text()='Downloads']", "Download Python"),
#         ("//a[text()='Community']", "Our Community"),
#         ("//a[text()='Success Stories']", "Our Success Stories"),
#         ("//a[text()='News']", "Our Blogs"),
#         ("//a[text()='Events']", "Our Events"),
#     ]
# )
# def test_navigation_links(driver, xpath, expected_title):
#     link = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, xpath))
#     )
#     link.click()
#     assert expected_title in driver.title

# def test_mouse_hover_on_about(driver):
#     from selenium.webdriver.common.action_chains import ActionChains

#     about_link = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.LINK_TEXT, "About"))
#     )
#     actions = ActionChains(driver)
#     actions.move_to_element(about_link).perform()

#     # Check for submenu items after hover
#     submenu_items = [
#         "Applications",
#         "Quotes",
#         "Getting Started",
#         "Help",
#         "Python Brochure"
#     ]
#     for item in submenu_items:
#         submenu = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.LINK_TEXT, item))
#         )
#         assert submenu.is_displayed()

def test_scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    scroll_position = driver.execute_script("return window.pageYOffset + window.innerHeight;")
    page_height = driver.execute_script("return document.body.scrollHeight;")
    assert abs(scroll_position - page_height) < 5  # Allow small difference
