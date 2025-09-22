from sqlalchemy import event
from src.database.models import User
from src.conf.settings import redis_client


@event.listens_for(User, "after_update")
def clear_user_cache(mapper, connection, target: User):
    redis_client.delete(f"username:{target.username}")


@event.listens_for(User, "after_delete")
def clear_user_cache_on_delete(mapper, connection, target: User):
    redis_client.delete(f"username:{target.username}")
