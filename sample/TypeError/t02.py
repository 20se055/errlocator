#ClassCastException

from datetime import datetime

map = {}
dt = datetime.now()
map["birthday"] = "2000/01/01"

birthday = dt.strptime(map.get["birthday"], "%Y/%m/%d")

print(birthday)

