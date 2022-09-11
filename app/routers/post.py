from .. import models, schemas, oauth2
from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# @app.get("/posts")
# def get_posts():
#     cursor.execute("""select * from posts""")
#     posts = cursor.fetchall()
#     return {"data": posts}

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id
        ).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts

# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_posts(post: Post):
#     cursor.execute("""insert into posts (title, content, published) values (%s, %s, %s) returning * """, 
#                                                 (post.title, post.content, post.published))
#     new_post =  cursor.fetchone()
#     conn.commit()
#     return {"data": new_post}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# @app.get("/posts/{id}")
# def get_post(id: int):
#     cursor.execute("""select * from posts where id = %s """, (id,))
#     post = cursor.fetchone()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
#     return {"post_detail": post}

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    return post


# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):

#     cursor.execute("""delete from posts where id = %s returning * """, (id,))
#     deleted_post = cursor.fetchone()
#     conn.commit()

#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform the requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# @app.put("/posts/{id}")
# def update_post(id: int, post: Post):
    
#     cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning * """, 
#     (post.title, post.content, post.published, id))
    
#     updated_post = cursor.fetchone()
#     conn.commit()

#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

#     return {"data": updated_post}


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform the requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()