# ============================================
# Models -> user
# ============================================

# Importar librerías 
from dataclasses import dataclass

@dataclass
class User:
    username: str
    password: str
    role: str = "viewer"   # Por defecto usuario normal

    def is_admin(self) -> bool:
        return self.role == "admin"