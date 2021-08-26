import os


class LogisimValues:

    def __init__(self) -> None:
        self.PATH_TO_DATA = "Logisim_data/"
        self.all_data = {}

        files = os.listdir(self.PATH_TO_DATA)

        for file in files:

            with open(f"{self.PATH_TO_DATA}{file}", "r+") as cur_file:
                read_cur_file = cur_file.read().replace("v3.0 hex words plain\n", "")
                read_cur_file = read_cur_file.replace(" ", "\n").strip().split("\n")

                for index, item in enumerate(read_cur_file):
                    read_cur_file[index] = int(item, 16)

                self.all_data[file] = read_cur_file

                # cur_file.seek(0)
                # cur_file.write(read_cur_file)
                # cur_file.truncate()

            # print(self.all_data)
            # break

    def get_value(self, file_name, index):
        try:
            return self.all_data[file_name][index]

        except Exception:
            return -1


if __name__ == "__main__":
    x = LogisimValues()
    y = x.get_value("PC", 0)
    print(y)
