"""
Este script realiza la primera fase del scraping de Wallapop (Step 1).

Funcionalidades principales:
1.  **Navegación**: Abre el navegador y busca artículos basándose en los parámetros de `config.json`.
2.  **Scroll Infinito**: Realiza scrolls iniciales, detecta y pulsa el botón "Cargar más" (incluso dentro de Shadow DOM), y continúa haciendo scroll.
3.  **Extracción**: Recopila información básica de los artículos (título, precio, ID, URL).
4.  **Guardado**: Almacena los datos crudos en un archivo CSV en la carpeta `data/step1/`.
"""
import logging
import time
import pandas as pd
import setuptools # Required to patch distutils
import distutils
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .config import CONFIG, DATA_DIR
from .utils import get_coords

logger = logging.getLogger(__name__)

import undetected_chromedriver as uc

def setup_driver():
    options = uc.ChromeOptions()
    if CONFIG["scraping"].get("headless", True):
        # UC expects this for headless
        options.add_argument('--headless=new') 
        
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1920,1080')
    
    # Enable shadow-root (UC handles this well, but just in case)
    
    tc_driver_use = True
    if os.getenv("USE_STD_DRIVER", "false").lower() == "true":
        logger.info("Forcing standard Selenium driver (USE_STD_DRIVER=true)...")
        tc_driver_use = False

    if tc_driver_use:
        try:
            # uc automatically handles driver download and patching
            # version_main allows pinning major version if needed, but usually auto is best
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e:
            logger.warning(f"Failed to initialize undetected_chromedriver: {e}. Fallback to standard Selenium.")
    
    # Fallback to standard or forced standard
    options_std = webdriver.ChromeOptions()
    if CONFIG["scraping"].get("headless", True):
        options_std.add_argument('--headless')
    options_std.add_argument('--disable-gpu')
    options_std.add_argument('--no-sandbox')
    options_std.add_argument('--disable-dev-shm-usage')
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options_std)
        
    return driver

def build_url(item_config):
    name = item_config["name"]
    filters = item_config["filters"]
    
    # Use simple replacement to handle any number of words, robustly
    keywords = name.replace(" ", "%20")
    
    # Hardcoded coordinates for Madrid as requested
    # longitude=-3.69196&latitude=40.41956
    
    # Handle distance: config has "10000" (likely meters). 
    # User snippet had distance + '000' (implying km input).
    # We will use the config value directly if it seems to be meters, 
    # or append 000 if it looks like km (small integer).
    raw_dist = str(filters.get("distancia", "10000"))
    if raw_dist.isdigit() and int(raw_dist) < 100:
        dist = raw_dist + "000"
    else:
        dist = raw_dist

    # Base URL
    url = f"https://es.wallapop.com/app/search?filters_source=quick_filters&keywords={keywords}&longitude=-3.69196&latitude=40.41956&distance={dist}"


    
    # Handle Conditions (Multiple states)
    conditions_dict = filters.get("conditions")
    if conditions_dict and isinstance(conditions_dict, dict):
        active_conditions = [k for k, v in conditions_dict.items() if v]
        if active_conditions:
            joined_conditions = "%2C".join(active_conditions)
            url += f"&condition={joined_conditions}"
    
    # Legacy: Fallback to simple 'estado' if 'conditions' not present
    elif filters.get("estado") and filters.get("estado").lower() != "all":
         estado = filters.get("estado")
         url += f"&condition={estado}"
         
    return url

