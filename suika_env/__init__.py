from gymnasium.envs.registration import register as register
print("registering suika env")
register(
    id="SuikaEnv-v0",
    entry_point='suika_env.suika_browser_env:SuikaBrowserEnv',
    max_episode_steps=100,
)
