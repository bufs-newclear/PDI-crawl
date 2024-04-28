# BUFS Shikdan parse
부산외국어대학교 식단 페이지를 분석하여 [PDI-Backend](https://github.com/bufs-newclear/PDI-backend)에 REST API을 이용하여 전송합니다.
https://github.com/ltlapy/bufs_shikdan_parse 을 기반으로 하고 있습니다.

## How to use
```sh
# 1회성 동작
#pip install beautifulsoup4 lxml
pip install -r requirements.txt
python3 main.py
```
실행 시 1회성으로 동기화를 실행하며, 주기적으로 동기화하려는 경우 운영체제의 cronjob 등을 통해 정기적으로 실행시킬 필요가 있습니다.

### TODO
- [x] REST API를 통한 데이터 인계
  - [x] 실행 로직 재설계
  - [x] 환경 변수 설정
- [ ] 마지막 갱신 시간의 대조