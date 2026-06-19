class Selection():

  per_page = 10

  model_types = [
    ('ollama', 'Ollama'),
  ]

  category_types = [
    ('addressType', 'Address Type'),
    ('contactType', 'Contact Type'),
    ('emailType', 'Email Type'),
    ('phoneType', 'Phone Type'),
    ('eventType', 'Event Type')
  ]

  abstract_ethnicities = [
    ('hispanic', 'Hispanic'),
    ('middle_eastern', 'Middle Eastern'),
    ('indian', 'Indian'),
    ('african', 'African / African American'),
    ('asian', 'Asian'),
    ('white', 'White / Caucasian'),
  ]

  primary_languages = [
    ('english', 'English'),
    ('spanish', 'Spanish'),
    ('french', 'French'),
    ('chinese', 'Chinese'),
    ('japanese', 'Japanese'),
    ('korean', 'Korean'),
  ]

  api_types = [
    ('api', 'API'),
    ('rss', 'RSS'),
    ('scraper', 'Page Scraper'),
  ]

  available_databases = {
    "investigation_db": "Investigation",
    "investigator_db": "Investigator",
    "determinator_db": "Determinator"
  }

  available_collections = {
    "missing_persons": "Missing Persons",
    "database_statements": "Database Statements",
    "investigation_instructions": "Investigation Instructions"
  }

  data_entities = [
    'people',
    'aliases',
    'addresses',
    'email_addresses',
    'phone_numbers',
    'files',
    'events',
    'leads'
  ]

  # GPU selections
  available_devices = {
    # Standard Devices
    "cpu": "CPU", #Standard Central Processing Unit
    "cuda": "NVIDIA GPU", # (shorthand for cuda:0)
    # "cuda:0": "Specific NVIDIA GPU by index",

    # Apple Silicon & Mobile
    "mps": "MPS", # Metal Performance Shaders (Apple Silicon M1/M2/M3)
    "npu": "NPU", # Neural Processing Unit (found in specialized AI hardware)

    # Intel & Specialized Accelerators
    "xpu": "XPU", # Intel Data Center or Arc GPU (requires Intel Extension for PyTorch)
    "mlu": "MLU", # Cambricon MLU (requires Cambricon PyTorch extension)
    "tpu": "TPU", # Google Cloud Tensor Processing Unit
    "ipu": "IPU", # Graphcore Intelligence Processing Unit

    # Emerging & Vendor Specific
    "sdaa": "SDAA", # Metax specialized hardware accelerator
    "musa": "MUSA", # Moore Threads MUSA GPU

    # Automated Logic
    "meta": "Meta", # Device used for loading large model skeletons without allocating RAM
    None: "Auto-detects" # Auto-detects best available hardware (typically CUDA -> CPU)
  }

  fileType_select = [
    ("image", "Image"),
    ("pdf", "Pdf"),
  ]

  loader_select = [
    ("docling", "DoclingLoader"),
    ("pypdf", "PyPDFLoader")
  ]
