# Notice
Before you edit the code, "pull request" is always first.

### Repository를 로컬 PC에서 관리하기
0. 터미널 실행, 프로젝트를 관리할 디렉토리로 이동
1. git clone https://github.com/Sanddalggi/raspberryflask.git
2. git init
3. git remote add origin https://github.com/Sanddalggi/raspberryflask.git
4. git add .
5. git commit -m "커밋 내용"
6. git push origin master
-> 변경사항이 필요할 때는 README.md 고치고 커밋
-> 중간에 막히면 구글링, ChatGPT

### 로컬에서 flask run
venv 가상환경을 같이 올려두었으니 해당 디렉토리의 터미널에 들어간다.
source bin/activate(윈도우는 명령어 다름) 입력하면 가상환경 실행 가능.
python 인터프리터가 반드시 venv로 설정이 되어있어야 라이브러리가 정상적으로 import 가능.
Good luck.
