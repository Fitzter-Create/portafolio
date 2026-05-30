from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeTimedSerializer
from data import portfolio_data

app = FastAPI(title="Mi Portafolio")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _sync_globals():
    templates.env.globals["personal"] = portfolio_data.personal


_sync_globals()
portfolio_data.on_reload(_sync_globals)

SECRET_KEY = "portafolio-secret-key-cambiar-en-produccion"
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="admin-session")


def create_session_token():
    return serializer.dumps({"admin": True, "ts": datetime.utcnow().isoformat()})


def get_admin_session(request: Request) -> Optional[str]:
    token = request.cookies.get("admin_session")
    if not token:
        return None
    try:
        data = serializer.loads(token, max_age=86400)
        if data.get("admin"):
            return token
    except Exception:
        return None
    return None


async def require_admin(request: Request):
    if not get_admin_session(request):
        raise HTTPException(status_code=303, detail="No autorizado")


# --- Public routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    return templates.TemplateResponse(
        "projects.html",
        {"request": request, "projects": portfolio_data.projects}
    )


@app.get("/education", response_class=HTMLResponse)
async def education(request: Request):
    return templates.TemplateResponse(
        "education.html",
        {"request": request, "education": portfolio_data.education}
    )


@app.get("/blog", response_class=HTMLResponse)
async def blog(request: Request):
    return templates.TemplateResponse(
        "blog.html",
        {"request": request, "blog_posts": portfolio_data.blog_posts}
    )


# --- Admin auth ---

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    if get_admin_session(request):
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request}
    )


@app.post("/admin/login")
async def admin_login_post(request: Request, password: str = Form(...)):
    if portfolio_data.check_password(password):
        token = create_session_token()
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(
            key="admin_session",
            value=token,
            max_age=86400,
            httponly=True,
            samesite="lax"
        )
        return response
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Contraseña incorrecta"}
    )


@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("admin_session")
    return response


# --- Admin dashboard ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _=Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "personal": portfolio_data.personal,
            "projects_count": len(portfolio_data.projects),
            "education_count": len(portfolio_data.education),
            "blog_count": len(portfolio_data.blog_posts),
        }
    )


# --- Admin: Personal ---

@app.get("/admin/personal", response_class=HTMLResponse)
async def admin_personal(request: Request, _=Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/personal.html",
        {"request": request}
    )


@app.post("/admin/personal")
async def admin_personal_post(
    request: Request,
    name: str = Form(...),
    title: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    bio: str = Form(...),
    avatar: str = Form(...),
    github: str = Form(""),
    linkedin: str = Form(""),
    twitter: str = Form(""),
    _=Depends(require_admin)
):
    portfolio_data.save_personal({
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "location": location,
        "bio": bio,
        "avatar": avatar,
        "social": {
            "github": github,
            "linkedin": linkedin,
            "twitter": twitter,
        }
    })
    return RedirectResponse(url="/admin/personal?success=1", status_code=303)


# --- Admin: Projects ---

@app.get("/admin/projects", response_class=HTMLResponse)
async def admin_projects(request: Request, _=Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/projects.html",
        {"request": request, "projects": portfolio_data.projects}
    )


@app.post("/admin/projects/add")
async def admin_projects_add(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    tech: str = Form(...),
    url: str = Form(""),
    image: str = Form(""),
    _=Depends(require_admin)
):
    proj = portfolio_data.projects.copy()
    proj.append({
        "title": title,
        "description": description,
        "tech": [t.strip() for t in tech.split(",") if t.strip()],
        "url": url,
        "image": image or f"https://placehold.co/600x400/141414/D4AF37?text={title.replace(' ', '+')}"
    })
    portfolio_data.save_projects(proj)
    return RedirectResponse(url="/admin/projects", status_code=303)


