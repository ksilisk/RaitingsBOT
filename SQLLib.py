import sqlite3

con = sqlite3.connect('raitings_base.db', check_same_thread=False)
cur = con.cursor()


def check_ban(user_id):
    if cur.execute("SELECT banned FROM users WHERE Id = ?", (user_id,)).fetchall()[0][0] == 1:
        return True
    return False


def add_complaint(user_id):
    cur.execute("UPDATE users SET complaints = complaints + 1 WHERE Id = ?", (user_id,))
    con.commit()


def check_user(user_id):
    if len(cur.execute("SELECT * FROM users WHERE Id = ?", (user_id,)).fetchall()) == 1:
        return True
    return False


def add_user(user_id, position):
    cur.execute("INSERT INTO users (Id, position) VALUES (?,?)", (user_id, position))
    con.commit()


def set_who_to(user_id, text):
    cur.execute("UPDATE users SET who_to = ? WHERE Id = ?", (text, user_id))
    con.commit()


def set_whom_to(user_id, text):
    cur.execute("UPDATE users SET whom_to = ? WHERE Id = ?", (text, user_id))
    con.commit()


def set_position(user_id, position):
    cur.execute("UPDATE users SET position = ? WHERE Id = ?", (position, user_id))
    con.commit()


def get_position(user_id):
    return cur.execute("SELECT position FROM users WHERE Id = ?", (user_id,)).fetchone()[0]


def set_gender(user_id, text):
    cur.execute("UPDATE users SET gender = ? WHERE Id = ?", (text, user_id))
    con.commit()


def get_gender(user_id):
    return cur.execute("SELECT gender FROM users WHERE Id = ?", (user_id,)).fetchone()[0]


def search_photo(user_id): # пофиксить баг
    photos = cur.execute("SELECT file_id, id, user_id FROM photos WHERE photos.id NOT IN ("
                          "SELECT photo_id FROM raitings WHERE user_id = ?) ", (user_id, )).fetchall()
    for photo in photos:
        if (get_whom_to(user_id) == get_gender(photo[2]) or get_whom_to(user_id) == 'all') \
                and (get_who_to(photo[2]) == get_gender(user_id) or get_who_to(photo[2]) == 'all') \
                and (photo[2] != user_id):
            return photo[0:2]
    return 0


def add_new_photo(user_id, file_id):
    cur.execute("INSERT INTO photos (file_id, user_id) VALUES (?,?)", (file_id, user_id))
    con.commit()


def get_whom_to(user_id):
    return cur.execute("SELECT whom_to FROM users WHERE Id = ?", (user_id,)).fetchone()[0]


def get_who_to(user_id):
    return cur.execute("SELECT who_to FROM users WHERE Id = ?", (user_id,)).fetchone()[0]


def add_rait(photo_id, user_id, raiting):
    cur.execute("INSERT INTO raitings (photo_id, user_id, raiting) VALUES (?,?,?)", (photo_id, user_id, raiting))
    con.commit()


def my_photos_raitings(user_id):
    raitings = {}
    photos = cur.execute("SELECT id FROM photos WHERE user_id = ?", (user_id, )).fetchall()
    for photo in photos:
        raitings[photo[0]] = cur.execute("SELECT ROUND(AVG(raiting), 1) FROM raitings WHERE photo_id = ?", (photo[0], )).fetchall()[0][0]
    return raitings


def get_file_id(photo_id):
    return cur.execute("SELECT file_id FROM photos WHERE id = ?", (photo_id,)).fetchone()[0]


def close():
    con.close()


def func():
    print('hello')


if __name__ == '__main__':
    func()
