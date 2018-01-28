class AbstractImageManager:
    """
    Знает как расположены спрайты на входном изображении и умеет ключу
    изображения (т.е. либо имя, либо число мин вокруг ячейки)
    сопоставлять непосредственно изображение
    """
    def __init__(self, filename):
        self.image_map = {}

    def get(self, key):
        return self.image_map.get(key)
