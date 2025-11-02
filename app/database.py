"""
Database connection modules for PostgreSQL and MongoDB
"""
import os
from typing import Optional
import psycopg2
from psycopg2 import pool
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient


_postgres_pool: Optional[pool.ThreadedConnectionPool] = None


def get_postgres_config():
    """Get PostgreSQL configuration from environment variables"""
   
    postgres_url = os.getenv('POSTGRES_URL')
    if postgres_url:
        from urllib.parse import urlparse
        parsed = urlparse(postgres_url)
        config = {
            'host': parsed.hostname,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username,
            'password': parsed.password,
            'port': parsed.port or 5432
        }
       
        config['sslmode'] = 'require'
        return config
    
   
    config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'database': os.getenv('POSTGRES_DB', 'agroyield'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'port': int(os.getenv('POSTGRES_PORT', '5432'))
    }
    
    
    ssl_required = os.getenv('POSTGRES_SSL', 'false').lower() == 'true'
    if ssl_required or not config['host'] == 'localhost':
        config['sslmode'] = 'require'
    
    return config


def init_postgres_pool():
    """Initialize PostgreSQL connection pool"""
    global _postgres_pool
    if _postgres_pool is None:
        config = get_postgres_config()
        _postgres_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **config
        )
    return _postgres_pool


def get_postgres_conn():
    """Get a PostgreSQL connection from the pool"""
    pool = init_postgres_pool()
    return pool.getconn()


def return_postgres_conn(conn):
    """Return a PostgreSQL connection to the pool"""
    if _postgres_pool:
        _postgres_pool.putconn(conn)



_mongo_client: Optional[MongoClient] = None
_async_mongo_client: Optional[AsyncIOMotorClient] = None


def get_mongo_uri():
    """Get MongoDB URI from environment variables"""
    return os.getenv('MONGO_URI', 'mongodb://localhost:27017/')


def get_mongo_client():
    """Get synchronous MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = get_mongo_uri()
        _mongo_client = MongoClient(mongo_uri)
    return _mongo_client


def get_async_mongo_client():
    """Get asynchronous MongoDB client"""
    global _async_mongo_client
    if _async_mongo_client is None:
        mongo_uri = get_mongo_uri()
        _async_mongo_client = AsyncIOMotorClient(mongo_uri)
    return _async_mongo_client


def get_mongo_db(db_name: str = 'agroyeild'):
    """Get MongoDB database instance"""
    client = get_mongo_client()
    return client[db_name]


async def get_async_mongo_db(db_name: str = 'agroyeild'):
    """Get asynchronous MongoDB database instance"""
    client = get_async_mongo_client()
    return client[db_name]


def close_postgres_pool():
    """Close PostgreSQL connection pool"""
    global _postgres_pool
    if _postgres_pool:
        _postgres_pool.closeall()
        _postgres_pool = None


def close_mongo_clients():
    """Close MongoDB clients"""
    global _mongo_client, _async_mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
    if _async_mongo_client:
        _async_mongo_client.close()
        _async_mongo_client = None
