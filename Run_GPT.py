import os
import sys
import json
import requests
import pytz
from typing import Optional
from datetime import date, datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import QTextCursor, QAction
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtWidgets import *

from QEasyWidgets.Utils import *
from QEasyWidgets.QTasks import *
from QEasyWidgets.WindowCustomizer import *


def GPTRequest(
    URL: str,
    APP_ID: Optional[str] = None,
    API_key: str = ...,
    model: str = ...,
    messages: list = [{}],
    top_p: float = 0.8,
    top_k: int = 100,
    stream: bool = True
):
    if "transsion.com" in URL:
        Gateway = "https://pfgatewayuat.transsion.com:9199"
        # 获取令牌
        response = requests.request("get", f"{Gateway}/service-pf-open-gateway/oauth/token?grant_type=client_credentials&client_id={APP_ID}&client_secret={API_key}")
        res_token = response.json()
        #print(f"Token response:\n{res_token}")
        accessToken = res_token.get("data", {}).get("access_token", "")
        oauth_token = f"Bearer {accessToken}"
        # 请求GPT接口
        url = f"{Gateway}/gpt-proxy-service/api/azure/openai/chatCompletion?deploymentId={model}"
        Headers = {
            "Content-Type": "application/json",
            "Authorization": oauth_token
        }
        Payload = {
            "messages": messages,
            "temperature": 0,
            "topP": top_p,
        }
        response = requests.post(
            url = url,
            headers = Headers,
            data = json.dumps(Payload),
            stream = stream
        )
        if response.status_code == 200:
            content = ""
            for chunk in response.iter_content(chunk_size = 1024, decode_unicode = True):
                #chunk = ast.literal_eval(chunk)
                if chunk:
                    content += chunk#.decode('utf-8')
                    try:
                        parsed_content = json.loads(content)
                        return parsed_content['data']['choices'][0]['message']['content']
                    except json.JSONDecodeError:
                        continue
        else:
            print("Request failed with status code", response.status_code)

    if "dashscope.aliyuncs.com" in URL:
        Headers = {
            "Content-Type": "application/json" if stream else "text/event-stream",
            "Authorization": API_key
        }
        Payload = {
            "model": model,
            "messages": messages,
            "top_p": top_p,
            "top_k": top_k
        }
        response = requests.post(
            url = URL,
            headers = Headers,
            data = json.dumps(Payload),
            stream = stream
        )
        if response.status_code == 200:
            content = ""
            for chunk in response.iter_content(chunk_size = 1024, decode_unicode = True):
                if chunk:
                    content += chunk#.decode('utf-8')
                    try:
                        parsed_content = json.loads(content)
                        return parsed_content['output']['choices'][0]['message']['content']
                    except json.JSONDecodeError:
                        continue
        else:
            print("Request failed with status code", response.status_code)

    if "api.together.xyz" in URL:
        Headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": API_key
        }
        Payload = {
            "model": model,
            "messages": messages,
            "top_p": top_p,
            "top_k": top_k,
            "stream": stream
        }
        response = requests.post(
            url = URL,
            json = Payload,
            headers = Headers,
            stream = stream
        )
        if response.status_code == 200:
            content = ""
            for chunk in response.iter_content(chunk_size = 1024, decode_unicode = True):
                if chunk:
                    content += chunk#.decode('utf-8')
                    try:
                        parsed_content = json.loads(content)
                        return parsed_content['choices'][0]['message']['content']
                    except json.JSONDecodeError:
                        continue
        else:
            print("Request failed with status code", response.status_code)


def BuildMessageMarkdown(messages: list[dict]):
    markdown = ""
    for message in messages:
        role = str(message['role']).strip()
        content = str(message['content']).strip()
        if len(content) == 0:
            continue
        if role == 'user':
            markdown += f"**Q**: {content}\n\n\n"
        if role == 'assistant':
            markdown += f"**A**: {content}\n\n"
            markdown += "---------------------------------------\n\n"
    return markdown


class RequestThread(QThread):
    textReceived = Signal(str)

    def __init__(self,
        URL: str = ...,
        APP_ID: Optional[str] = None,
        API_key: str = ...,
        Model: str = ...,
        Messages: list[dict] = [{}],
        Top_P: float = 0.8,
        Top_K: int = 100,
    ):
        super().__init__()

        self.URL = URL
        self.APP_ID = APP_ID
        self.API_key = API_key
        self.Model = Model
        self.Messages = Messages
        self.Top_P = Top_P
        self.Top_K = Top_K

    def run(self):
        text = GPTRequest(
            URL = self.URL,
            APP_ID = self.APP_ID,
            API_key = self.API_key,
            model = self.Model,
            messages = self.Messages,
            top_p = self.Top_P,
            top_k = self.Top_K
        )
        self.textReceived.emit(text)


