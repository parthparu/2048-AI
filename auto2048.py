import pygame
import sys
import random
import math

# ---------- Heuristics ----------
def empty_tile_heuristic(grid):
    return sum(row.count(0) for row in grid)

def smoothness_heuristic(grid):
    smoothness = 0
    for x in range(4):
        for y in range(4):
            if grid[x][y]:
                value = math.log2(grid[x][y])
                for dx, dy in [(1,0), (0,1)]:
                    nx, ny = x+dx, y+dy
                    while 0 <= nx < 4 and 0 <= ny < 4:
                        if grid[nx][ny]:
                            target_value = math.log2(grid[nx][ny])
                            smoothness -= abs(value - target_value)
                            break
                        nx += dx
                        ny += dy
    return smoothness

def monotonicity_heuristic(grid):
    totals = [0,0,0,0]
    for x in range(4):
        row = grid[x]
        for i in range(3):
            a = math.log2(row[i]) if row[i] else 0
            b = math.log2(row[i+1]) if row[i+1] else 0
            if a > b:
                totals[0] += b-a
            elif b > a:
                totals[1] += a-b
    for y in range(4):
        col = [grid[x][y] for x in range(4)]
        for i in range(3):
            a = math.log2(col[i]) if col[i] else 0
            b = math.log2(col[i+1]) if col[i+1] else 0
            if a > b:
                totals[2] += b-a
            elif b > a:
                totals[3] += a-b
    return max(totals[0],totals[1]) + max(totals[2],totals[3])

def max_tile_heuristic(grid):
    return math.log2(max(max(r) for r in grid)) if max(max(r) for r in grid) else 0

def combined_heuristic(grid):
    return (2.7*empty_tile_heuristic(grid) +
            1.0*max_tile_heuristic(grid) +
            0.1*smoothness_heuristic(grid) +
            1.0*monotonicity_heuristic(grid))

# ---------- Game Logic ----------
def initialize_game():
    grid = [[0]*4 for _ in range(4)]
    add_random_tile(grid)
    add_random_tile(grid)
    return grid

def add_random_tile(grid):
    empty = [(r,c) for r in range(4) for c in range(4) if grid[r][c]==0]
    if empty:
        r,c = random.choice(empty)
        grid[r][c] = 2 if random.random()<0.9 else 4

def game_over(grid):
    if any(0 in r for r in grid): return False
    for x in range(4):
        for y in range(4):
            if x<3 and grid[x][y]==grid[x+1][y]: return False
            if y<3 and grid[x][y]==grid[x][y+1]: return False
    return True

def reverse(grid): return [r[::-1] for r in grid]

def rotate(grid,times=1):
    times%=4
    for _ in range(times):
        grid=[list(r) for r in zip(*grid[::-1])]
    return grid

def merge_left(grid):
    new=[]
    for r in grid:
        line=[x for x in r if x!=0]
        i=0
        while i<len(line)-1:
            if line[i]==line[i+1]:
                line[i]*=2
                del line[i+1]
                line.append(0)
            i+=1
        line+=[0]*(4-len(line))
        new.append(line)
    return new

def move(grid,dir):
    if dir=="left":
        return merge_left(grid)
    if dir=="right":
        return reverse(merge_left(reverse(grid)))
    if dir=="up":
        return rotate(merge_left(rotate(grid)), -1)
    if dir=="down":
        return rotate(merge_left(rotate(grid,-1)),1)
    return grid

def get_possible_moves(grid):
    res=[]
    for d in ["up","down","left","right"]:
        ng=move(grid,d)
        if ng!=grid: res.append((d,ng))
    return res

# ---------- AI (Expectimax) ----------
transposition_table={}
def expectimax(grid,depth,player,max_depth=3):
    tup=tuple(tuple(r) for r in grid)
    if (tup,depth,player) in transposition_table:
        return transposition_table[(tup,depth,player)]
    if depth==max_depth or game_over(grid):
        s=combined_heuristic(grid)
        transposition_table[(tup,depth,player)]=(s,None)
        return s,None
    if player:
        best=-1e9; bd=None
        for d,ng in get_possible_moves(grid):
            s,_=expectimax(ng,depth+1,False,max_depth)
            if s>best: best,bd=s,d
        transposition_table[(tup,depth,player)]=(best,bd)
        return best,bd
    else:
        score=0
        empty=[(r,c) for r in range(4) for c in range(4) if grid[r][c]==0]
        if not empty:
            score=combined_heuristic(grid)
            return score,None
        for r,c in empty:
            for val,p in [(2,0.9),(4,0.1)]:
                ng=[row[:] for row in grid]
                ng[r][c]=val
                s,_=expectimax(ng,depth+1,True,max_depth)
                score+=s*(p/len(empty))
        transposition_table[(tup,depth,player)]=(score,None)
        return score,None

# ---------- Pygame UI ----------
pygame.init()
size=500
screen=pygame.display.set_mode((size,size))
pygame.display.set_caption("2048 AI")
font=pygame.font.SysFont("arial",40,True)

colors={0:(200,200,200),2:(238,228,218),4:(237,224,200),8:(242,177,121),
        16:(245,149,99),32:(246,124,95),64:(246,94,59),
        128:(237,207,114),256:(237,204,97),512:(237,200,80),
        1024:(237,197,63),2048:(237,194,46)}

def draw_grid(grid):
    screen.fill((187,173,160))
    cell=size//4
    for r in range(4):
        for c in range(4):
            val=grid[r][c]
            rect=pygame.Rect(c*cell,r*cell,cell,cell)
            pygame.draw.rect(screen,colors.get(val,(60,58,50)),rect)
            if val:
                text=font.render(str(val),True,(0,0,0))
                text_rect=text.get_rect(center=rect.center)
                screen.blit(text,text_rect)
    pygame.display.flip()

def play_game():
    global transposition_table
    grid=initialize_game()
    clock=pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
        draw_grid(grid)
        if any(2048 in r for r in grid):
            print("2048 reached! 🎉")
            pygame.time.wait(2000)
            return
        if game_over(grid):
            print("Game Over!")
            pygame.time.wait(2000)
            return
        _,d=expectimax(grid,0,True,3)
        if d is None: return
        grid=move(grid,d)
        add_random_tile(grid)
        clock.tick(10)  # speed (moves/sec)

if __name__=="__main__":
    play_game()
