import requests
import re
from bs4 import BeautifulSoup as bs
from unicodedata import normalize
from datetime import datetime, timedelta
from typing import Optional, List, AnyStr
from menu_types import Menu, DailyMenu


class BUFSMeals:
    WEEKLY_MEAL_URL = 'http://www.bufs.ac.kr/bbs/my/ajax.view.skin.php?bo_table=weekly_meal&wr_id=1'

    def __init__(self, fetch_on_init=True):
        self.last_updated = None
        self.weekly_meals = []

        if fetch_on_init:
            self.refresh()

    def is_valid(self) -> bool:
        if self.last_updated is None or datetime.now() - self.last_updated > timedelta(minutes=30):
            return False
        return True
    

    def get_weekly(self) -> List[DailyMenu]:
        if not self.is_valid():
            self.refresh()
        return self.weekly_meals


    def get_daily(self, date: Optional[datetime.date] = None) -> DailyMenu:
        if not self.is_valid():
            self.refresh()
        
        for day in self.weekly_meals:
            if day['date'] == date:
                return day
        return None

    def refresh(self) -> None:
        page = requests.get(self.WEEKLY_MEAL_URL)
        if page.status_code != 200:
            raise ConnectionError(f"웹 페이지가 {page.status_code}를 반환했습니다")

        soup = bs(page.text, "lxml")
        # tbls = soup.select('table.__se_tbl')
        tbls = soup.find_all('table', class_='__se_tbl')
        weekly_meals = []

        # 첫 번째는 운영시간, 마지막은 교직원식당임
        for idx, item in enumerate(tbls[1:-1]):
            daily_meals = {}
            # * 각 행을 추출한다
            tr = item.find_all('tr')

            # * 제목을 찾는다
            title_td = tr[0].find('td', colspan=3)
            if title_td:
                # print(title_td)
                title = title_td.find_all(recursive=False)[-1].text.strip()

            # 연월일 날짜 파싱
            date_pattern = r'(\d+)년 *(\d+)월 *(\d+)일'
            date_match = re.search(date_pattern, normalize('NFD', title))
            if not date_match:
                raise ValueError(f"날짜 파싱에 실패하였습니다. `{date_pattern}` 을 기대했으나, `{normalize('', title)}`이 삽입되었습니다.")
            d = date_match.groups()
            meal_date = datetime.strptime(f"{d[0]}-{d[1]}-{d[2]}", '%Y-%m-%d').date() or None
            daily_meals['datestring'] = normalize('NFC', title)
            daily_meals['date'] = meal_date

            # * 조식
            breakfasts = []
            BREAKFAST_START_TR = 1
            # breakfast = tr[BREAKFAST_START_TR]  # 조식 첫 번째 행
            breakfast_td = tr[BREAKFAST_START_TR].find('td')  # 조식 첫 번째 행 첫 번째 열
            breakfast_count = int(breakfast_td.get('rowspan') or 1)

            for i in range(breakfast_count):
                menu_row = tr[BREAKFAST_START_TR+i]
                menu_td = menu_row.find_all('td')
                corner = menu_td[-2].find(recursive=True).text.strip()
                menu = menu_td[-1].find(recursive=True).text.strip()
                
                # print(f'(조식) {corner.text.strip() or "CORNER ?"} : {menu.text.strip() or "???"}')
                if normalize('NFC', menu) not in ['-' or '미운영']:
                    breakfasts.append({'menu': normalize('NFC', menu), 'corner': normalize('NFC', corner)})
            
            daily_meals['breakfast'] = breakfasts
            
            # * 중식/석식
            lunches = []
            LUNCH_START_TR = BREAKFAST_START_TR + breakfast_count
            lunch_td = tr[LUNCH_START_TR].find('td')  # 조식 첫 번째 행 첫 번째 열 (lunch_count 세는 데 필요)
            lunch_count = int(lunch_td.get('rowspan') or 1)

            for i in range(lunch_count):
                menu_row = tr[LUNCH_START_TR + i]
                menu_td = menu_row.find_all('td')

                if i == 0:
                    menu = menu_td[-1].find('p', recursive=True).text.strip()
                    corner = menu_td[-2].find(recursive=True).text.strip()
                else:
                    # menu_td는 최소 1개 이상이 존재하며, -1은 항상 메뉴명
                    menu = menu_td[-1].find('p', recursive=True).text.strip() 
                    
                    # menu_td가 2개일 경우, 첫 번째에는 코너가 오게 됨. 1개일 경우 메뉴명.
                    corner_candidates = menu_td[0].find_all(recursive=True)
                    corner_candidate = ''
                    for tmp_corner in corner_candidates:
                        # 'CORNER 3' 상하로 엔터를 넣으셔서 (모두 p 태그로 분리되는 바람에)
                        # 실제 내용이 들어있는 것을 추려내야 함
                        tmp_corner_name = tmp_corner.text.strip()
                        if len(tmp_corner_name) > len(corner_candidate):
                            corner_candidate = tmp_corner_name
                    
                    ignored_corner = (
                        '(면/밥) +탕수육'  # '짬뽕' + '(면/밥) +탕수육'
                    )

                    if corner_candidate and corner_candidate != menu and corner_candidate not in ignored_corner:
                        corner = corner_candidate

                # print(f'{corner or "CORNER ?"} : {menu or "???"}')
                if normalize('NFC', menu) not in ['미운영', '-']:
                    lunches.append({'corner': normalize('NFKC', corner), 'menu': normalize('NFC', menu)})
            
            daily_meals['lunch'] = lunches
            weekly_meals.append(daily_meals)
            
        # * 교직원식당  #########################
        employee = {}
        for row in tbls[-1].find_all('tr')[1:]:  # 첫 번째는 제목이다
            daily_employee = {}
            
            # 날짜
            date = row.find_all(recursive=False)[0].text.strip()
            # 연월일 날짜 파싱
            date_pattern = r'(\d+)/(\d+)'
            date_match = re.search(date_pattern, normalize('NFD', date))
            if not date_match:
                raise ValueError(f"날짜 파싱에 실패하였습니다. `{date_pattern}` 을 기대했으나, `{normalize('NFC', date)}`이 삽입되었습니다.")
            d = date_match.groups()
            meal_date = datetime.strptime(f"{d[0]}-{d[1]}", '%m-%d').date() or None
            meal_date = meal_date.replace(year=datetime.today().year)
            daily_employee['datestring'] = normalize('NFC', date)
            daily_employee['date'] = meal_date
            
            # 식단
            meal_menu = normalize('NFC', row.find_all(recursive=False)[2].text.strip())
            while(meal_menu[0] in '\ufeff\u200b '): meal_menu = meal_menu[1:]  # 불필요한 문자열 제거
            daily_employee['menu'] = meal_menu

            if meal_menu not in ['미운영', '-']:
                employee[meal_date] = daily_employee
        
        # 중식에서 찾아서 넣는다
        for daily_meals in weekly_meals:
            daily_employee = employee.pop(daily_meals['date'], None)
            if daily_employee is None: continue
            daily_meals['employee'] = daily_employee['menu']
            

        self.weekly_meals = weekly_meals
        self.last_updated = datetime.now()
