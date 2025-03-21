from menu_item import MenuItem

class Food(MenuItem):
    def __init__(self, name, price, calorie):
        super().__init__(name, price)
        self.calorie = calorie

    def info(self):
        return self.name + ': ¥' + self.price + ' (' + str(self.calorie) + 'kcal)'
        #正しくはstr(self.price)

    def calorie_info(self):
        print(str(self.calorie) + 'kcalです')
