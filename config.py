from environs import Env

class ConfigDataLoader:

    env = Env()
    env.read_env()

    UA = env('UA')
    