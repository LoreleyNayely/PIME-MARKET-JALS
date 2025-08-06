from app.core.camel_case_config import CamelBaseModel

class User(CamelBaseModel):
    email: str
    name: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_reset_password: bool = False
    
