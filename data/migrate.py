import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(os.path.dirname(__file__), "portfolio.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

from data.database import init_db, save_personal, save_experience, save_skills, save_projects, save_education, save_blog_posts

init_db()
print("Tablas creadas.")

p = data["personal"]
save_personal({
    "name": p["name"],
    "title": p["title"],
    "email": p["email"],
    "phone": p["phone"],
    "location": p["location"],
    "bio": p["bio"],
    "avatar": p["avatar"],
    "social": {
        "github": p.get("social", {}).get("github", ""),
        "linkedin": p.get("social", {}).get("linkedin", ""),
        "twitter": p.get("social", {}).get("twitter", ""),
    }
})
print("Personal migrado.")

save_experience(data["experience"])
print(f"Experiencia migrada ({len(data['experience'])} items).")

save_skills(data["skills"])
print(f"Habilidades migradas ({len(data['skills'])} categorias).")

save_projects(data["projects"])
print(f"Proyectos migrados ({len(data['projects'])} items).")

save_education(data["education"])
print(f"Educacion migrada ({len(data['education'])} items).")

save_blog_posts(data["blog_posts"])
print(f"Blog migrado ({len(data['blog_posts'])} items).")

print("Migracion completada!")
