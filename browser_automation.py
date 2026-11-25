
from playwright.sync_api import sync_playwright, Playwright  # type: ignore
from playwright.sync_api import Error as PlaywrightError # type: ignore
from playwright.sync_api import Page, Locator  # type: ignore
import re
from pathlib import Path
from profiles import Profile

ANDRE_PROFILE = Profile(
    "Andre", 
    "Austin", 
    "andreaustinx@gmail.com", 
    "https://www.linkedin.com/in/andre-austin",
    "https://www.github.com/andreaustin",
    r"C:\Users\andre\OneDrive\Documents\coding_projects\jobclick\Andre_Resume.pdf"
)
def check_missing_fields(page: Page) -> list:
    missing = []

    for frame in page.frames:
        fields = frame.locator("input:not([type=hidden]), textarea, select")

        for i in range(fields.count()):
            field = fields.nth(i)

            try:
                if not field.is_visible() or not field.is_enabled():
                    continue

                field_type = field.get_attribute("type") or ""
                if field_type in ["submit", "button", "reset", "file"]:
                    continue

                label = field.get_attribute("aria-label") or field.get_attribute("placeholder") or ""
                field_id = field.get_attribute("id")
                required = field.get_attribute("required") is not None or field.get_attribute("aria-required") == "true"

                if field_id:
                    label_element = frame.locator(f'label[for="{field_id}"]')
                    if label_element.count():
                        label = label_element.first.inner_text().strip()

                if not required and not re.search(r"\*", label):
                    continue

                value = field.input_value().strip()

                if field_type == "checkbox":
                    if not field.is_checked():
                        missing.append(label.lower() or "Required checkbox")
                elif field_type == "radio":
                    name = field.get_attribute("name")
                    if name and not frame.locator(f'input[type="radio"][name="{name}"]:checked').count():
                        missing.append(label.lower() or name)
                elif not value or value in ["Select", "Please select"]:
                    missing.append(label.lower() or f"Required field {i + 1}")

            except Exception:
                continue

    if missing:
        print("Missing required fields:", missing)
    else:
        print("No missing required fields found.")

    return missing

def upload_resume(page: Page, file_path: str) -> bool:
    file_path = str(Path(file_path).resolve())

    for frame in page.frames:
        for selector in ['input[type="file"]', 'input[accept*=".pdf" i]', 'input[accept*=".doc" i]']:
            locator = frame.locator(selector)
            for i in range(locator.count()):
                element = locator.nth(i)
                try:
                    element.set_input_files(file_path, timeout=10000)
                    print(f"Resume uploaded: {file_path}")
                    return True
                except Exception:
                    continue

    print("Resume upload input not found")
    return False

def find_apply_button(page: Page) -> Locator | None:
    pattern = re.compile(r"^(apply|apply now|apply for this job|apply to this job)$", re.I)

    for frame in page.frames:
        for role in ["button", "link"]:
            locator = frame.get_by_role(role, name=pattern)
            for i in range(locator.count()):
                element = locator.nth(i)
                try:
                    if element.is_visible() and element.is_enabled():
                        print(f"Found Apply: {role} | {frame.url}")
                        return element
                except Exception:
                    continue

    return None

def ziprecruiter_apply(context, page):
    apply_button = page.get_by_role("link", name="Apply", exact=True).last
    apply_button.wait_for(state="visible", timeout=30000)

    # Capture the new tab opened by clicking Apply
    with context.expect_page(timeout=30000) as new_page_info:
        apply_button.click(timeout=30000)

    application_page = new_page_info.value
    application_page.wait_for_load_state("domcontentloaded", timeout=60000)
    application_page.wait_for_timeout(2000)
    application_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Usage
    next_apply_button = find_apply_button(application_page)
    if next_apply_button:
        next_apply_button.wait_for(state="visible",timeout=30000)
        next_apply_button.click(timeout=15000)
    else:
        print("Apply button not found")   

    application_page.wait_for_timeout(2000)

    return application_page

def apply(playwright: Playwright, url: str = "http://google.com"):
    remote_port_file = Path(
        r"C:\Users\andre\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    )
    your_session_port = remote_port_file.read_text().splitlines()
    rd_endpoint = (f"ws://127.0.0.1:{your_session_port[0].strip()}" f"{your_session_port[1].strip()}")
    browser = playwright.chromium.connect_over_cdp(rd_endpoint)

    # Create a dedicated tab instead of reusing an existing one
    context = browser.contexts[0]
    page = context.new_page()

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)

        # ZIPRECRUITER
        if "ziprecruiter" in url.lower():
            final_application_page = ziprecruiter_apply(context, page)
            upload_resume(final_application_page, ANDRE_PROFILE.getResume())
            final_application_page.wait_for_load_state("domcontentloaded", timeout=60000)
            missing = check_missing_fields(final_application_page)
            if missing:
                if "github" in missing:
                    # DO something
                    pass
                print("Missing required fields:", missing)
            else:
                print("All required fields completed.")
        # # INDEED
        # elif "indeed" in url.lower():
        #     apply_button = page.get_by_role(
        #         "link", name="Apply", exact=True
        #     ).last
        #     apply_button.wait_for(
        #         state="visible",
        #         timeout=30000
        #     )

        #     # Click Apply
        #     apply_button.click(timeout=30000)

        #     page.wait_for_timeout(2000)

        #     page.screenshot(
        #         path="application.png",
        #         full_page=True
        #     )
    except PlaywrightError as e:
        print("Playwright error:", e)
    finally:
        # Close only tabs created by this function
        if not page.is_closed():
            page.close()

def apply_to_job(url: str):
    with sync_playwright() as playwright:
        apply(playwright, url)
