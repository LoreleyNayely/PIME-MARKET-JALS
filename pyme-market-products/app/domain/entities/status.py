from app.core.camel_case_config import CamelBaseModel

class Status(CamelBaseModel):
    code: str
    description: str