@app.post("/admin/projects/edit/{index}")
async def admin_projects_edit(
    request: Request,
    index: int,
    title: str = Form(...),
    description: str = Form(...),
    tech: str = Form(...),
    url: str = Form(""),
    image: str = Form(""),
    _=Depends(require_admin)
):
    proj = portfolio_data.projects.copy()
    if 0 <= index < len(proj):
        proj[index] = {
            "title": title,
            "description": description,
            "tech": [t.strip() for t in tech.split(",") if t.strip()],
            "url": url,
            "image": image or f"https://placehold.co/600x400/141414/D4AF37?text={title.replace(' ', '+')}"
        }
        portfolio_data.save_projects(proj)
    return RedirectResponse(url="/admin/projects", status_code=303)


@app.post("/admin/projects/delete/{index}")
async def admin_projects_delete(
    request: Request,
    index: int,
    _=Depends(require_admin)
):
    proj = portfolio_data.projects.copy()
    if 0 <= index < len(proj):
        proj.pop(index)
        portfolio_data.save_projects(proj)
    return RedirectResponse(url="/admin/projects", status_code=303)


# --- Admin: Education ---

@app.get("/admin/education", response_class=HTMLResponse)
async def admin_education(request: Request, _=Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/education.html",
        {"request": request, "education": portfolio_data.education}
    )


@app.post("/admin/education/add")
async def admin_education_add(
    request: Request,
    institution: str = Form(...),
    degree: str = Form(...),
    period: str = Form(...),
    description: str = Form(...),
    _=Depends(require_admin)
):
    edu = portfolio_data.education.copy()
    edu.append({
        "institution": institution,
        "degree": degree,
        "period": period,
        "description": description
    })
    portfolio_data.save_education(edu)
    return RedirectResponse(url="/admin/education", status_code=303)


@app.post("/admin/education/edit/{index}")
async def admin_education_edit(
    request: Request,
    index: int,
    institution: str = Form(...),
    degree: str = Form(...),
    period: str = Form(...),
    description: str = Form(...),
    _=Depends(require_admin)
):
    edu = portfolio_data.education.copy()
    if 0 <= index < len(edu):
        edu[index] = {
            "institution": institution,
            "degree": degree,
            "period": period,
            "description": description
        }
        portfolio_data.save_education(edu)
    return RedirectResponse(url="/admin/education", status_code=303)


@app.post("/admin/education/delete/{index}")
async def admin_education_delete(
    request: Request,
    index: int,
    _=Depends(require_admin)
):
    edu = portfolio_data.education.copy()
    if 0 <= index < len(edu):
        edu.pop(index)
        portfolio_data.save_education(edu)
    return RedirectResponse(url="/admin/education", status_code=303)


# --- Admin: Blog ---

@app.get("/admin/blog", response_class=HTMLResponse)
async def admin_blog(request: Request, _=Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/blog.html",
        {"request": request, "blog_posts": portfolio_data.blog_posts}
    )


@app.post("/admin/blog/add")
async def admin_blog_add(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    summary: str = Form(...),
    tags: str = Form(...),
    url: str = Form(""),
    _=Depends(require_admin)
):
    posts = portfolio_data.blog_posts.copy()
    posts.append({
        "title": title,
        "date": date,
        "summary": summary,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "url": url or f"/blog/{title.lower().replace(' ', '-')}"
    })
    portfolio_data.save_blog_posts(posts)
    return RedirectResponse(url="/admin/blog", status_code=303)


@app.post("/admin/blog/edit/{index}")
async def admin_blog_edit(
    request: Request,
    index: int,
    title: str = Form(...),
    date: str = Form(...),
    summary: str = Form(...),
    tags: str = Form(...),
    url: str = Form(""),
    _=Depends(require_admin)
):
    posts = portfolio_data.blog_posts.copy()
    if 0 <= index < len(posts):
        posts[index] = {
            "title": title,
            "date": date,
            "summary": summary,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "url": url or f"/blog/{title.lower().replace(' ', '-')}"
        }
        portfolio_data.save_blog_posts(posts)
    return RedirectResponse(url="/admin/blog", status_code=303)


@app.post("/admin/blog/delete/{index}")
async def admin_blog_delete(
    request: Request,
    index: int,
    _=Depends(require_admin)
):
    posts = portfolio_data.blog_posts.copy()
    if 0 <= index < len(posts):
        posts.pop(index)
        portfolio_data.save_blog_posts(posts)
    return RedirectResponse(url="/admin/blog", status_code=303)
