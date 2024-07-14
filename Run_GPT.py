import os
import sys
import json
import requests
import pytz
import pandas
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


# Offline method to get available models for each url
ModelDict = {
    "transsion.com": [
        'gpt-35-turbo',
        'gpt4-8k',
        'gpt-4o'
    ],
    "dashscope.aliyuncs.com": [
        'qwen-vl-chat-v1'
    ],
    "api.together.xyz": [
        'Qwen/Qwen1.5-110B-Chat'
    ]
}


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


def updateModels(NewURL): # Should add request method in the future (see ref in dashscope)
    assert ModelDict.__len__() > 0, "ModelDict should not be empty!"
    keywordURLs = list(ModelDict.keys())
    for keywordURL in keywordURLs:
        if keywordURL in NewURL:
            Models = ModelDict[keywordURL]
            return Models
        elif keywordURLs.index(keywordURL) == keywordURLs.__len__():
            raise Exception("URL not found, plz update ModelDict!")


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


class TestWindow(DialogBase):
    '''
    Dialog Window
    '''
    QuestionList = []

    def __init__(self, parent = None):
        super().__init__(parent)

        self.resize(360, 240)

    def initUI(self):
        self.Label = QLabel()
        self.Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.Input_FilePath = LineEditBase()

        self.Input_Column = LineEditBase()

        self.Input_Amount = LineEditBase()

        self.Button_Confirm = QPushButton('Confirm', self)

        self.Button_Cancel = QPushButton('Cancel', self)

        Layout = QGridLayout(self)
        Layout.addWidget(self.Label, 0, 0, 1, 2)
        Layout.addWidget(self.Input_FilePath, 1, 0, 1, 2)
        Layout.addWidget(self.Input_Column, 2, 0, 1, 2)
        Layout.addWidget(self.Input_Amount, 3, 0, 1, 2)
        Layout.addWidget(self.Button_Confirm, 4, 0, 1, 1)
        Layout.addWidget(self.Button_Cancel, 4, 1, 1, 1)
        Layout.setRowStretch(0, 1)

    def LoadQuestions(self):
        FilePath = self.Input_FilePath.text()
        if Path(FilePath).exists():
            excelDF = pandas.read_excel(FilePath, usecols = self.Input_Column.text().strip())
            self.QuestionList = excelDF.iloc[:, 0].to_list()
        MaximumAmount = self.Input_Amount.text().strip()
        if MaximumAmount.__len__() > 0 and self.QuestionList.__len__() > int(MaximumAmount) > 0 :
            self.QuestionList = self.QuestionList[:int(MaximumAmount)]

    def exec(self):
        self.initUI()

        self.Label.setText("Plz provide ur excel file path and its column letter:")

        self.Input_FilePath.SetFileDialog('SelectFile', '表格 (*.csv *.xlsx)')
        self.Input_FilePath.setAcceptDrops(True)
        self.Input_FilePath.setPlaceholderText("Please enter the excel file path to load")

        self.Input_Column.RemoveFileDialogButton()
        self.Input_Column.setAcceptDrops(False)
        self.Input_Column.setPlaceholderText("Please enter the column where questions are located")

        self.Input_Amount.RemoveFileDialogButton()
        self.Input_Amount.setAcceptDrops(False)
        self.Input_Amount.setPlaceholderText("Please enter the maximum amount of questions")

        self.Button_Confirm.clicked.connect(self.LoadQuestions, Qt.ConnectionType.QueuedConnection)
        self.Button_Confirm.clicked.connect(self.close, Qt.ConnectionType.QueuedConnection)

        self.Button_Cancel.clicked.connect(self.close)

        super().exec()


