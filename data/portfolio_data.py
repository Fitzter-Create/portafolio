from data.database import (
    init_db, get_personal, save_personal as _save_personal,
    get_experience, save_experience as _save_experience,
    get_skills, save_skills as _save_skills,
    get_projects, save_projects as _save_projects,
    get_education, save_education as _save_education,
    get_blog_posts, save_blog_posts as _save_blog_posts,
    check_password, change_password,
)

init_db()

personal = get_personal()
experience = get_experience()
skills = get_skills()
projects = get_projects()
education = get_education()
blog_posts = get_blog_posts()


_on_reload_callbacks = []


def on_reload(callback):
    _on_reload_callbacks.append(callback)


def reload():
    global personal, experience, skills, projects, education, blog_posts
    personal = get_personal()
    experience = get_experience()
    skills = get_skills()
    projects = get_projects()
    education = get_education()
    blog_posts = get_blog_posts()
    for cb in _on_reload_callbacks:
        cb()


def save_personal(data):
    _save_personal(data)
    reload()


def save_experience(data):
    _save_experience(data)
    reload()


def save_skills(data):
    _save_skills(data)
    reload()


def save_projects(data):
    _save_projects(data)
    reload()


def save_education(data):
    _save_education(data)
    reload()


def save_blog_posts(data):
    _save_blog_posts(data)
    reload()
