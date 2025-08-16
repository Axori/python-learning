class FileOpener:
    def __enter__(self):
        print("enter")
        return {}
    def __exit__(self, type, value, traceback):
        print("exit {0}, {1}, {2}", type, value, traceback)
        return True

with FileOpener() as fo:
    # fo.undefined()
    print("inside")
