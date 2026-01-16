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

import random
from fake_useragent import UserAgent

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

def save_debug_html(driver, prefix="error"):
    """Saves the current page source and screenshot to files for debugging."""
    try:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save HTML
        debug_html_path = DATA_DIR / f"{prefix}-{timestamp_str}.html"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        # Save Screenshot
        debug_png_path = DATA_DIR / f"{prefix}-{timestamp_str}.png"
        driver.save_screenshot(str(debug_png_path))
        
        # Also overwrite the 'latest' error screenshot for easy access
        driver.save_screenshot("error_screenshot.png")
        
        logger.info(f"DEBUG: Saved HTML to {debug_html_path} and Screenshot to {debug_png_path}")
    except Exception as e:
        logger.error(f"Failed to save debug artifacts: {e}")

def check_for_block(driver):
    """Checks if the page is blocked by CloudFront or other anti-bot protections."""
    try:
        title = driver.title
        page_source = driver.page_source
        
        if "ERROR" in title or "The request could not be satisfied" in title or "Request blocked" in page_source:
             logger.critical("🚨 BLOCK DETECTED: CloudFront/Filter detected our request! 🚨")
             logger.critical(f"Title: {title}")
             save_debug_html(driver, prefix="blocked")
             return True
             
        return False
    except Exception as e:
        logger.error(f"Error checking for block: {e}")
        return False

def random_sleep(min_seconds=0.5, max_seconds=2.0):
    """Sleeps for a random amount of time to simulate human behavior."""
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

def setup_driver():
    options = uc.ChromeOptions()
    
    # 1. Random User-Agent
    try:
        ua = UserAgent()
        random_ua = ua.random
        logger.info(f"Using Random User-Agent: {random_ua}")
        options.add_argument(f'user-agent={random_ua}')
    except Exception as e:
        logger.warning(f"Could not load fake-useragent: {e}. using default.")

    # More anti-detection measures
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-popup-blocking')
    
    # Referer Spoofing (Try to look like we come from Google)
    options.add_argument('--referrer=https://www.google.com/')
    
    # 2. Random Window Size
    window_sizes = ["1920,1080", "1366,768", "1536,864", "1440,900", "1280,720"]
    selected_size = random.choice(window_sizes)
    logger.info(f"Using Random Window Size: {selected_size}")
    options.add_argument(f'--window-size={selected_size}')

    if CONFIG["scraping"].get("headless", True):
        # UC expects this for headless
        options.add_argument('--headless=new') 
    else:
        # If not headless, disable gpu can cause issues
        pass
    
    tc_driver_use = True
    if os.getenv("USE_STD_DRIVER", "false").lower() == "true":
        logger.info("Forcing standard Selenium driver (USE_STD_DRIVER=true)...")
        tc_driver_use = False

    if tc_driver_use:
        try:
            # uc automatically handles driver download and patching
            # version_main allows pinning major version if needed, but usually auto is best
            # use_subprocess=True can help with stability
            driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            
            # Give the driver a moment to stabilize before returning
            time.sleep(2)
            logger.info("Driver initialized successfully")
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
    random_sleep(2.0, 4.0) # Jitter after load
    
    if check_for_block(driver):
        raise Exception("Navegación bloqueada por CloudFront/Wallapop (Title: ERROR)")
    
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
    # Improved script to avoid clicking the wrong button (upload/login)
    script = """
    return (function() {
        // Search ONLY within the search results container to avoid other buttons
        const searchContainer = document.querySelector('main') || document.body;
        
        // Target class from logs
        const targetClass = 'walla-button__button walla-button__button--medium walla-button__button--primary';
        
        const candidates = searchContainer.querySelectorAll('walla-button');
        for (const host of candidates) {
            // SKIP buttons that are part of navigation/header/upload areas
            const parent = host.closest('[role="banner"], nav, header, [class*="upload"], [class*="nav"]');
            if (parent) continue;
            
            // Priority 1: Check host text for "Cargar más" / "Load more" ONLY
            if (host.innerText) {
                const text = host.innerText.toLowerCase();
                if (text.includes('cargar más') || text.includes('ver más artículos') || text.includes('load more')) {
                    console.log('Found button by host text:', host.innerText);
                    return host;
                }
            }
            
            // Check in Shadow DOM
            if (host.shadowRoot) {
                const innerBtn = host.shadowRoot.querySelector('button');
                if (innerBtn) {
                    const txt = (innerBtn.innerText || innerBtn.textContent || '').toLowerCase();
                    // Be very specific: only "cargar más" or "ver más artículos", NOT just "ver" or "cargar"
                    if (txt === 'cargar más' || txt === 'ver más artículos' || txt === 'load more' || txt === 'see more') {
                        console.log('Found button in shadow DOM:', txt);
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
        random_sleep(0.5, 1.5) # Jitter between scrolls
        
        # 2. Search & Click cargar más
        try:
            boton_ver_mas = driver.execute_script(script)
            
            # Fallback: XPath provided by user with detailed logging
            if not boton_ver_mas:
                try:
                    xpath_selector = '//*[@id="__next"]/main/div/div/div/div[2]/section/div[3]/button'
                    # Use JavaScript to get detailed info about the element
                    element_info = driver.execute_script("""
                        const xpath = arguments[0];
                        const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        const element = result.singleNodeValue;
                        
                        if (element) {
                            return {
                                found: true,
                                tagName: element.tagName,
                                id: element.id,
                                className: element.className,
                                innerText: element.innerText || element.textContent || ''
                            };
                        }
                        return {found: false};
                    """, xpath_selector)
                    
                    if element_info and element_info.get('found'):
                        logger.info(f"XPath fallback - Elemento encontrado: Tag={element_info.get('tagName')}, ID='{element_info.get('id')}', Class='{element_info.get('className')}', Text='{element_info.get('innerText')}'")
                        boton_ver_mas = driver.find_element(By.XPATH, xpath_selector)
                        logger.info("Botón encontrado mediante XPath fallback.")
                    else:
                        logger.warning("XPath fallback no encontró ningún elemento.")
                except Exception as e:
                    logger.warning(f"Error en XPath fallback: {e}")
                    pass # Keep None if not found

            if boton_ver_mas:
                # Capture identifiers for future reference
                btn_id = boton_ver_mas.get_attribute("id")
                btn_class = boton_ver_mas.get_attribute("class")
                logger.info(f"Identificadores del botón para futuro uso: ID='{btn_id}', Class='{btn_class}'")
                
                driver.execute_script("arguments[0].scrollIntoView(true);", boton_ver_mas)
                random_sleep(0.5, 1.0)
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
         save_debug_html(driver, prefix="error_load_more")
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
            random_sleep(1.0, 2.5) # Random sleep between main scrolls
            
            if check_for_block(driver):
                 raise Exception("Bloqueo detectado durante el scroll.")
                 
            n += 1
            print(f"scroll {n}")
    except Exception as e:
        logger.error(f"Ocurrió un error durante el scroll principal: {e}")

    # Parse key elements
    items = driver.find_elements(By.CSS_SELECTOR, "a[class*='item-card_ItemCard']")
    logger.info(f"Found {len(items)} items in the DOM.")
    
    if len(items) == 0:
        logger.info(f"Current URL: {driver.current_url}")
        
        # Save HTML & Screenshot for debug
        save_debug_html(driver, prefix="error_no_items")
        
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
            
            # No Retry logic: Fail fast as requested
            try:
                df = scrape_item(driver, item)
                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Error scraping {item['name']}: {e}")
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
