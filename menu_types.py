from typing import TypedDict, List, Union, Literal
from datetime import datetime

class Menu(TypedDict):
    corner: Union[
        Literal['CORNER 1', 'CORNER 2', 'CORNER 3', '공통찬', '분식'],
        str
    ]
    menu: str


class DailyMenu(TypedDict):
    datestring: str
    date: datetime
    breakfast: List[Menu]
    lunch: List[Menu]
