#!/usr/bin/env python3
"""
timesheet_fill.py by Melissa Chow, 2022

A script to fill in hours automatically in Accenture MyTE Portal. 
Please remember to double check your hours.ini file that login and project information are accurate if recently changed.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import configparser
import os
import time

TIMEOUT = 75 #seconds

def main():
    start_time = time.time()

    # Setup
    config = read_config()
    driver = webdriver.Chrome("chromedriver") #path to chromedriver.exe

    # Username entry
    driver.get(config['url'])
    wait(driver, (By.ID, "i0116"), "username input")
    driver.find_element(by=By.NAME, value="loginfmt").send_keys(config["username"]) #username input
    driver.find_element(by=By.ID, value="idSIButton9").click() #submit

    # Password entry
    wait(driver, (By.ID, "i0118"), "password input")
    driver.find_element(by=By.NAME, value="passwd").send_keys(config["password"]) #password input
    driver.find_element(by=By.ID, value="idSIButton9").click() #submit

    # Fill HOURS table
    time.sleep(1.5)
    #time_table = driver.find_element(by=By.XPATH, value="/html/body/div[7]/form/div[6]/table/tbody/tr/td[2]/div[6]/div[1]/table") #time entry grid
    #/html/body/myte-app/div/myte-page-content/div/div/myte-time/div[1]/div
    time_table = driver.find_element(by=By.XPATH, value="/html/body/myte-app/div/myte-page-content/div/div/myte-time/div[1]/div/ag-grid-angular[1]") #time entry table?
    
    #thead = time_table.find_element(by=By.TAG_NAME, value="thead") #table head
    thead = time_table.find_element(by=By.CLASS_NAME, value="ag-header-row")

    #rows = thead.find_elements(by=By.TAG_NAME, value="tr") #rows in table
    rows = thead.find_elements(by=By.CLASS_NAME, value="ag-header-cell")
    indices = []
    helper_dict = {}
    more_rows = rows[0].find_elements(by=By.TAG_NAME, value="th")
    counter = 3
    for index in range(len(more_rows)-1):
        # find_input = driver.find_element(by=By.XPATH, value="/html/body/div[7]/form/div[6]/table/tbody/tr/td[2]/div[6]/div[1]/table/tbody/tr[12]/td[" + str(counter) + "]")
        # print(find_input.get_attribute('class'))
        # if "Holiday" in find_input.get_attribute('class'):
        #     helper_dict[more_rows[index].get_attribute('abbr') + " - Holiday"] = index
        # else:
        helper_dict[more_rows[index].get_attribute('abbr')] = index
        for days in str_to_list(config['valid_days']):
                if days in more_rows[index].get_attribute('abbr'):
                    indices.append(index)
        #counter+=1

    print(helper_dict)
    print(indices)

    for index in indices:
        # holiday_box = driver.find_element(by=By.XPATH, value="/html/body/div[7]/form/div[6]/table/tbody/tr/td[2]/div[6]/div[1]/table/tbody/tr[12]/td[" + str(index+2) + "]/input[1]").get_attribute('value')
        # is_holiday = True if holiday_box == "8.0" else False
        # if not is_holiday:
        driver.find_element(by=By.XPATH, value="/html/body/div[7]/form/div[6]/table/tbody/tr/td[2]/div[6]/div[1]/table/tbody/tr[1]/td[" + str(index+2) +"]/input[1]").send_keys(8) #time entry input
        driver.find_element(by=By.XPATH, value="/html/body/div[7]/form/div[6]/table/tbody/tr/td[2]/div[6]/div[1]/table/tbody/tr[1]/td[" + str(index+2) +"]/input[1]").send_keys(Keys.ENTER) #enter

    entry_indices = []
    index = 1
    del(helper_dict[''])
    for key in helper_dict:
        if (("Sat" in key or "Sun" in key) and (helper_dict[key] == "01" or helper_dict[key] == "02")):
            index+=1
            entry_indices.append(index)
        elif "Sat" in key or "Sun" in key:
            pass
        elif "Fri" in key:
            index+=2
            entry_indices.append(index)
            index+=2
        else:
            index+=2
            entry_indices.append(index)

    # if "Fri" in key:
    #     index+=2
    #     entry_indices.append(index)
    #     index+=2
    # else:
    #     index+=2
    #     entry_indices.append(index)

    # Fill WORKING HOURS table
    driver.find_element(by=By.XPATH, value="/html/body/div[7]/form/div[6]/table/tbody/tr/td[2]/div[6]/div[2]/table/tbody/tr[5]/td[1]/a").click() #WorkingHoursMenuLink
    WebDriverWait(driver=driver, timeout=TIMEOUT).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "DynamicPopupIframe"))) #iframe
    WebDriverWait(driver=driver, timeout=TIMEOUT).until(EC.presence_of_element_located((By.ID, "ctl00_UpdatePanelPopup"))) #updatePanelPopup

    tr = 0 #table row count
    td = 2 #standard data cell in table count
    tr_counter = 0 #to keep track of entry_indices index
    selector_options = str_to_list(config['select_times'])
    options_index = 0 #index in selector_options array
    for entry_index in range(entry_indices[-1]+1):
        if entry_index in entry_indices:
            tr = entry_indices[tr_counter]
            for selector_row_index in range(9):
                if selector_row_index == 4 or selector_row_index == 8:
                    selector = Select(driver.find_element(by=By.XPATH, value="/html/body/form/div[3]/table/tbody/tr/td[1]/div/table/tbody/tr[" + str(tr) + "]/td[" + str(td) + "]/select")) #meal reason
                    selector.select_by_value('I took my meal break or a meal break is not required.')
                    td = 2
                elif selector_row_index == 5:
                    driver.find_element(by=By.XPATH, value="/html/body/form/div[3]/table/tbody/tr/td[1]/div/table/tbody/tr[" + str(tr) + "]/td[7]/input").click() #plus button
                    tr+=1                    
                    time.sleep(3)
                else:
                    for selector_td_index in range(2):
                        if options_index > 11:
                            continue
                        #WebDriverWait(driver=driver, timeout=TIMEOUT).until(EC.staleness_of((By.XPATH, "/html/body/form/div[3]/table/tbody/tr/td[1]/div/table/tbody/tr[" + str(tr) + "]/td[" + str(td) + "]/select[" + str(j+1) + "]")))
                        selector = Select(driver.find_element(by=By.XPATH, value="/html/body/form/div[3]/table/tbody/tr/td[1]/div/table/tbody/tr[" + str(tr) + "]/td[" + str(td) + "]/select[" + str(selector_td_index+1) + "]")) #time selector
                        selector.select_by_value(selector_options[options_index])
                        options_index+=1
                    if selector_row_index+1 == 8:
                        td+=3
                    else:
                        td+=1
            tr_counter+=1
            options_index = 0
    
    # Save changes
    driver.find_element(by=By.ID, value="ctl00_PopupContentPlaceHolder_WorkingHoursEntryPopUpOkButton").click()
    #driver.find_element(by=By.ID, value="btn_Cancel").click() #press cancel when testing
    driver.switch_to.default_content()

    # Uncomment if eligible/worked OT during pay period - only need to press calculate button if so
    # wait(driver, (By.ID, "btn_recalculate"), "calculate button")
    # driver.find_element(by=By.ID, value="btn_recalculate").click()

    end_time = time.time()
    print("time to execute script: " + str(round(end_time - start_time, 3)) + "s")

    driver.close()

def read_config():
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.realpath(__file__))
    config.read(path + '/hours.ini')
    return config['DEFAULT']

def wait(driver, wait_for_field, whats_this):
    #WebDriverWait(driver=driver, timeout=TIMEOUT).until(lambda x: x.execute_script("return document.readyState === 'complete'")) #for github test
    WebDriverWait(driver=driver, timeout=TIMEOUT).until(EC.element_to_be_clickable(wait_for_field))
    errors = driver.find_elements(by=By.CLASS_NAME, value="flash-error")
    error_message = "Incorrect username or password."
    if any(error_message in e.text for e in errors):
        print("[!] Failed " + error_message)
    else:
        print("[+] Successful " + whats_this)

def str_to_list(convert_list):
    return list(map(str.strip, convert_list.strip('][').replace('"', '').split(',')))

def use_wbs_or_assignment(assignment, wbs):
    if assignment and not wbs:
        return assignment
    elif wbs and not assignment:
        return wbs
    elif assignment and wbs:
        return (assignment, wbs)
    else:
        raise NoChargeCodeError("ERROR: Enter either a charge code (WBS) or assignment name in hours.ini. " + 
        "Assignment name must be the same as the Description in the Assignments Dropdown.")

class NoChargeCodeError(Exception):
    pass

class IncorrectWbsOrAssignment(Exception):
    pass
    
if __name__ == '__main__':
    main()