class Window(QWidget):
    '''
    '''
    roles = {
        "无": """
        """,
        "航班信息翻译员": """
            ## Role:
            航班信息翻译员
            ## Profile:
            - language: 中文
            - description: 你是一个专门处理航班信息的翻译员，你的主要职责是将原始的航班信息翻译并整理为用户易读的格式。原始的机票信息结构是：多个航段组成的一张票据信息，票据会有一个总价格
            ## Goals:
            - 理解和翻译航班信息
            - 按照规定的格式整理翻译后的航班信息
            ## Constrains:
            - 输出的航班信息只包含航班号（英文+需要翻译为中文名称）、航空公司（仅翻译为中文名称）、出发地、目的地、起飞机场（英文+需要翻译为中文名称）、落地机场（英文+需要翻译为中文名称）、起飞时间（格式为yyyy-MM-dd HH:mm:ss）、到达时间（格式为yyyy-MM-dd HH:mm:ss）、行李限额（需要翻译为中文解释）、改签费（即：更改航班费用）、退票费（即：取消退款费用）、误机费（即：未办理登记手续费用）、机票总价格（仅返回数字）、预订编码、机票号、出发城市代码、目的城市代码
            - 所有的时间和日期信息需要按照用户指定的格式处理
            - 所有的信息需要按照有序列表输出
            - 机票总价格的格式如下：TOTAL代表机票总金额 CNY代表国际币种简称，后面的数字代表金额，最终期望显示为：机票总金额：金额，如果币种简称不符合币种要求，显示为：暂无
            - 将机票信息转换成JSON数组格式。缺失的信息请在JSON中以null表示。JSON模板：{
                "fightNumber": "航班号（英文+需要翻译为中文名称）",
                "airway": "航空公司（仅翻译为中文名称）",
                "fightDepartureCity": "出发地",
                "fightFallCity": "目的地",
                "fightDepartureAirport": "起飞机场（英文+需要翻译为中文名称）",
                "fightFallAirport": "落地机场（英文+需要翻译为中文名称）",
                "fightStatus": "航班状态",
                "fightDepartureTime": "起飞时间（格式为yyyy-MM-dd HH:mm:ss）",
                "fightFallTime": "到达时间（格式为yyyy-MM-dd HH:mm:ss）",
                "baggageAllowance": "行李限额（需要翻译为中文解释）",
                "rebookFee": "改签费（即：更改航班费用）",
                "refundFee": "退票费（即：取消退款费用）",
                "delayFee": "误机费（即：未办理登记手续费用）",
                "flightPrice": "机票总价格（仅返回数字）",
                "bookingCode": "预订编码",
                "ticketNo": "机票号",
                "fightDepartureCityCode": "出发城市代码",
                "fightFallCityCode": "目的城市代码"
            }
            - 结果中仅包含JSON数组
        """,
        "写作助理": """
            As a writing improvement assistant, your task is to improve the spelling, grammar, clarity, concision, and overall readability of the text provided.
            While breaking down long sentences, reducing repetition, and providing suggestions for improvement.
            Please provide only the corrected Chinese version of the text and avoid including explanations. Please begin by editing the following text: [文章内容]
        """
    }
    Messages = []

    HistoryDir = './Conversations'
    currentFileName = ''

    thread = None

    def __init__(self):
        super().__init__()

        self.initUI()

        self.LoadHistoryList()

        self.CreateConversation()

    def initUI(self):
        # Top area
        self.Input_URL = QLineEdit(self)
        self.Input_URL.setPlaceholderText("Please enter the URL")
        self.Input_URL.setText("https://gptgateway-uat.transsion.com")

        self.Input_APIKey = QLineEdit(self)
        self.Input_APIKey.setPlaceholderText("Please enter your API key")
        self.Input_APIKey.setText("tITFPtSs9lLXD4a0xuLlGPTrwPNftZ0g")

        self.Input_APPID = QLineEdit(self)
        self.Input_APPID.setPlaceholderText("Please enter your APP ID (Leave this empty if u don't have any)")
        self.Input_APPID.setText("c_MjIxMTI1MDAxbQ")

        self.ModelSelector = QComboBox(self)
        self.ModelSelector.addItems(['gpt-4o', '...']) # Should sync it with URL in the future

        self.RoleSelector = QComboBox(self)
        self.RoleSelector.addItems(self.roles.keys())
        self.RoleSelector.currentIndexChanged.connect(self.ApplyRole)

        Layout_Top = QGridLayout()
        Layout_Top.addWidget(self.Input_URL, 0, 1, 1, 2)
        Layout_Top.addWidget(self.Input_APIKey, 0, 3, 1, 2)
        Layout_Top.addWidget(self.Input_APPID, 0, 5, 1, 2)
        Layout_Top.addWidget(self.ModelSelector, 1, 1, 1, 3)
        Layout_Top.addWidget(self.RoleSelector, 1, 4, 1, 3)

        # Right area
        self.Browser = QTextBrowser(self)

        self.InputArea = TextEditBase(self)
        self.InputArea.keyEnterPressed.connect(self.Query)
        self.InputArea.setPlaceholderText(
            """
            请在此区域输入您的问题，点击 Send 或按下 Ctrl+Enter 发送提问
            当答案开始输出的时候，问题才会显示，请不要着急
            如果只返回了问题，而没有答案，请等待几秒或者换一个模型试试
            """
        )
        self.InputArea.setText(
            """
            1.  TG340  V1  TH01AUG  DACBKK DK1   0245 0615       达卡-曼谷
                2.  TG664  V1  TH01AUG  BKKPVG DK1   1045 1600      曼谷-上海浦东
                3930+35=3965CNY        25KG    改期USD50,退票USD100,误机USD150,部分税费不退
            """
        )

        self.Button_Send = QPushButton('Send', self)
        self.Button_Send.clicked.connect(self.Query)
    
        self.Button_Test = QPushButton('Test', self)
        self.Button_Test.clicked.connect(self.QueryTest)

        Layout_Right = QGridLayout()
        Layout_Right.addWidget(self.Browser, 0, 0, 5, 2)
        Layout_Right.addWidget(self.InputArea, 5, 0, 2, 2)
        Layout_Right.addWidget(self.Button_Send, 7, 0, 1, 1)
        Layout_Right.addWidget(self.Button_Test, 7, 1, 1, 1)

        # Left area
        self.HistoryList = QListWidget(self)
        self.HistoryList.itemClicked.connect(self.LoadHistory)
        self.HistoryList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.HistoryList.customContextMenuRequested.connect(self.ShowContextMenu)

        self.Button_CreateConversation = QPushButton('New Conversation', self)
        self.Button_CreateConversation.clicked.connect(self.CreateConversation)

        Layout_Left = QVBoxLayout()
        Layout_Left.addWidget(self.HistoryList)
        Layout_Left.addWidget(self.Button_CreateConversation)

        # Combine layouts
        Layout = QGridLayout(self)
        Layout.addLayout(Layout_Top, 0, 0, 1, 4)
        Layout.addLayout(Layout_Left, 1, 0, 4, 1)
        Layout.addLayout(Layout_Right, 1, 1, 4, 3)
        Layout.setColumnStretch(1, 1)

    def ApplyRole(self):
        self.Messages.clear(),
        self.Messages.append(
            {
                'role': 'assistant',
                'content': self.roles[self.RoleSelector.currentText()]
            }
        )

    def renameConversation(self):
        current_item = self.HistoryList.currentItem()
        if current_item:
            old_name = current_item.text()
            new_name, ok = QInputDialog.getText(self,
                'Rename Conversation',
                'Enter new conversation name:'
            )
            if ok and new_name:
                self.currentFilePath = Path(self.HistoryDir).joinpath(new_name + '.txt').as_posix()
                os.rename(self.HistoryDir + old_name + '.txt', self.currentFilePath)
                current_item.setText(new_name)

    def deleteConversation(self):
        current_item = self.HistoryList.currentItem()
        if current_item:
            confirm = QMessageBox.question(self,
                'Delete Conversation',
                'Are you sure you want to delete this conversation?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                row = self.HistoryList.row(current_item)
                self.HistoryList.takeItem(row)
                self.Browser.clear()
                os.remove(Path(self.HistoryDir).joinpath(current_item.text() + '.txt').as_posix())

    def ShowContextMenu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Conversation", self)
        delete_action.triggered.connect(self.deleteConversation)
        rename_action = QAction("Rename Conversation", self)
        rename_action.triggered.connect(self.renameConversation)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.HistoryList.mapToGlobal(position))

    def LoadHistoryList(self):
        self.HistoryList.clear()
        # Check if the conversations directory exists
        if not os.path.exists(self.HistoryDir):
            os.makedirs(self.HistoryDir)
        for file in os.listdir(self.HistoryDir):
            if file.endswith('.txt'):
                self.HistoryList.addItem(file[:-4]) # Remove the .txt extension

    def LoadHistory(self, item: QListWidgetItem):
        self.Browser.clear()
        # Load a conversation from a txt file and display it in the conversation window
        self.currentFilePath = Path(self.HistoryDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.currentFilePath, 'r', encoding = 'utf-8') as f:
            self.Messages = [json.loads(line) for line in f]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(self.Messages)
        self.Browser.setText(markdown) #self.Browser.setMarkdown(markdown)

    def CreateConversation(self):
        self.ApplyRole()
        # Get the current time as the name of conversation
        beijing_timezone = pytz.timezone('Asia/Shanghai')
        formatted_time = datetime.now(beijing_timezone).strftime("%Y_%m_%d_%H_%M_%S")
        # Add the given name to the history list
        self.HistoryList.addItem(formatted_time)
        # Save the current conversation to a txt file with the given name
        self.currentFilePath = Path(self.HistoryDir).joinpath(formatted_time + '.txt').as_posix()
        with open(self.currentFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        # Clear the conversation window
        self.Browser.clear()

    def updateText(self):
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(self.Messages)
        self.Browser.setText(markdown) #self.Browser.setMarkdown(markdown)
        # Move the scrollbar to the bottom
        cursor = self.Browser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.Browser.setTextCursor(cursor)
        # Save the current conversation to a txt file with the given name
        with open(self.currentFilePath, 'w', encoding = 'utf-8') as f:
            conversation_str = '\n'.join(json.dumps(message) for message in self.Messages)
            f.write(conversation_str)

    def recieveAnswer(self, recievedText):
        if self.Messages[-1]['role'] == 'user':
            self.Messages.append({'role': 'assistant', 'content': recievedText})
        '''
        else:
            self.Messages[-1]['content'] += recievedText
        '''
        self.updateText()

    def startThread(self):
        InputContent = self.InputArea.toPlainText()
        if InputContent.strip() != "":
            if self.thread is not None and self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
            self.Messages.append({'role': 'user', 'content': InputContent})
            self.updateText()
            self.thread = RequestThread(
                URL = self.Input_URL.text(),
                APP_ID = self.Input_APPID.text(),
                API_key = self.Input_APIKey.text(),
                Model = self.ModelSelector.currentText(),
                Messages = self.Messages
            )
            self.thread.textReceived.connect(self.recieveAnswer)
            self.thread.start()

    def Query(self):
        self.startThread()
        self.InputArea.clear()

    def QueryTest(self):
        Answers = []
        self.CurrentTestTime = 1
        print('Current test time:', self.CurrentTestTime)
        self.TotalTestTimes = int(
            QInputDialog.getText(self,
                'Set Testing Times',
                'Enter testing times:'
            )[0]
        )
        Input = self.InputArea.toPlainText()
        def collectAnswers(recievedText):
            self.CurrentTestTime += 1
            if self.CurrentTestTime <= self.TotalTestTimes:
                print('Current test time:', self.CurrentTestTime)
                Answers.append(recievedText)
                self.InputArea.setText(Input)
                self.startThread()
                self.thread.textReceived.connect(collectAnswers)
                self.InputArea.clear()
            else: #if self.CurrentTestTime > self.TotalTestTimes:
                tfidf_vectorizer = TfidfVectorizer()
                tfidf_matrix = tfidf_vectorizer.fit_transform(Answers) # Transfer data into TF-IDF vector
                similarity_matrix = cosine_similarity(tfidf_matrix) # Compute cosine similarity of the matrix
                MsgBox = QMessageBox()
                MsgBox.setWindowTitle('Test Result')
                MsgBox.setText(f'The similarity matrix is:\n{similarity_matrix}')
                MsgBox.exec()
                print(f'The similarity matrix is:\n{similarity_matrix}') # In case the result is too large to display
        self.startThread()
        self.thread.textReceived.connect(collectAnswers)


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    window.resize(900, 600)
    window.show()
    sys.exit(App.exec())