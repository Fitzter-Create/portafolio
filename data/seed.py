import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import init_db, save_personal, save_experience, save_skills, save_projects, save_education, save_blog_posts

init_db()

import json
from data.database import change_password

save_personal({
    "name": "Tu Nombre",
    "title": "Desarrollador Full Stack",
    "email": "tu@email.com",
    "phone": "+52 555 123 4567",
    "location": "Ciudad de México, MX",
    "bio": "Desarrollador apasionado por crear soluciones tecnológicas elegantes y funcionales. Especializado en Python, FastAPI y desarrollo web moderno.",
    "avatar": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=400",
    "social": {
        "github": "https://github.com/tuusuario",
        "linkedin": "https://linkedin.com/in/tuusuario",
        "twitter": "https://twitter.com/tuusuario"
    }
})

save_experience([
    {
        "company": "Empresa Tech S.A.",
        "position": "Desarrollador Senior",
        "period": "2022 - Presente",
        "description": "Lideré el desarrollo de APIs con FastAPI, migración de microservicios y optimización de bases de datos."
    },
    {
        "company": "Startup Innovadora",
        "position": "Desarrollador Full Stack",
        "period": "2020 - 2022",
        "description": "Construcción de aplicación web con React y FastAPI, integración con servicios cloud."
    },
    {
        "company": "Agencia Digital",
        "position": "Desarrollador Junior",
        "period": "2018 - 2020",
        "description": "Desarrollo de sitios web responsivos y mantenimiento de sistemas legacy."
    }
])

save_skills({
    "Lenguajes": ["Python", "JavaScript", "TypeScript", "Java", "SQL"],
    "Frameworks": ["FastAPI", "React", "Django", "Flask", "Next.js"],
    "Herramientas": ["Git", "Docker", "AWS", "PostgreSQL", "MongoDB"],
    "Otros": ["CI/CD", "REST APIs", "GraphQL", "Linux", "Scrum"]
})

save_projects([
    {
        "title": "Sistema de Gestión",
        "description": "Plataforma web para gestión de inventarios con FastAPI y React.",
        "tech": ["FastAPI", "React", "PostgreSQL", "Docker"],
        "url": "https://github.com/tuusuario/proyecto1",
        "image": "https://placehold.co/600x400/141414/D4AF37?text=Proyecto+1"
    },
    {
        "title": "API de Machine Learning",
        "description": "API REST para predicciones usando modelos de ML con FastAPI.",
        "tech": ["FastAPI", "TensorFlow", "Redis", "Docker"],
        "url": "https://github.com/tuusuario/proyecto2",
        "image": "https://placehold.co/600x400/141414/D4AF37?text=Proyecto+2"
    },
    {
        "title": "Blog Personal",
        "description": "Blog con editor Markdown, comentarios y panel admin.",
        "tech": ["Next.js", "FastAPI", "MongoDB", "Vercel"],
        "url": "https://github.com/tuusuario/proyecto3",
        "image": "https://placehold.co/600x400/141414/D4AF37?text=Proyecto+3"
    }
])

save_education([
    {
        "institution": "Universidad Nacional",
        "degree": "Ingeniería en Sistemas Computacionales",
        "period": "2014 - 2018",
        "description": "Titulación con honores. Enfoque en desarrollo de software y bases de datos."
    },
    {
        "institution": "Platzi",
        "degree": "Escuela de Desarrollo Web",
        "period": "2019",
        "description": "Cursos avanzados de Python, JavaScript, React y Docker."
    },
    {
        "institution": "Coursera",
        "degree": "Machine Learning Specialization",
        "period": "2020",
        "description": "Especialización en ML con Stanford University y DeepLearning.AI."
    }
])

save_blog_posts([
    {
        "title": "Introducción a FastAPI",
        "date": "15 Enero 2024",
        "summary": "Guía completa para empezar con FastAPI, el moderno framework web para Python.",
        "tags": ["Python", "FastAPI", "Tutorial"],
        "url": "/blog/intro-fastapi"
    },
    {
        "title": "Arquitectura Limpia en Python",
        "date": "20 Diciembre 2023",
        "summary": "Cómo aplicar principios de arquitectura limpia en proyectos Python.",
        "tags": ["Python", "Arquitectura", "Clean Code"],
        "url": "/blog/clean-architecture-python"
    },
    {
        "title": "Microservicios con FastAPI y Docker",
        "date": "10 Noviembre 2023",
        "summary": "Implementación de microservicios escalables usando FastAPI y contenedores Docker.",
        "tags": ["FastAPI", "Docker", "Microservicios"],
        "url": "/blog/microservicios-fastapi-docker"
    }
])

print("Datos insertados correctamente en Turso!")
