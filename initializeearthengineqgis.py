import ee

try:
    ee.Initialize(project='ee-hemedl')
    print("Earth Engine initialized successfully")
except Exception as e:
    print("Initialization failed, authenticating...")
    ee.Authenticate()
    ee.Initialize(project='ee-hemedl')
    print("Earth Engine authenticated and initialized")
