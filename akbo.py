import os, asyncio, random, time
from dataclasses import dataclass
from typing import List
import requests, httpx
from tqdm import tqdm

from akbo_ticket import grant_tickets_bulk
from akbo_history import load_last_id, save_last_id
from akbo_utils import chunked

import urllib3, warnings
warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)

LOGIN_URL   = "https://www.akbobada.com/member/passwordEncryption.html"
REFER_URL   = "https://www.akbobada.com/mypage/my_order.html"
ORDER_URL   = "https://www.akbobada.com/mypage/getOrderData.html?ran=Math.random()"
PDF_URL     = "https://www.akbobada.com/home/akbobada/archive/order/pdf/{id}{username}.pdf"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Referer": REFER_URL,
    "Connection": "keep-alive"
}

_TRANSL = str.maketrans({
    "\\": "＼",
    "/": "／",
    ":": "：",
    "*": "＊",
    "?": "？",
    '"': "＂",
    "<": "＜",
    ">": "＞",
    "|": "｜"
})


def sanitize(name: str) -> str:
    return name.translate(_TRANSL)


@dataclass
class Account:
    id: str
    pw: str


@dataclass
class Score:
    title: str
    maker: str
    part: str
    id: str
    user: str

    def pdf_url(self) -> str:
        return PDF_URL.format(id=self.id, username=self.user)

    def filename(self) -> str:
        raw = f"{self.title} - {self.maker} {self.part} ({self.id}).pdf"
        return sanitize(raw)


def login(account: Account) -> requests.Session:
    s = requests.Session()
    payload = {"flag": "login1", "mid": account.id, "mpassword": account.pw}
    r = s.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=10, allow_redirects=False, verify=False)
    r.raise_for_status()
    if "JSESSIONID" not in s.cookies:
        raise RuntimeError(f"[{account.id}] 로그인 실패")
    # print(s.cookies)
    assert_logged_in(s)
    return s

def assert_logged_in(s: requests.Session):
    r = s.get(REFER_URL, headers=HEADERS, timeout=10, allow_redirects=False, verify=False)
    if r.status_code in (301, 302, 303, 307, 308):
        raise RuntimeError(f"로그인 검증 실패(redirect): {r.headers.get('Location')}")
    if r.status_code != 200:
        raise RuntimeError(f"로그인 검증 실패: status={r.status_code}")


def scrape_scores(s: requests.Session, username: str, recovery: bool = False) -> List[Score]:
    scores: List[Score] = []
    page = 1
    last_saved = None if recovery else load_last_id(username)
    stop = False

    while not stop:
        payload = {
            "pageIndex": str(page),
            "code": "0",
            "sChoice": "new",
            "searchWord": "",
            "searchGubun": "",
            "first": "1"
        }
        r = s.post(ORDER_URL, data=payload, headers=HEADERS, timeout=10, verify=False)
        r.raise_for_status()

        try:
            data = r.json()
        except:
            print(f"[WARN] JSON 데이터 미반환, STATUS_CODE={r.status_code}")
            print(r.text[:200])

        if not data:
            break

        for song in data:
            title = song['TITLE']
            maker = song['ARTIST']
            part = song['PARTCODE']
            id = song['PARTMRID']

            sc = Score(title, maker, part, id, username)
            if not recovery and sc.id == last_saved:
                stop = True; break

            scores.append(sc)

        if stop: break

        page += 1

    if scores:
        save_last_id(username, scores[0].id)

    return list(reversed(scores))


async def async_download(scores: List[Score], s: requests.Session, outdir: str, concur: int = 6, label=""):
    # 세션의 쿠키를 httpx로 입력
    cookies = s.cookies.get_dict()
    async with httpx.AsyncClient(http2=True, headers=HEADERS, cookies=cookies, verify=False) as client:
        sem = asyncio.Semaphore(concur)

        async def fetch(sc: Score):
            async with sem:
                await asyncio.sleep(random.uniform(1, 3))
                url = sc.pdf_url()

                for attempt in range(6):
                    try:
                        r = await client.get(url, follow_redirects=False)
                        if r.status_code == 404:
                            await asyncio.sleep(2 ** attempt)
                            continue

                        # 로그인 리디렉션 확인
                        if r.status_code in (301, 302, 303, 307, 308):
                            raise RuntimeError(f"Redirect to {r.headers.get('Location')}")

                        r.raise_for_status()

                        path = os.path.join(outdir, sc.part)
                        os.makedirs(path, exist_ok=True)
                        with open(os.path.join(path, sc.filename()), "wb") as f:
                            f.write(r.content)
                    except httpx.HTTPError as e:
                        print(f"[ERR] {sc.filename()} → {e}")
                    except Exception as e:
                        print(f"[ERR] {e}")
                    finally:
                        await asyncio.sleep(random.uniform(1, 2))

        tasks = [asyncio.create_task(fetch(s)) for s in scores]
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=label):
            await f


def run_pipeline(account: Account, outdir: str, workers: int = 4, recovery: bool = False, batch=100):
    if recovery: print("복구모드 진행")

    t0 = time.time()

    s = login(account)
    scores = scrape_scores(s, account.id, recovery)
    total = len(scores)
    print(f"[{account.id}] {total}곡 발견")

    if not total:
        print(f"[{account.id}] 새 악보 없음"); return

    batches = list(chunked(scores, batch))
    for i, akbos in enumerate(batches, 1):
        print(f"[{account.id}] 배치 {i}/{len(batches)} "
              f"({len(akbos)}곡) 티켓 발급중..")

        grant_tickets_bulk(s, akbos)

        label = f"{account.id} {i}/{len(batches)}"

        asyncio.run(async_download(akbos, s, outdir, concur=workers, label=label))

    elapsed = time.time() - t0
    print(f"[{account.id}] 완료 - {total}곡, {elapsed:.1f}초")