class ServiceContainer:
    def __init__(self):
        self._singletons = {}

    def register_singleton(self, name, instance):
        self._singletons[name] = instance

    def resolve(self, name):
        if name not in self._singletons:
            print(f"[service_container] Missing: {name} → Registered: {list(self._singletons.keys())}")
            raise KeyError(f"Service '{name}' not registered")
        return self._singletons[name]
# Core/service_container.py  (inside ServiceContainer)
    def try_resolve(self, name: str):
        try:
            return self.resolve(name)
        except Exception:
            return None

