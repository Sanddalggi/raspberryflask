# Notice
자신의 작업 branch를 꼭 생성하고 작업하기 : git pull origin (브랜치 이름)
- git branch -> 현재 내가 다루는 branch 확인
- git branch (브랜치 이름) -> 내가 작업할 브랜치를 생성
- git checkout (브랜치 이름) -> 작업할 브랜치로 이동

* master 브랜치로 merge 하기 전까지 항상 자신의 작업 branch에서 코드를 작성
(예시) 범규 : git checkout bcrypt

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

34.64.187.181