def scrape_item(driver, item_config):
    url = build_url(item_config)
    logger.info(f"Navigating to: {url}")
    driver.get(url)

    # DEBUG: Save HTML execution
    try:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_html_path = DATA_DIR / f"web-{timestamp_str}.html"
        # Ensure directory exists (DATA_DIR should exist, but just in case)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"DEBUG: Page source saved to {debug_html_path}")
    except Exception as e:
        logger.error(f"Failed to save debug HTML: {e}")
    
    # Cookie/Privacy Banner
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
        ).click()
        logger.info("Cookies rejected.")
    except Exception:
         logger.info("No cookie banner found or already handled.")

    driver.maximize_window()
    
    # Load More Button Strategy: Loop up to 10 times (Scroll -> Search -> Click)
    button_found = False
    logger.info("Iniciando ciclo de búsqueda del botón 'Cargar más' (10 intentos)...")

    # Script to find the button even inside Shadow DOM
    script = """
    return (function() {
        const candidates = document.querySelectorAll('walla-button');
        for (const host of candidates) {
            if (host.innerText && (host.innerText.toLowerCase().includes('cargar más') || host.innerText.toLowerCase().includes('ver más') || host.innerText.toLowerCase().includes('load'))) {
                return host;
            }
            if (host.shadowRoot) {
                const innerBtn = host.shadowRoot.querySelector('button');
                if (innerBtn) {
                        const txt = innerBtn.innerText || innerBtn.textContent;
                        if (txt && (txt.toLowerCase().includes('cargar') || txt.toLowerCase().includes('ver más') || txt.toLowerCase().includes('load'))) {
                            return innerBtn;
                        }
                }
            }
        }
        return null;
    })();
    """

    for i in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        
        # 2. Search & Click cargar más
        try:
            boton_ver_mas = driver.execute_script(script)
            if boton_ver_mas:
                print("Botón cargar más encontrado")
                logger.info(f"Botón 'cargar más' encontrado en intento {i+1} '{'boton_ver_mas.tag_name'}'--> {boton_ver_mas.tag_name}")
                
                driver.execute_script("arguments[0].scrollIntoView(true);", boton_ver_mas)
                time.sleep(1)
                try:
                    boton_ver_mas.click()
                except:
                    driver.execute_script("arguments[0].click();", boton_ver_mas)
                
                logger.info("Clicked 'Load More'")
                button_found = True
                break
        except Exception as e:
            logger.warning(f"Excepción puntual buscando botón (intento {i+1}): {e}")

    if not button_found:
         logger.error("Botón no encontrado tras 10 intentos (Scroll + Search).")
         raise Exception("Botón no encontrado")
         
    time.sleep(0.5)

    # Main Scroll Loop
    # Logic from src_old: Scroll 25 times (configurable)
    n_scrolls_cada_vez = CONFIG["scraping"].get("scrolls", 25)
    n = 0
    logger.info(f"Starting main scrolling ({n_scrolls_cada_vez} times)...")
    try:
        while n < n_scrolls_cada_vez:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            n += 1
            print(f"scroll {n}")
    except Exception as e:
        logger.error(f"Ocurrió un error durante el scroll principal: {e}")

    # Parse key elements
    items = driver.find_elements(By.CSS_SELECTOR, "a[class*='item-card_ItemCard']")
    logger.info(f"Found {len(items)} items in the DOM.")
    
    if len(items) == 0:
        screenshot_path = "error_screenshot.png"
        driver.save_screenshot(screenshot_path)
        logger.error(f"No items found! Screenshot saved to {screenshot_path}")
        logger.info(f"Current URL: {driver.current_url}")
        raise Exception("Scraping failed: No items found in DOM.")
        
    data = []
    
    for item in items:
        try:
            link = item.get_attribute('href')
            
            # Title selector: h3[class*="item-card_ItemCard__title"]
            # We try to find it within the item element
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "h3[class*='item-card_ItemCard__title']")
                title = title_elem.text.strip()
            except:
                title = item.get_attribute('title') or "No Title"

            # Price selector: strong[class*="item-card_ItemCard__price"]
            try:
                price_elem = item.find_element(By.CSS_SELECTOR, "strong[class*='item-card_ItemCard__price']")
                price = price_elem.text.strip()
            except:
                price = "0"
            
            item_id = link.split('-')[-1]
            
            data.append({
                "id": item_id,
                "time_scrap": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre": title,
                "precio": price,
                "url_articulo": link,
                "municipio": item_config["filters"].get("municipio"),
                "search_term": item_config["name"]
            })
        except Exception as e:
            logger.debug(f"Error parsing item: {e}")
            continue
            
    return pd.DataFrame(data)

def run_scraper():
    driver = setup_driver()
    try:
        all_dfs = []
        for item in CONFIG["search_items"]:
            logger.info(f"Scraping item: {item['name']}")
            
            # Retry logic: Try up to 2 times (Initial + 1 Retry)
            max_retries = 1
            for attempt in range(max_retries + 1):
                try:
                    df = scrape_item(driver, item)
                    all_dfs.append(df)
                    break # Success, exit retry loop
                except Exception as e:
                    logger.warning(f"Error scraping {item['name']} (Attempt {attempt+1}/{max_retries+1}): {e}")
                    if attempt < max_retries:
                        logger.info("Retrying...")
                        time.sleep(3) # Wait a bit before retry
                    else:
                        logger.error(f"Max retries reached for {item['name']}. Skipping.")
                        # Optionally raise if we want the WHOLE pipeline to fail if one item fails, 
                        # but usually skipping failed item is better if others succeeded. 
                        # User said "Si no, si que despliegue el error". 
                        # Let's re-raise to fail the pipeline as per earlier fail-fast instruction.
                        raise e
            
        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = DATA_DIR / "step1" / f"raw_{timestamp}.csv"
            
            # Ensure folder exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            final_df.to_csv(output_path, index=False)
            logger.info(f"Scraping finished. Saved {len(final_df)} items to {output_path}")
        else:
            logger.warning("No data scraped.")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_scraper()
