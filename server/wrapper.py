import os
import json
import PyEasyUtils as EasyUtils
from pathlib import Path

##############################################################################################################################

class ChatManager:
    """
    """
    def __init__(self,
        promptDir: str,
        conversationDir: str,
        questionDir: str,
    ):
        self.promptDir = promptDir
        self.conversationDir = conversationDir
        self.questionDir = questionDir

        self.promptDict = {}
        self.messagesDict = {}

    def _setFilePath(self, dir, id, name):
        return Path(dir).joinpath(f"{id}_{name}.txt").as_posix()

    def _updatePromptDict(self, promptID, promptName):
        self.promptDict[promptID] = promptName

    def _getPromptName(self, promptID):
        return self.promptDict[promptID]

    def _getPromptFilePath(self, promptID, promptName):
        return self._setFilePath(self.promptDir, promptID, promptName)

    def _getPromptIDAndPromptName(self, promptFilePath):
        return Path(promptFilePath).stem.split('_')

    def loadPrompts(self):
        # Check if the prompt directory exists
        if not os.path.exists(self.promptDir):
            os.makedirs(self.promptDir)
        # Initialize roles and add prompt to combobox
        for fileName in os.listdir(self.promptDir):
            if fileName.endswith('.txt'):
                promptFilePath = Path(self.promptDir).joinpath(fileName).as_posix()
                # if os.path.getsize(promptFilePath) == 0: # Remove empty files
                #     os.remove(promptFilePath)
                #     continue
                promptID, promptName = self._getPromptIDAndPromptName(promptFilePath)
                self._updatePromptDict(promptID, promptName)
        return self.promptDict

    def getPrompt(self, promptID):
        promptName = self._getPromptName(promptID)
        # Load from file
        promptFilePath = self._getPromptFilePath(promptID, promptName)
        with open(promptFilePath, 'r', encoding = 'utf-8') as f:
            prompt = f.read().strip()
        return prompt

    def createPrompt(self, name):
        promptID = EasyUtils.generateRandomString() # Generate a random string
        promptFilePath = self._getPromptFilePath(promptID, name)
        # Setup file
        with open(promptFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        # Init prompt
        promptID, promptName = self._getPromptIDAndPromptName(promptFilePath)
        self._updatePromptDict(promptID, promptName)
        return promptID, promptName

    def renamePrompt(self, promptID, newName):
        oldName = self._getPromptName(promptID)
        oldPromptFilePath = self._getPromptFilePath(promptID, oldName)
        newPromptFilePath = self._getPromptFilePath(promptID, newName)
        # Rename file
        os.rename(oldPromptFilePath, newPromptFilePath)
        # Update prompt
        self._updatePromptDict(promptID, newName)

    def deletePrompt(self, promptID):
        promptName = self._getPromptName(promptID)
        # Remove file
        os.remove(self._setFilePath(self.promptDir, promptID, promptName))
        # Remove prompt
        self.promptDict.pop(promptID)

    def savePrompt(self, promptID, prompt: str):
        promptName = self._getPromptName(promptID)
        promptFilePath = self._getPromptFilePath(promptID, promptName)
        # Save to file
        with open(promptFilePath, 'w', encoding = 'utf-8') as f:
            promptStr = prompt.strip()
            f.write(promptStr)

    def _updateMessageDict(self, historyID, conversationName):
        self.messagesDict[historyID] = conversationName

    def _getConversationName(self, historyID):
        return self.messagesDict[historyID]

    def _getHistoryFilePath(self, historyID, conversationName):
        return self._setFilePath(self.conversationDir, historyID, conversationName), self._setFilePath(self.questionDir, historyID, conversationName)

    def _getHistoryIDAndConversationName(self, conversationFilePath):
        return Path(conversationFilePath).stem.split('_')

    def loadHistories(self):
        # Check if the conversations directory exists
        if not os.path.exists(self.conversationDir):
            os.makedirs(self.conversationDir)
        # Check if the questions directory exists
        if not os.path.exists(self.questionDir):
            os.makedirs(self.questionDir)
        # Initialize messagesDict and add conversations&questions to listwidget
        for fileName in os.listdir(self.conversationDir):
            if fileName.endswith('.txt'):
                conversationFilePath = Path(self.conversationDir).joinpath(fileName).as_posix()
                questionFilePath = Path(self.questionDir).joinpath(fileName).as_posix()
                if os.path.getsize(conversationFilePath) == 0: # Remove empty files
                    os.remove(conversationFilePath)
                    os.remove(questionFilePath) if Path(questionFilePath).exists() else None
                    continue
                historyID, conversationName = self._getHistoryIDAndConversationName(conversationFilePath)
                self._updateMessageDict(historyID, conversationName)
        return self.messagesDict

    def getHistory(self, historyID):
        conversationName = self._getConversationName(historyID)
        # Load from file
        conversationFilePath, questionFilePath = self._getHistoryFilePath(historyID, conversationName)
        with open(conversationFilePath, 'r', encoding = 'utf-8') as f:
            messages = [eval(message.strip()) for message in f.read().splitlines()] #messages = [json.loads(message) for message in f.readlines()]
        with open(questionFilePath, 'r', encoding = 'utf-8') as f:
            question = f.read().strip()
        return messages, question

    def createConversation(self, name):
        historyID = EasyUtils.generateRandomString() # Generate a random string
        conversationFilePath, questionFilePath = self._getHistoryFilePath(historyID, name)
        # Setup files
        with open(conversationFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        with open(questionFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        # Init message
        historyID, conversationName = self._getHistoryIDAndConversationName(conversationFilePath)
        self._updateMessageDict(historyID, conversationName)
        #self.applyPrompt(promptID)
        return historyID, conversationName

    def renameConversation(self, historyID, newName):
        oldName = self._getConversationName(historyID)
        oldConversationFilePath, oldQuestionFilePath = self._getHistoryFilePath(historyID, oldName)
        newConversationFilePath, newQuestionFilePath = self._getHistoryFilePath(historyID, newName)
        # Rename file
        os.rename(oldConversationFilePath, newConversationFilePath)
        os.rename(oldQuestionFilePath, newQuestionFilePath)
        # Transfer&Remove message
        self._updateMessageDict(historyID, newName)
        #self.applyPrompt(promptID)

    def deleteConversation(self, historyID):
        conversationName = self._getConversationName(historyID)
        conversationFilePath, questionFilePath = self._getHistoryFilePath(historyID, conversationName)
        # Remove file
        os.remove(conversationFilePath)
        os.remove(questionFilePath)
        # Remove messages
        self.messagesDict.pop(historyID)

    def saveConversation(self, historyID, messages: list):
        conversationName = self._getConversationName(historyID)
        conversationFilePath, _ = self._getHistoryFilePath(historyID, conversationName)
        # Save to file
        with open(conversationFilePath, 'w', encoding = 'utf-8') as f:
            conversationStr = '\n'.join(json.dumps(message, ensure_ascii = False) for message in messages)
            f.write(conversationStr)

    def saveQuestion(self, historyID, question: str):
        conversationName = self._getConversationName(historyID)
        _, questionFilePath = self._getHistoryFilePath(historyID, conversationName)
        # Save to file
        with open(questionFilePath, 'w', encoding = 'utf-8') as f:
            questionStr = question.strip()
            f.write(questionStr)

    def applyPrompt(self, promptID):
        prompt = self.getPrompt(promptID)
        for historyID, _ in self.messagesDict.copy().items():
            messages, _ = self.getHistory(historyID)
            for message in messages.copy():
                messages.remove(message) if message['role'] == 'system' else None # Remove previous prompt if exists
            messages.append(
                {
                    'role': 'system',
                    'content': prompt
                }
            )
            # Save conversation
            self.saveConversation(historyID, messages)

    def addUserMessage(self, historyID, userMessage: dict):
        messages, _ = self.getHistory(historyID)
        messages.append(userMessage)
        # Save conversation
        self.saveConversation(historyID, messages)

    def recieveAnswer(self, historyID, recievedText):
        messages, _ = self.getHistory(historyID)
        if messages[-1]['role'] == 'assistant':
            messages[-1]['content'] += recievedText
        if messages[-1]['role'] == 'user':
            messages.append({'role': 'assistant', 'content': recievedText})
        # Save conversation
        self.saveConversation(historyID, messages)
        return messages

##############################################################################################################################