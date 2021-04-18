from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
import numpy as np

def bfs(curr_boards, curr_cell):
    next_boards = []
    for ind in range(len(curr_boards)):
        if ind == 0: zero_used = False
        cb = curr_boards[ind]
        for i in av_nums[curr_cell]:
            if (cb[3*(curr_cell[0]//3):3*(curr_cell[0]//3)+3,
                3*(curr_cell[1]//3):3*(curr_cell[1]//3)+3] == i).sum() == 0 and \
                (cb[curr_cell[0],:] == i).sum() == 0 and \
                (cb[:,curr_cell[1]] == i).sum() == 0:
                nb = np.copy(cb)
                nb[curr_cell[0],curr_cell[1]] = i
                if ind == 0: zero_used = True
                next_boards.append(nb)
    return next_boards, zero_used

profile_path = 'to_fill'
selenium_exe_path = 'to_fill'

options = Options()
profile = webdriver.FirefoxProfile(profile_path)
driver = webdriver.Firefox(options=options, firefox_profile=profile,
            executable_path=selenium_exe_path)

driver.maximize_window()
driver.get('https://www.websudoku.com/?level=4')
sleep(7)
for g in range(10):
    frame = driver.find_element_by_xpath('/html/frameset/frame')
    driver.switch_to.frame(frame)
    cells = {}
    av_nums = {}
    for i in range(9):
        for j in range(9):
            av_nums[(i, j)] = {k for k in range(1, 10)}
    board = np.zeros(shape=(9,9), dtype=np.int32)
    to_fill = []
    for i in range(9):
        for j in range(9):
            cell = driver.find_element_by_xpath("//input[contains(@id, 'f" + str(j) + str(i) + "')]")
            try:
                k = int(cell.get_attribute('value'))
                board[i,j] = k
                for r in range(9):
                    if k in av_nums[(r,j)]:
                        av_nums[(r,j)].remove(k)
                for c in range(9):
                    if k in av_nums[(i,c)]:
                        av_nums[(i,c)].remove(k)
                sq = (3*(i//3), 3*(j//3))
                for r in range(3):
                    for c in range(3):
                        if k in av_nums[(sq[0]+r, sq[1]+c)]:
                            av_nums[(sq[0]+r, sq[1]+c)].remove(k)
            except:
                to_fill.append((i,j))
            cells[(i,j)] = cell

    curr_boards = [board]
    curr_cell = [0,0]
    k = 0
    #to_fill.sort(key= lambda x: len(av_nums[x]))
    while len(curr_boards) > 0 and k < len(to_fill):
        curr_cell = to_fill[k]
        print(curr_cell, len(curr_boards))
        curr_boards, zero_used = bfs(curr_boards, curr_cell)
        if not zero_used:
            for i in range(k):
                v = cells[to_fill[i]].get_attribute('value')
                if v != '':
                    if int(v) != curr_boards[0][to_fill[i][0],to_fill[i][1]]:
                        cells[to_fill[i]].clear()
                        cells[to_fill[i]].send_keys(str(curr_boards[0][to_fill[i][0],to_fill[i][1]]))
                else:
                    cells[to_fill[i]].send_keys(str(curr_boards[0][to_fill[i][0], to_fill[i][1]]))
        cells[to_fill[k]].send_keys(str(curr_boards[0][to_fill[k][0], to_fill[k][1]]))
        (i, j) = to_fill[k]
        k += 1
    cells[to_fill[-1]].send_keys(str(curr_boards[0][to_fill[-1][0], to_fill[-1][1]]))
    cells[to_fill[-1]].send_keys(Keys.ENTER)
    sleep(1)
    driver.get('https://www.websudoku.com/?level=4')
driver.close()
driver.quit()
