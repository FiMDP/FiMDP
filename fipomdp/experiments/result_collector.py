from statistics import stdev


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ResultCollector(metaclass=Singleton):

    preprocessing_time = 0
    _rewards = []
    _decision_times = []

    def get_results(self):
        return self.preprocessing_time, self._rewards, stdev(self._rewards), self._decision_times, stdev(self._decision_times)

    def add_rewards(self, reward: float):
        self._rewards.append(reward)

    def add_decision_time(self, decision_time: float):
        self._decision_times.append(decision_time)
