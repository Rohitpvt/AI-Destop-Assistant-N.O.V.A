import webbrowser as wb
from core.logger import log_event

def open_website(url, query_for_log=None):
    """Opens a website in the default browser."""
    wb.open(url)
    if query_for_log:
        log_event(query_for_log, "Website", "Success")
