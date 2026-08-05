from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    DATABASE_HOST=os.environ.get('DATABSE_HOST'),
    DATABASE_PORT=os.environ.get('DATABSE_PORT'),
    DATABASE_NAME= os.environ.get('DATABASE_NAME'),
    DATABASE_USER=os.environ.get('DATABSE_USER'),
    DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD')