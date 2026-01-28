import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait                 #changed
from selenium.webdriver.support import expected_conditions as EC        #changed
from selenium.webdriver.common.by import By 
import requests.packages.urllib3.exceptions
import pprint
import webbrowser
import fnmatch, logging
import getopt  # command parameter support
import os
import shutil



def createHansyLink(log):
    hansy_generated_link=""    
    #driver=webdriver.Firefox(executable_path="C:/Users/CMN3KOR/Downloads/v3 ref/geckodriver.exe")
    executable_path="C:/Users/CMN3KOR/Downloads/v3 ref/geckodriver.exe" #changed
    os.environ["PATH"] += os.pathsep + executable_path       #changed
    driver = webdriver.Firefox()                             #changed
    driver.implicitly_wait(0.5)
    driver.get("http://fe0vm20pemaivi.de.bosch.com:8083/")
    #s = driver.find_element_by_name("file")
    wait = WebDriverWait(driver, 5)                                       #changed
    s = wait.until(EC.presence_of_element_located((By.NAME, "file")))     #changed
    abso_path=os.path.abspath(log)
    s.send_keys(abso_path)
    s.submit()
    hansy_loading_link=driver.current_url
    print("Hansy Loading Link: "+hansy_loading_link)
    print("Hansy link generation in progress...")
    while(hansy_loading_link==driver.current_url):
        #print("--")
        pass
    hansy_generated_link=driver.current_url
    print("Hansy_generated_link: "+hansy_generated_link)
    driver.close()
    hansyLinkRenameTimes=0
    currentLog=log
    while(hansy_generated_link=="http://fe0vm20pemaivi.de.bosch.com:8083/upload"):
        if(hansyLinkRenameTimes==0):
            if os.path.exists("temp\\"):
                shutil.rmtree("temp\\")
            os.mkdir("temp\\")
        hansyLinkRenameTimes=hansyLinkRenameTimes+1
        renamedLog=renamelogToUploadInHansy(currentLog,hansyLinkRenameTimes)
        hansy_generated_link=createHansyLinkRenamedUpload(renamedLog)
        os.remove(renamedLog)
        #currentLog=renamedLog
        #createHansyLink(renamedLog)
        #hansy_generated_link="Em Trace already uploaded in Hansy. For reset summary, please search attached decoded EM trace filename in http://fe0vm20pemaivi.de.bosch.com:8083/"
        #hansy_generated_link="http://fe0vm20pemaivi.de.bosch.com:8083/show_report_by_name/"+attachment_name+"?uploaded=1"
    """
    if os.path.exists("temp\\"):
        shutil.rmtree("temp\\")
    """
    return hansy_generated_link
    
def createHansyLinkRenamedUpload(renamedLog):
    hansy_generated_link=""    
    #driver=webdriver.Firefox(executable_path="C:/Users/CMN3KOR/Downloads/v3 ref/geckodriver.exe")
    executable_path="C:/Users/CMN3KOR/Downloads/v3 ref/geckodriver.exe" #changed
    os.environ["PATH"] += os.pathsep + executable_path       #changed
    driver = webdriver.Firefox()                             #changed
    driver.implicitly_wait(0.5)
    driver.get("http://fe0vm20pemaivi.de.bosch.com:8083/")
    #s = driver.find_element_by_name("file")
    wait = WebDriverWait(driver, 5)                                       #changed
    s = wait.until(EC.presence_of_element_located((By.NAME, "file")))     #changed
    abso_path=os.path.abspath(renamedLog)
    s.send_keys(abso_path)
    s.submit()
    hansy_loading_link=driver.current_url
    print("Hansy Loading Link: "+hansy_loading_link)
    print("Hansy link generation in progress...")
    while(hansy_loading_link==driver.current_url):
        #print("--")
        pass
    hansy_generated_link=driver.current_url
    print("Hansy_generated_link: "+hansy_generated_link)
    driver.close()   
    return hansy_generated_link
    
def renamelogToUploadInHansy(log,hansyLinkRenameTimes):
    shutil.copy(log,"temp\\")
    basename = os.path.basename(log)
    copiedlog_path="temp\\"+basename
    suffix_name=str(hansyLinkRenameTimes)
    filename,extension = os.path.splitext(basename)
    renamedlog_path="temp\\"+filename+"__renamed_for_HansyUpload_"+suffix_name+extension
    os.rename(copiedlog_path,renamedlog_path)
    print(renamedlog_path)
    return renamedlog_path