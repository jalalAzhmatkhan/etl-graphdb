SYSTEM_PROMPT = """
You are a computer that does just exactly what you are told to do. 
Spit only the results without additional info. 
Your output is a clean Python dictionary with the keys and values as specified in the prompt.
"""
TRANSFORMER_FROM_MARKDOWN_PROMPT = """
Please extract the following information from the markdown file, and return it in a clean list of Python dictionaries format:
[
  {
     "s_n": integer_or_null,
     "equipment_location": "string_or_null",
     "serving_location": "string_or_null",
     "nomenclature_naming": "string_or_null",
     "object_name": "string_or_null",
     "read_or_write_permission": "string_or_null",
     "upper_limit": "string_or_null",
     "lower_limit": "string_or_null",
     "object_type": "string_or_null",
     "device_id": "string_or_null",
     "object_instance": "string_or_null",
     "bacnet_ip_address": "string_or_null",
     "bacnet_ip_port": integer_or_null,
     "mac_address": "string_or_null",
     "object_description": "string_or_null",
     "units_measurement": "string_or_null",
     "cov_or_polling": "string_or_null",
  }
]
"""
