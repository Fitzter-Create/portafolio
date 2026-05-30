from data.database import (
    init_db, get_personal, save_personal as _save_personal,
    get_experience, save_experience as _save_experience,
    get_skills, save_skills as _save_skills,
    get_projects, save_projects as _save_projects,
    get_education, save_education as _save_education,
    get_blog_posts, save_blog_posts as _save_blog_posts,
    check_password, change_password,
)

_loaded = False


def _ensure_loaded():
    global _loaded
    if not _loaded:
        init_db()
        reload()
        _loaded = True


_on_reload_callbacks = []


def on_reload(callback):
    _on_reload_callbacks.append(callback)


def reload():
    _data_store["personal"] = get_personal()
    _data_store["experience"] = get_experience()
    _data_store["skills"] = get_skills()
    _data_store["projects"] = get_projects()
    _data_store["education"] = get_education()
    _data_store["blog_posts"] = get_blog_posts()
    for cb in _on_reload_callbacks:
        cb()


_data_store = {}
_DATA_KEYS = {"personal", "experience", "skills", "projects", "education", "blog_posts"}


def __getattr__(name):
    if name in _DATA_KEYS:
        _ensure_loaded()
        return _data_store[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
