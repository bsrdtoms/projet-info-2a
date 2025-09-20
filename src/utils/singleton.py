class Singleton(type):
    """
    Toutes les classes qui hériteront de Singleton n'auront qu'une seule et unique instance
    -> https://refactoring.guru/fr/design-patterns/singleton
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
