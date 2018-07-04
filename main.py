import time
from carrefour import Carrefour

carrefour = Carrefour()

while(True):
    carrefour.update()
    carrefour.output()
    time.sleep(1)