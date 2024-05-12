from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['blog_database']

# Define MongoDB collections
posts_collection = db['posts']
comments_collection = db['comments']

# Define models
class Post(BaseModel):
    title: str
    content: str

class Comment(BaseModel):
    post_id: str
    content: str

class Like(BaseModel):
    post_id: str
    action: str

# Define endpoints
@app.post("/posts/", response_model=Post)
async def create_post(post: Post):
    post_id = posts_collection.insert_one(post.dict()).inserted_id
    return {**post.dict(), "id": str(post_id)}

@app.get("/posts/", response_model=List[Post])
async def get_posts():
    return list(posts_collection.find())

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: str):
    post = posts_collection.find_one({"_id": post_id})
    if post:
        return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: str, post: Post):
    posts_collection.update_one({"_id": post_id}, {"$set": post.dict()})
    return post

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    posts_collection.delete_one({"_id": post_id})
    return {"message": "Post deleted successfully"}

@app.post("/comments/", response_model=Comment)
async def create_comment(comment: Comment):
    comment_id = comments_collection.insert_one(comment.dict()).inserted_id
    return {**comment.dict(), "id": str(comment_id)}

@app.get("/comments/{post_id}", response_model=List[Comment])
async def get_comments(post_id: str):
    return list(comments_collection.find({"post_id": post_id}))

@app.post("/likes/")
async def like_post(like: Like):
    if like.action.lower() not in ['like', 'dislike']:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'like' or 'dislike'.")
    posts_collection.update_one({"_id": like.post_id}, {"$inc": {like.action.lower(): 1}})
    return {"message": f"Post {like.action.lower()}d successfully"}

