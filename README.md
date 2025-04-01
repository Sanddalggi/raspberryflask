# Notice
자신의 작업 branch를 꼭 생성하고 작업하기 : git pull origin (브랜치 이름)
- git branch -> 현재 내가 다루는 branch 확인
- git branch (브랜치 이름) -> 내가 작업할 브랜치를 생성
- git checkout (브랜치 이름) -> 작업할 브랜치로 이동
master 브랜치로 merge 하기 전까지 항상 자신의 작업 branch에서 코드를 작성
(예시) 범규 : git checkout bcrypt
    1. bcrypt 비밀번호 코드를 작성하기 위해 bcrypt라는 이름의 branch를 나누어서 작업
    2. 이후 코드 수정이 끝나고 기능을 넣을때 master branch로 merge(팀원들의 동의 필요)
    + branch를 나누는 이유? master 브랜치를 동시에 다룰 경우 commit push 과정에서 충돌 발생
    + 이렇게 번거로운데도 git 버전관리를 하는 이유?
        (1) **같은 패키지에 동시 작업 불가, 5명이 한번에 개발할 수 없어서 시간 소모 매우 큼**
        (2) 코드가 크게 날아갔을 때 버전 히스토리 이용해서 특정 시점으로 복구 가능
        (3) 찐최종리얼최종본이이상수정하지않음백퍼센트_final_realend.py -> 이런거 안해도 됨
        (4) 멋있음


### Repository를 로컬 PC에서 관리하기
0. 터미널 실행, 프로젝트를 관리할 디렉토리로 이동
1. git clone https://github.com/Sanddalggi/raspberryflask.git
2. git init
3. git remote add origin https://github.com/Sanddalggi/raspberryflask.git
4. git add .
5. git commit -m "커밋 내용"
6. git push origin (브랜치 이름)
-> 변경사항이 필요할 때는 README.md 고치고 커밋
-> 중간에 막히면 구글링, ChatGPT


### 로컬에서 flask run
venv 가상환경을 같이 올려두었으니 해당 디렉토리의 터미널에 들어간다.
source bin/activate(윈도우는 명령어 다름) 입력하면 가상환경 실행 가능.
python 인터프리터가 반드시 venv로 설정이 되어있어야 라이브러리가 정상적으로 import 가능.
Good luck.
