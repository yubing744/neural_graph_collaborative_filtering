import os
import pathlib


class User:
    def __init__(self, id, name, remap_id):
        self.id = id
        self.name = name
        self.remap_id = remap_id


class Course:
    def __init__(self, id, name, remap_id):
        self.id = id
        self.name = name
        self.remap_id = remap_id


class UserCourse:
    def __init__(self, user, course):
        self.user = user
        self.course = course


def load_courses(courses_file):
    courses = dict()
    course_num = -1

    with open(courses_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if course_num == -1:
                course_num = course_num + 1
                continue

            if len(line) > 0:
                line = line.strip('\n').split(',')
                course = Course(line[0], line[1], course_num)
                course_num = course_num + 1
                courses[course.id] = course

    return courses


def load_users(users_file):
    users = dict()
    user_num = -1

    with open(users_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if user_num == -1:
                user_num = user_num + 1
                continue

            if len(line) > 0:
                line = line.strip('\n').split(',')
                user = User(line[0], line[1], user_num)
                user_num = user_num + 1
                users[user.id] = user

    return users


def load_user_courses(rel_file, users, courses):
    rels = []

    with open(rel_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if len(line) > 0:
                line = line.strip('\n').split(',')
                uid = line[0]
                cid = line[1]

                if uid in users and cid in courses:
                    user = users[uid]
                    course = courses[cid]
                    uc = UserCourse(user, course)
                    rels.append(uc)

    return rels


def group_course_by_user(ucs: []):
    user_courses = dict()

    for uc in ucs:
        if uc.user in user_courses:
            courses = user_courses[uc.user]
            courses.append(uc.course)
        else:
            user_courses[uc.user] = [uc.course]

    return user_courses


def print_user_courses(ucs):
    for user in ucs:
        courses = ucs[user]
        print(user.name, [c.name for c in courses])


def save_dataset(ucs, dataset, file):
    with open(file, 'w') as f:
        for user in dataset:
            courses = ucs[user]
            f.write("%s %s\n" % (user.remap_id, " ".join([str(c.remap_id) for c in courses])))


def output_dataset(ucs, percent):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(cur_dir, "output")
    output_path = pathlib.Path(output_dir)
    if not output_path.exists():
        os.mkdir(output_path)

    users = [u for u in ucs.keys()]
    train_count = int(len(ucs) * percent)

    train_set = users[0:train_count]
    train_file = os.path.join(output_path, "train.txt")
    save_dataset(ucs, train_set, train_file)

    test_set = users[train_count:]
    test_file = os.path.join(output_path, "test.txt")
    save_dataset(ucs, test_set, test_file)


def output_users(users):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(cur_dir, "output")
    output_path = pathlib.Path(output_dir)
    if not output_path.exists():
        os.mkdir(output_path)

    user_file = os.path.join(output_path, "user_list.txt")
    with open(user_file, 'w') as f:
        f.write("org_id remap_id\n")

        for uid in users:
            user = users[uid]
            f.write("%s %d\n" % (user.id, user.remap_id))


def output_courses(courses):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(cur_dir, "output")
    output_path = pathlib.Path(output_dir)
    if not output_path.exists():
        os.mkdir(output_path)

    user_file = os.path.join(output_path, "course_list.txt")
    with open(user_file, 'w') as f:
        f.write("org_id remap_id\n")

        for cid in courses:
            course = courses[cid]
            f.write("%s %d\n" % (course.id, course.remap_id))


def convert_dataset(train_perc):
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    # 1. 加载user.csv
    user_csv_file = os.path.join(cur_dir, "./user.csv")
    users = load_users(user_csv_file)
    print("user count:", len(users))

    # 2. 加载 course.csv
    course_csv_file = os.path.join(cur_dir, "./course.csv")
    courses = load_courses(course_csv_file)
    print("course count:", len(courses))

    # 3. 加载 rel_user_course.csv
    uc_csv_file = os.path.join(cur_dir, "./rel_user_course.csv")
    ucs = load_user_courses(uc_csv_file, users, courses)
    print("user course count:", len(ucs))

    # 4. 按用户分组，并输出分组结果
    user_courses = group_course_by_user(ucs)
    print("user_courses count:", len(user_courses))
    print_user_courses(user_courses)

    # 5. 导出训练集和测试集，train_perc为训练集占比
    output_dataset(user_courses, train_perc)
    output_users(users)
    output_courses(users)

    print("convert ok!")


if __name__ == '__main__':
    convert_dataset(0.8)
