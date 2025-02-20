import random
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []

index = count()


def animate(i,x):
    r = random.randint(0,5)
    z = x*r
    print(r,x,z)
    x_vals.append(next(index))
    y_vals.append(z)
    
    plt.cla()
    plt.plot(x_vals,y_vals)


ani = FuncAnimation(plt.gcf(), animate, fargs=(20,), interval=1000)

plt.tight_layout()
plt.show()