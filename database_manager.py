from imports import *


class DatabaseManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = threading.Lock() 

    def read_data(self):
        with self.lock:
            try:
                return pd.read_csv(self.file_path)
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")
                return pd.DataFrame(columns=['guild_id', 'user_id', 'experience', 'level', 'about_me'])

    def write_data(self, df):
        with self.lock:
            try:
                df.to_csv(self.file_path, index=False)
            except Exception as e:
                print(f"Ошибка при записи в файл: {e}")

    def get_user_data(self, guild_id, user_id):
        df = self.read_data()
        user_data = df[(df['guild_id'] == guild_id) & (df['user_id'] == user_id)]
        if not user_data.empty:
            return user_data.iloc[0]
        return None

    def update_user_data(self, guild_id, user_id, exp_gain=None, about_me=None, level=None):
        df = self.read_data()
        user_data = df[(df['guild_id'] == guild_id) & (df['user_id'] == user_id)]

        if not user_data.empty:
            if exp_gain is not None:
                df.loc[(df['guild_id'] == guild_id) & (df['user_id'] == user_id), 'experience'] += exp_gain
            if about_me is not None:
                df.loc[(df['guild_id'] == guild_id) & (df['user_id'] == user_id), 'about_me'] = about_me
            if level is not None:
                df.loc[(df['guild_id'] == guild_id) & (df['user_id'] == user_id), 'level'] = level
        else:
            new_row = pd.DataFrame({
                'guild_id': [guild_id],
                'user_id': [user_id],
                'experience': [exp_gain if exp_gain is not None else 0],
                'level': [level if level is not None else 1],
                'about_me': [about_me if about_me is not None else "Я не я, корова не моя"]
            })
            df = pd.concat([df, new_row], ignore_index=True)

        self.write_data(df)

