import gymnasium
import suika_env
import numpy as np
import imageio

def make_env():
    return gymnasium.make("SuikaEnv-v0")

def make_grid(images):
    # Assuming images is a list of 4 images of the same size
    top = np.concatenate(images[:2], axis=1)  # concatenate along width
    bottom = np.concatenate(images[2:], axis=1)  # concatenate along width
    return np.concatenate([top, bottom], axis=0)  # concatenate along height

if __name__ == "__main__":
    env = gymnasium.vector.AsyncVectorEnv([make_env for _ in range(4)])
    try:
        # Create a list to store all grid images
        grid_images = []
        obs, info = env.reset()
        # Make a 2x2 grid of images
        grid_image = make_grid(obs['image'])
        grid_images.append(grid_image)


        for _ in range(10):  # replace 100 with the number of steps you want to take
            print("step", _)
            actions = env.action_space.sample()  # replace with your action selection logic
            obs, rewards,terminated, trucnated, info = env.step(actions)

            # Make a 2x2 grid of images
            grid_image = make_grid(obs['image'])
            grid_images.append(grid_image)

        # Save all grid images as a GIF
        imageio.mimsave('grid_images.gif', grid_images, fps=10)  # adjust fps as needed
    finally:
        env.close()