class MainWindow(QWidget):
    '''
    Main Window
    '''
    Models = []

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
        """
    }
    MessagesDict = {}

    ConversationDir = './Conversations'
    ConversationFilePath = ''
    QuestionDir = './Questions'
    QuestionFilePath = ''

    thread = None

    def __init__(self):
        super().__init__()

        self.resize(900, 600)

    def initUI(self):
        # Top area
        self.Input_URL = QLineEdit(self)

        self.Input_APIKey = QLineEdit(self)

        self.Input_APPID = QLineEdit(self)

        self.ModelSelector = QComboBox(self)

        self.RoleSelector = QComboBox(self)

        Layout_Top = QGridLayout()
        Layout_Top.addWidget(self.Input_URL, 0, 1, 1, 2)
        Layout_Top.addWidget(self.Input_APIKey, 0, 3, 1, 2)
        Layout_Top.addWidget(self.Input_APPID, 0, 5, 1, 2)
        Layout_Top.addWidget(self.ModelSelector, 1, 1, 1, 3)
        Layout_Top.addWidget(self.RoleSelector, 1, 4, 1, 3)

        # Right area
        self.Browser = QTextBrowser(self)

        self.InputArea = TextEditBase(self)

        self.Button_Load = QPushButton('Load Questions from File', self)

        self.Button_Send = QPushButton('Send', self)
    
        self.Button_Test = QPushButton('Test', self)

        Layout_Right = QGridLayout()
        Layout_Right.addWidget(self.Browser, 0, 0, 5, 2)
        Layout_Right.addWidget(self.InputArea, 5, 0, 2, 2)
        Layout_Right.addWidget(self.Button_Load, 7, 0, 1, 2)
        Layout_Right.addWidget(self.Button_Send, 8, 0, 1, 1)
        Layout_Right.addWidget(self.Button_Test, 8, 1, 1, 1)

        # Left area
        self.ConversationList = QListWidget(self)

        self.Button_CreateConversation = QPushButton('New Conversation', self)

        Layout_Left = QVBoxLayout()
        Layout_Left.addWidget(self.ConversationList)
        Layout_Left.addWidget(self.Button_CreateConversation)

        # Combine layouts
        Layout = QGridLayout(self)
        Layout.addLayout(Layout_Top, 0, 0, 1, 4)
        Layout.addLayout(Layout_Left, 1, 0, 4, 1)
        Layout.addLayout(Layout_Right, 1, 1, 4, 3)
        Layout.setColumnStretch(1, 1)

    def UpdateModels(self):
        self.Models = updateModels(self.Input_URL.text())
        self.ModelSelector.clear()
        self.ModelSelector.addItems(self.Models)

    def renameConversation(self):
        currentItem = self.ConversationList.currentItem()
        if currentItem:
            old_name = currentItem.text()
            new_name, ok = QInputDialog.getText(self,
                'Rename Conversation',
                'Enter new conversation name:'
            )
            if ok and new_name:
                self.ConversationFilePath = Path(self.ConversationDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(self.ConversationDir).joinpath(f"{old_name}.txt"), self.ConversationFilePath)
                currentItem.setText(new_name)
                self.QuestionFilePath = Path(self.QuestionDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(self.QuestionDir).joinpath(f"{old_name}.txt"), self.QuestionFilePath)

    def deleteConversation(self):
        currentItem = self.ConversationList.currentItem()
        if currentItem:
            confirm = QMessageBox.question(self,
                'Delete Conversation',
                'Are you sure you want to delete this conversation?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                row = self.ConversationList.row(currentItem)
                self.ConversationList.takeItem(row)
                self.Browser.clear()
                os.remove(Path(self.ConversationDir).joinpath(currentItem.text() + '.txt').as_posix())
                os.remove(Path(self.QuestionDir).joinpath(currentItem.text() + '.txt').as_posix())

    def ShowContextMenu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Conversation", self)
        delete_action.triggered.connect(self.deleteConversation)
        rename_action = QAction("Rename Conversation", self)
        rename_action.triggered.connect(self.renameConversation)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.ConversationList.mapToGlobal(position))

    def LoadConversationList(self):
        # Check if the conversations directory exists
        if not os.path.exists(self.ConversationDir):
            os.makedirs(self.ConversationDir)
        # Check if the questions directory exists
        if not os.path.exists(self.QuestionDir):
            os.makedirs(self.QuestionDir)
        # Remove empty conversations(&questions) and add the rest to history list
        self.ConversationList.clear()
        for HistoryFileName in os.listdir(self.ConversationDir):
            if HistoryFileName.endswith('.txt'):
                HistoryFilePath = Path(self.ConversationDir).joinpath(HistoryFileName).as_posix()
                QuestionFilePath = Path(self.QuestionDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(HistoryFilePath) == 0:
                    os.remove(HistoryFilePath)
                    os.remove(QuestionFilePath) if Path(QuestionFilePath).exists() else None
                    continue
                self.ConversationList.addItem(HistoryFileName[:-4]) # Remove the .txt extension

    def LoadCurrentHistory(self, item: QListWidgetItem):
        # Load a conversation from a txt file and display it in the browser
        self.ConversationFilePath = Path(self.ConversationDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.ConversationFilePath, 'r', encoding = 'utf-8') as f:
            Messages = [json.loads(line) for line in f]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.Browser.setText(markdown) #self.Browser.setMarkdown(markdown)
        # Load a question from the txt file and display it in the input area
        self.QuestionFilePath = Path(self.QuestionDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.QuestionFilePath, 'r', encoding = 'utf-8') as f:
            Question = f.read()
        # Set qustion
        self.InputArea.setText(Question)

    def ApplyRole(self):
        ConversationName = Path(self.ConversationFilePath).stem# if self.ConversationList.currentItem() is None else self.ConversationList.currentItem().text()
        Messages = [
            {
                'role': 'assistant',
                'content': self.roles[self.RoleSelector.currentText()]
            }
        ]
        self.MessagesDict[ConversationName] = Messages
        return Messages

    def CreateConversation(self):
        # Get the current time as the name of conversation
        beijing_timezone = pytz.timezone('Asia/Shanghai')
        formatted_time = datetime.now(beijing_timezone).strftime("%Y_%m_%d_%H_%M_%S")
        # Check if the path would be overwritten
        FilePath = Path(self.ConversationDir).joinpath(f"{formatted_time}.txt")
        Directory, FileName = os.path.split(FilePath)
        while Path(FilePath).exists():
            pattern = r'(\d+)\)\.'
            if re.search(pattern, FileName) is None:
                FileName = FileName.replace('.', '(0).')
            else:
                CurrentNumber = int(re.findall(pattern, FileName)[-1])
                FileName = FileName.replace(f'({CurrentNumber}).', f'({CurrentNumber + 1}).')
            FilePath = Path(Directory).joinpath(FileName).as_posix()
        FileName = Path(FilePath).name
        ConversationName = Path(FilePath).stem
        # Update the history file path and the question file path
        self.ConversationFilePath = FilePath
        self.QuestionFilePath = Path(self.QuestionDir).joinpath(FileName).as_posix()
        # Set the files & browser
        with open(self.ConversationFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        self.Browser.clear()
        with open(self.QuestionFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        self.InputArea.clear()
        # Add the given name to the history list and select it
        NewConversation = QListWidgetItem(ConversationName)
        self.ConversationList.addItem(NewConversation)
        self.ConversationList.setCurrentItem(NewConversation)
        # Init role
        self.ApplyRole()

    def saveConversation(self, Messages: list):
        with open(self.ConversationFilePath, 'w', encoding = 'utf-8') as f:
            ConversationStr = '\n'.join(json.dumps(message) for message in Messages)
            f.write(ConversationStr)

    def saveQuestion(self, Question: str):
        with open(self.QuestionFilePath, 'w', encoding = 'utf-8') as f:
            QuestionStr = Question.strip()
            f.write(QuestionStr)

    def LoadQuestions(self):
        ChildWindow_Test = TestWindow(self)
        ChildWindow_Test.exec()
        Questions =  ChildWindow_Test.QuestionList
        for Question in Questions:
            self.CreateConversation()
            self.InputArea.setText(Question)
            #self.Query()

    def updateRecord(self, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.Browser.setText(markdown) if self.ConversationList.currentItem().text() == ConversationName else None #self.Browser.setMarkdown(markdown)
        # Move the scrollbar to the bottom
        cursor = self.Browser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.Browser.setTextCursor(cursor)
        # Save the current conversation to a txt file with the given name
        self.saveConversation(Messages)

    def recieveAnswer(self, recievedText, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        if Messages[-1]['role'] == 'user':
            Messages.append({'role': 'assistant', 'content': recievedText})
        '''
        else:
            Messages[-1]['content'] += recievedText
        '''
        self.MessagesDict[ConversationName] = Messages
        self.updateRecord(ConversationName)

    def startThread(self, InputContent, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        if InputContent.strip().__len__() > 0:
            if self.thread is not None and self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
            Messages.append({'role': 'user', 'content': InputContent})
            self.MessagesDict[ConversationName] = Messages
            self.updateRecord(ConversationName)
            self.thread = RequestThread(
                URL = self.Input_URL.text(),
                APP_ID = self.Input_APPID.text(),
                API_key = self.Input_APIKey.text(),
                Model = self.ModelSelector.currentText(),
                Messages = Messages
            )
            self.thread.textReceived.connect(lambda text: self.recieveAnswer(text, ConversationName))
            self.thread.start()

    def Query(self):
        InputContent = self.InputArea.toPlainText()
        ConversationName = self.ConversationList.currentItem().text()
        self.startThread(InputContent, ConversationName)
        self.InputArea.clear()

    def QueryTest(self):
        InputContent = self.InputArea.toPlainText()
        ConversationName = self.ConversationList.currentItem().text()
        TotalTestTimes, ok = QInputDialog.getText(self,
            'Set Testing Times',
            'Enter testing times:'
        )
        if ok and TotalTestTimes:
            self.TotalTestTimes = int(TotalTestTimes)
        else:
            return
        self.CurrentTestTime = 1
        print('Current test time:', self.CurrentTestTime)
        Input = self.InputArea.toPlainText()
        Answers = []
        def collectAnswers(recievedText):
            self.CurrentTestTime += 1
            if self.CurrentTestTime <= self.TotalTestTimes:
                print('Current test time:', self.CurrentTestTime)
                Answers.append(recievedText)
                self.startThread(InputContent, ConversationName)
                self.thread.textReceived.connect(collectAnswers)
            else: #if self.CurrentTestTime > self.TotalTestTimes:
                tfidf_vectorizer = TfidfVectorizer()
                tfidf_matrix = tfidf_vectorizer.fit_transform(Answers) # Transfer data into TF-IDF vector
                similarity_matrix = cosine_similarity(tfidf_matrix) # Compute cosine similarity of the matrix
                MsgBox = QMessageBox()
                MsgBox.setWindowTitle('Test Result')
                MsgBox.setText(f'The similarity matrix is:\n{similarity_matrix}')
                MsgBox.exec()
                # Save the test result
                csvPath = './TestResult.csv'
                TestResults = {
                    'CodeInput': [Input],
                    'Answer': [Answers[0]],
                    'SimilarityMatrix': [similarity_matrix]
                }
                TestResultsDF = pandas.DataFrame(TestResults)
                if Path(csvPath).exists():
                    TestResultsDF = pandas.concat([pandas.read_csv(csvPath), TestResultsDF], ignore_index = True)
                    TestResultsDF.reset_index()
                TestResultsDF.to_csv(csvPath, index = False)
        self.startThread(InputContent, ConversationName)
        self.thread.textReceived.connect(collectAnswers)
        self.InputArea.clear()

    def Main(self):
        self.initUI()

        # Top area
        self.Input_URL.textChanged.connect(self.UpdateModels)
        self.Input_URL.setPlaceholderText("Please enter the URL")
        self.Input_URL.setText("https://gptgateway-uat.transsion.com")

        self.Input_APIKey.setPlaceholderText("Please enter your API key")
        self.Input_APIKey.setText("tITFPtSs9lLXD4a0xuLlGPTrwPNftZ0g")

        self.Input_APPID.setPlaceholderText("Please enter your APP ID (Leave this empty if u don't have any)")
        self.Input_APPID.setText("c_MjIxMTI1MDAxbQ")

        self.ModelSelector.setCurrentIndex(self.ModelSelector.count() - 1) # Select the last index as default

        self.RoleSelector.addItems(self.roles.keys())
        self.RoleSelector.currentIndexChanged.connect(self.ApplyRole)

        # Right area
        self.InputArea.textChanged.connect(self.saveQuestion)
        self.InputArea.keyEnterPressed.connect(self.Query)
        self.InputArea.setPlaceholderText(
            """
            请在此区域输入您的问题，点击 Send 或按下 Ctrl+Enter 发送提问
            如果只返回了问题而没有答案，请等待几秒或者换一个模型试试
            """
        )

        self.Button_Load.clicked.connect(self.LoadQuestions)

        self.Button_Send.clicked.connect(self.Query)

        self.Button_Test.clicked.connect(self.QueryTest)

        # Left area
        self.ConversationList.itemClicked.connect(self.LoadCurrentHistory)
        self.ConversationList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ConversationList.customContextMenuRequested.connect(self.ShowContextMenu)

        self.Button_CreateConversation.clicked.connect(self.CreateConversation)

        # Load histories
        self.LoadConversationList()

        # Create a new conversation
        self.CreateConversation()

        # Show window
        self.show()


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = MainWindow()
    window.Main()
    sys.exit(App.exec())