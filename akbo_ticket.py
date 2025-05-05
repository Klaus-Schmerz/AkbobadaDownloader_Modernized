import requests

AJAX_TICKET_URL = "https://www.akbobada.com/pdfView.html"
REFER_URL = "https://www.akbobada.com/mypage/my_order.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Referer": REFER_URL,
    "Connection": "keep-alive"
}


def grant_ticket(s: requests.Session, score) -> None:
    payload = {
        "partID": score.id,
        "bought1": "new",
        "path1": "/WEB-INF/views/mypage/MYP-02-01.jsp",
        "title1": score.title
    }
    r = s.post(AJAX_TICKET_URL, data=payload, headers=HEADERS, timeout=10, verify=False)
    r.raise_for_status()


def grant_tickets_bulk(s: requests.Session, scores: list) -> None:
    for sc in scores:
        grant_ticket(s, sc)
    print("티켓 발급 완료")