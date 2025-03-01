class ProductionConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@production-db-host:5432/production_db"
    JWT_SECRET_KEY = "your-production-secret-key"
    CORS_ORIGINS = ["https://your-production-frontend.com"]