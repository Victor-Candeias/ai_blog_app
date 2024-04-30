from django.apps import AppConfig
import structlog

class BlogGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_generator'
    
logger = structlog.get_logger()
logger.info("Logging with structlog")
