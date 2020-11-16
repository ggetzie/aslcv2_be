unmanaged = ["spatialarea", "spatialcontext", "objectfind", 
             "materialcategory", "areatype", "contexttype"]

class DefaultRouter:
    def db_for_read(self, model, **hints):
        if model._meta.model_name not in unmanaged:
            return "default"

    def db_for_write(self, model, **hints):
        if model._meta.model_name not in unmanaged:        
            return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name not in unmanaged:                
            return True

class ArchaeologyRouter:

    def db_for_read(self, model, **hints):
        if model._meta.model_name in unmanaged:                
            return "archaeology"        

    def db_for_write(self, model, **hints):
        if model._meta.model_name in unmanaged:                
            return "archaeology"                
    
    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return False
