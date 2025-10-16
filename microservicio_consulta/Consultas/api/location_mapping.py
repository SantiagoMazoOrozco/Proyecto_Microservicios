import unicodedata

# Diccionario para mapear ciudades a departamentos en Colombia
city_to_department = {
 'Manizales': 'Caldas',
    'Chinchiná': 'Caldas',  # Segunda ciudad importante
    'Bogotá': 'Cundinamarca',
    'Medellín': 'Antioquia',
    'Envigado': 'Antioquia',  # Segunda ciudad importante
    'Cali': 'Valle del Cauca',
    'Palmira': 'Valle del Cauca',  # Segunda ciudad importante
    'Pereira': 'Risaralda',
    'Dosquebradas': 'Risaralda',  # Segunda ciudad importante
    'Armenia': 'Quindío',
    'Circasia': 'Quindío',  # Segunda ciudad importante
    'Leticia': 'Amazonas',
    'Arauca': 'Arauca',
    'Barranquilla': 'Atlántico',
    'Soledad': 'Atlántico',  # Segunda ciudad importante
    'Cartagena': 'Bolívar',
    'Magangué': 'Bolívar',  # Segunda ciudad importante
    'Tunja': 'Boyacá',
    'Sogamoso': 'Boyacá',  # Segunda ciudad importante
    'Bucaramanga': 'Santander',
    'Floridablanca': 'Santander',  # Segunda ciudad importante
    'Popayán': 'Cauca',
    'Santander de Quilichao': 'Cauca',  # Segunda ciudad importante
    'Yopal': 'Casanare',
    'Florencia': 'Caquetá',
    'Valledupar': 'Cesar',
    'Aguachica': 'Cesar',  # Segunda ciudad importante
    'Quibdó': 'Chocó',
    'Istmina': 'Chocó',  # Segunda ciudad importante
    'Montería': 'Córdoba',
    'Lorica': 'Córdoba',  # Segunda ciudad importante
    'Inírida': 'Guainía',
    'San José del Guaviare': 'Guaviare',
    'Neiva': 'Huila',
    'Pitalito': 'Huila',  # Segunda ciudad importante
    'Riohacha': 'La Guajira',
    'Maicao': 'La Guajira',  # Segunda ciudad importante
    'Santa Marta': 'Magdalena',
    'Ciénaga': 'Magdalena',  # Segunda ciudad importante
    'Villavicencio': 'Meta',
    'Acacías': 'Meta',  # Segunda ciudad importante
    'Pasto': 'Nariño',
    'Ipiales': 'Nariño',  # Segunda ciudad importante
    'San Andrés': 'San Andrés y Providencia',
    'Mocoa': 'Putumayo',
    'Cúcuta': 'Norte de Santander',
    'Ocaña': 'Norte de Santander',  # Segunda ciudad importante
    'Sincelejo': 'Sucre',
    'Corozal': 'Sucre',  # Segunda ciudad importante
    'Ibagué': 'Tolima',
    'Espinal': 'Tolima',  # Segunda ciudad importante
    'Mitú': 'Vaupés',
    'Puerto Carreño': 'Vichada'
    # Puedes agregar más ciudades principales o secundarias según sea necesario
}

# Build a normalized lookup dict once
def _normalize_text(s):
    if not s:
        return None
    s = s.strip()
    # remove accents/diacritics
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    return s.title()

_normalized_city_to_department = { _normalize_text(k): v for k, v in city_to_department.items() }

def get_department_by_city(city):
    """
    Obtiene el departamento correspondiente a una ciudad.
    Devuelve None si no hay coincidencia.
    """
    if not city:
        return None
    key = _normalize_text(city)
    return _normalized_city_to_department.get(key)

# Diccionario para mapear departamentos a zonas en Colombia
department_to_zone = {
    'Caldas': 'Eje Cafetero',
    'Quindío': 'Eje Cafetero',
    'Risaralda': 'Eje Cafetero',
    'Cundinamarca': 'Bogotá',
    'Antioquia': 'Medellín',
    'Valle del Cauca': 'Valle',
    'Atlántico': 'Costa',
    'Bolívar': 'Costa',
    'Magdalena': 'Costa',
    'Córdoba': 'Costa',
    'Sucre': 'Costa',
    'La Guajira': 'Costa',
    'San Andrés y Providencia': 'Costa',
    'Cesar': 'Costa',
    # Agrega más departamentos y zonas según sea necesario
}

def get_zone_by_department(department):
    return department_to_zone.get(department)

# Diccionario para mapear departamentos a regiones en Colombia
department_to_region = {
    'Caldas': 'Eje Cafetero',
    'Quindío': 'Eje Cafetero',
    'Risaralda': 'Eje Cafetero',
    'Cundinamarca': 'Bogotá',
    'Antioquia': 'Medellín',
    'Valle del Cauca': 'Valle',
    'Atlántico': 'Costa',
    'Bolívar': 'Costa',
    'Magdalena': 'Costa',
    'Córdoba': 'Costa',
    'Sucre': 'Costa',
    'La Guajira': 'Costa',
    'San Andrés y Providencia': 'Costa',
    'Cesar': 'Costa',
    # Agrega más departamentos y regiones según sea necesario
}

def get_region_by_department(department):
    """
    Obtiene la región correspondiente a un departamento.
    Devuelve None si no existe.
    """
    if not department:
        return None
    return department_to_region.get(department)
