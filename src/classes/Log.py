import time # 'Zaman bilgisi ve Yazılımı bekletme' işlemleri için kullanıyoruz.
import traceback # Hata ayıklama için mevcut hata detaylarını gösterir.
import os
from src.utils.helper import getConfig

CONFIG = getConfig()
PATH = str(CONFIG["logging"]["path"])
LEVEL = int(CONFIG["logging"]["minimumLevel"])
SIZE = int(CONFIG["logging"]["fileSizeLimitMegabytes"])
PRINTCONSOLE = bool(CONFIG["logging"]["printLogsToConsole"])

# Konsol yazılarını renklendirebilmek için kullanılan sınıf
class Log:
    # Log kayıtları için kullanılan fonksiyon
    def __init__(self, printConsole:bool=PRINTCONSOLE, logFolder:str=PATH, logLevel:int=LEVEL, maxFileSizeMB:int=SIZE):
        if not 1 <= logLevel <= 5:
            raise ValueError("'logLevel' value must be between 1 and 5.")
        self.printConsole = printConsole
        self.logFolder = logFolder
        self.logLevel = logLevel
        self.maxFileSizeMB = maxFileSizeMB
        if not os.path.exists(self.logFolder):
            os.makedirs(self.logFolder)

    def _log(self, message:str, level:int):
        try:
            if level <= self.logLevel:
                filePath = self._getLastLogFile()
                if os.path.exists(filePath):
                    currentSize = os.path.getsize(filePath) / (1024*1024) # Dosya boyutunu MB cinsinden alır.
                    if currentSize > self.maxFileSizeMB: # Dosya boyutu, hedef boyuttan fazla ise yeni bir Log dosyası oluşturur.
                        self.createLogFile()
                    del currentSize
                logTime = time.strftime("[%d.%m.%Y %H:%M:%S]") # Mevcut zamanı 'gün.ay.yıl saat:dakika:saniye' formatında String olarak bir değişkende tutar.
                levelTags = {1: "[CRITICAL]", 2: "[ERROR]", 3: "[WARNING]", 4: "[INFO]", 5: "[DEBUG]"}
                logText = f"{logTime} {levelTags[level]} {message}"
                if self.printConsole and level != 5: # Log kayıtlarını konsole yazdırma seçeneği True ise VE yazdırılacak log mesajının seviyesi Debug değil ise koşul sağlanır.
                    print(logText) # Log kaydını konsole yazdırır.
                with open(filePath, "a", encoding="utf-8") as file: # Dosya mevcut ise içerisine ekleme yapar. Mevcut değil ise oluşturur.
                    file.write(f"{logText}\n")
                del logTime, levelTags, logText
        except Exception as e:
            errorName = type(e).__name__ # Yakalanan hatanın adını String olarak alır.
            errorMessage = f"[{errorName}]\n{traceback.format_exc()}"
            with open(filePath, "a", encoding="utf-8") as file:
                file.write(f"LogError: {errorMessage}\n")
    
    def createLogFile(self) -> str:
        fileName = time.strftime("log_%d%m%Y-%H%M%S.log") # Dosya adını 'log_günAyYıl-SaatDakika.log' olarak tutar.
        filePath = os.path.join(self.logFolder, fileName)
        with open(filePath, "w", encoding="utf-8") as file:
            file.write("")
        del fileName
        return filePath

    def _getLastLogFile(self) -> str:
        if not os.path.exists(self.logFolder):
            os.makedirs(self.logFolder)
        if len(os.listdir(self.logFolder)) < 1:
            self.createLogFile()
        lastLogFile = os.listdir(self.logFolder)[-1]
        filePath = os.path.join(self.logFolder, lastLogFile)
        del lastLogFile
        return filePath

    # Kritik düzeyde loglamalar için kullanılır.
    def critical(self, message:str):
        self._log(message, 1)

    # Hata düzeyinde loglamalar için kullanılır.
    def error(self, message:str):
        self._log(message, 2)

    # Uyarı düzeyinde loglamalar için kullanılır.
    def warning(self, message:str):
        self._log(message, 3)

    # Bilgi düzeyinde loglamalar için kullanılır.
    def info(self, message:str):
        self._log(message, 4)

    # Geliştirme (debug) düzeyinde loglamalar için kullanılır. Kod detaylarını içerir.
    def debug(self, message:str):
        self._log(message, 5)
