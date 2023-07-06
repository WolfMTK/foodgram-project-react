class PathDirError(Exception):
    def __init__(self, *args: object):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'{self.message}'
        return 'Ошибка! Путь до необходимой папки указан неверно!'
