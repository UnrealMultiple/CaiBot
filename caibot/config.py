from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    bot_superadmin_id: int = 3042538328
    bot_admin_group_id: int = 991556763
    db_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/caibot"
