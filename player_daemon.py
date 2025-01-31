from mpv_controller import MPVController
import time

if __name__ == '__main__':
    controller = MPVController()
    controller.run()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
