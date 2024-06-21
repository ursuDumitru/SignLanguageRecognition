import numpy as np
import os

# import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import PReLU


class Model:
    def __init__(self, sign_labels_file_path, data_set_path, model_save_path, random_state) -> None:
        self.sign_labels_file_path = sign_labels_file_path
        self.data_set_path = data_set_path
        self.model_save_path = model_save_path
        self.sign_labels = []
        self.random_state = random_state

        self.model = None

    def get_sign_labels(self):
        """
        This method is used to get the sign labels from the CSV file and
        automatically updates the sign_labels attribute.
        """
        # check if file exists
        try:
            with open(self.sign_labels_file_path, 'r') as file:
                sign_labels = file.read().splitlines()
                file.close()
                self.sign_labels = np.array(sign_labels)

        except FileNotFoundError:
            print(f"Error: File '{self.sign_labels_file_path}' not found!")
            exit(1)  # FIXME: maybe handle this better ?

    def save_model(self):
        self.model.save(self.model_save_path)


# noinspection DuplicatedCode
class ModelStatic(Model):
    def __init__(self, sign_labels_file_path,
                 data_set_path, model_save_path,
                 random_state):
        super().__init__(sign_labels_file_path,
                         data_set_path,
                         model_save_path,
                         random_state)

        self.get_sign_labels()

        self.model = Sequential([
            Input((21 * 2,)),
            Dense(256, activation=PReLU()),
            Dropout(0.2),
            Dense(128, activation=PReLU()),
            Dense(len(self.sign_labels),
                  activation='sigmoid')
        ])

    def load_data_set(self):
        x_data = np.loadtxt(self.data_set_path,
                            delimiter=',',
                            dtype='float32',
                            usecols=list(range(1, 43)))
        y_data = np.loadtxt(self.data_set_path,
                            delimiter=',',
                            dtype='int32',
                            usecols=0)

        return train_test_split(x_data,
                                to_categorical(y_data,
                                               len(self.sign_labels)),
                                test_size=0.2,
                                random_state=55)


class ModelDynamic(Model):
    def __init__(self, sign_labels_file_path,
                 data_set_path, model_save_path,
                 random_state):
        super().__init__(sign_labels_file_path,
                         data_set_path,
                         model_save_path,
                         random_state)

        self.data_set_signs_path = []
        self.get_sign_labels()

        self.model = Sequential([
            GRU(256, return_sequences=True,
                activation=PReLU(),
                input_shape=(30, 21 * 2)),
            GRU(128, return_sequences=True,
                activation=PReLU()),
            GRU(64, return_sequences=False,
                activation=PReLU()),
            Dense(64, activation=PReLU()),
            Dropout(0.2),
            Dense(32, activation=PReLU()),
            Dense(len(self.sign_labels),
                  activation='sigmoid')
        ])

        # self.model = Sequential([
        #     GRU(256, return_sequences=True, activation=PReLU(), input_shape=(30, 21 * 2)),
        #     GRU(128, return_sequences=True, activation=PReLU()),
        #     GRU(64, return_sequences=False, activation=PReLU()),
        #     Dense(64, activation=PReLU()),
        #     Dropout(0.2),
        #     Dense(32, activation=PReLU()),
        #     Dense(len(self.sign_labels), activation='sigmoid')
        # ])

    def get_data_set_dirs(self):
        """
        This method is used to create a directory for each sign label for data collecting.
        """
        try:
            if not os.path.isdir(self.data_set_path):
                raise FileNotFoundError
            else:
                for sign_label in self.sign_labels:
                    self.data_set_signs_path.append(self.data_set_path + "/" + sign_label)
        except FileNotFoundError:
            print(f"Directory '{self.data_set_path}' does not exist.")

    def load_data_set(self):
        x_data = []
        y_data = []

        self.get_data_set_dirs()
        for i, sign_dir in enumerate(
                self.data_set_signs_path):
            for file in os.listdir(sign_dir):
                data = np.load(sign_dir + "/" + file)
                x_data.append(data)
                y_data.append(i)

        return train_test_split(np.array(x_data),
                                to_categorical(y_data,
                                               len(self.sign_labels)),
                                test_size=0.2,
                                random_state=self.random_state)
