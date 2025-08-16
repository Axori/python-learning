class MyDB:
    def __init__(self):
        self.DB = {"test": "test"}
        
    def test(self):
        self.DB.update({"test": 2, "test2": "xd"})
        print(self.DB)

myDb = MyDB()
myDb.test()

