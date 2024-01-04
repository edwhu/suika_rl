from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import gymnasium
import ipdb
import io
import numpy as np    
from PIL import Image
import imageio

DEFAULT_URL = 'http://localhost:8001/'
class SuikaBrowserEnv(gymnasium.Env):
    def __init__(self, headless=True, delay_before_img_capture=0.5) -> None:
        opts = webdriver.ChromeOptions()
        opts.add_argument("--width=1024")
        opts.add_argument("--height=768")
        self.headless = headless
        if headless:
            opts.add_argument("--headless=new")
        self.delay_before_img_capture = delay_before_img_capture
        self.img_width = 128
        self.img_height = 128
        self.driver = webdriver.Chrome(options=opts)
        _obs_dict = {
            'image': gymnasium.spaces.Box(low=0, high=255, shape=(self.img_height, self.img_width, 4),  dtype="uint8"),
            'score': gymnasium.spaces.Box(low=0, high=1000000, shape=(1,), dtype="float32"),
        }
        self.observation_space = gymnasium.spaces.Dict(_obs_dict)
        self.action_space = gymnasium.spaces.Box(low=0, high=1, shape=(1,))

    def reset(self,seed=None, options=None):
        self._reload()
        info = {}
        obs, status = self._get_obs_and_status()
        return obs, info

    def _reload(self):
        # open the game.
        self.driver.get(DEFAULT_URL)
        # click start game button with id "start-game-button"
        self.driver.find_element(By.ID, 'start-game-button').click()
        time.sleep(1)
    
    def _get_obs_and_status(self):
        img = self._capture_canvas()
        status, score = self.driver.execute_script('return [window.Game.stateIndex, window.Game.score];')
        score = np.array([score], dtype=np.float32)
        return dict(image=img, score=score), status
    
    def _capture_canvas(self):
        # screenshots the game canvas with id "game-canvas" and stores it in a numpy array
        canvas = self.driver.find_element(By.ID, 'game-canvas')
        image_string = canvas.screenshot_as_png
        img = Image.open(io.BytesIO(image_string))
        # first crop out right hand side and lower bar.
        img = img.crop((0,0,520,img.height))
        arr = np.asarray(img)
        # imageio.imwrite('cropped.png', arr)
        # import ipdb; ipdb.set_trace()
        imgResized = img.resize((self.img_width,self.img_height), Image.ANTIALIAS) 
        arr = np.asarray(imgResized)
        return arr

    
    def step(self, action):
        driver = self.driver
        action = action[0]
        info = {}
        # action is a float from 0 to 1. need to convert to int from 0 to 640 and then string.
        action = str(int(action * 640))
        # clear the input box with id "fruit-position"
        driver.find_element(By.ID, 'fruit-position').clear()
        # enter in the number into the input box with id "fruit-position"
        driver.find_element(By.ID, 'fruit-position').send_keys(action)
        # click the button with id "drop-fruit-button"
        driver.find_element(By.ID, 'drop-fruit-button').click()
        time.sleep(self.delay_before_img_capture)

        obs, status = self._get_obs_and_status()
        reward = 0
        # check if game is over.
        terminal = status == 3
        truncated = False 
        info['score'] = obs['score'].item()
        reward += obs['score'].item()

        return obs, reward, terminal, truncated, info

    def close(self):
        super().close()
        if self.driver is not None:
            self.driver.quit()

if __name__ == "__main__":
    try:
        env = SuikaBrowserEnv(headless=False, delay_before_img_capture=0.5)
        video = []
        obs, info = env.reset()
        # video.append(obs['image'])
        # import imageio
        terminated = False
        while not terminated:
            action = [0]
            obs, rew, terminated, truncated, info = env.step(action)
            # video.append(obs['image'])
            if terminated:
                break
    finally:
        env.close()