from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from minio import Minio
from minio.error import S3Error
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)

_mongo_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None
_minio: Minio | None = None


# ─── MongoDB ────────────────────────────────────────────────────

def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
        )
    return _mongo_client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_mongo_client()[settings.MONGO_DB_NAME]
    return _db


async def init_mongo():
    """Connect to MongoDB and create indexes."""
    db = get_db()
    try:
        await get_mongo_client().admin.command("ping")
        logger.info(f"MongoDB connected: {settings.MONGO_URI}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

    # users indexes
    await db.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("uid", ASCENDING)], unique=True),
    ])

    # images indexes
    await db.images.create_indexes([
        IndexModel([("uid", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("uid", ASCENDING), ("is_favorite", ASCENDING)]),
        IndexModel([("uid", ASCENDING), ("tags", ASCENDING)]),
        IndexModel([("uid", ASCENDING), ("detected_objects", ASCENDING)]),
        IndexModel([("image_id", ASCENDING)], unique=True),
        IndexModel([("filename", TEXT), ("tags", TEXT)]),
    ])

    # vaults indexes
    await db.vaults.create_indexes([
        IndexModel([("uid", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("vault_id", ASCENDING)], unique=True),
    ])

    logger.info("MongoDB indexes created.")


async def close_mongo():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB connection closed.")


# ─── MinIO ──────────────────────────────────────────────────────

def get_minio() -> Minio:
    global _minio
    if _minio is None:
        _minio = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    return _minio


def init_minio():
    """Ensure bucket exists and is public-readable."""
    import json
    client = get_minio()
    bucket = settings.MINIO_BUCKET
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"MinIO bucket created: {bucket}")

        policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"]
            }]
        })
        client.set_bucket_policy(bucket, policy)
        logger.info(f"MinIO bucket ready: {bucket}")
    except S3Error as e:
        logger.error(f"MinIO init error: {e}")
        raise