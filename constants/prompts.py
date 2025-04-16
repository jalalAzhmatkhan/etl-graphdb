SYSTEM_PROMPT = """
You are a computer that does just exactly what you are told to do. Spit only the results without additional info. 
Your output is a clean Python dictionary with the keys and values as specified in the prompt.
"""
TRANSFORMER_FROM_MARKDOWN_PROMPT = """
Please extract the following information from the markdown file, and return it in a clean Python dictionary format:
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
    "cov_or_polling": "string_or_null"
}
Please ensure to return \"null\" for any missing values, and use the correct data types as specified.

**Markdown file content example:**
S/N Equipment Location Serving Location Nomenclature Naming ObjectName Read/Write Permission Upper Limit Lower Limit Object Type Device ID Object Instance BACnet IP Address BACnet IP port Mac Address Object Description Units Measurement COV/Polling
1 Level 2 Level 1 PLGS-C1-AHU-02-01 C1_AHU_02_01.OnStatus Read Only NA NA BINARY-VALUE device, 3065035 BinaryValue 1 10.239.226.249 47808 00:50:06:2E:C4:CB C1-AHU-02-01 Running Status NA
**Example response:**
{
    \"s_n\": 1,
    \"equipment_location\": \"Level 2\",
    \"serving_location\": \"Level 1\",
    \"nomenclature_naming\": \"PLGS-C1-AHU-02-01\",
    \"object_name\": \"C1_AHU_02_01.OnStatus\",
    \"read_or_write_permission\": \"Read Only\",
    \"upper_limit\": \"NA\",
    \"lower_limit\": \"NA\",
    \"object_type\": \"BINARY-VALUE\",
    \"device_id\": \"device, 3065035\",
    \"object_instance\": \"BinaryValue 1\",
    \"bacnet_ip_address\": \"10.239.226.249\",
    \"bacnet_ip_port\": 47808,
    \"mac_address\": \"00:50:06:2E:C4:CB\",
    \"object_description\": \"C1-AHU-02-01 Running Status\",
    \"units_measurement\": \"NA\",
    \"cov_or_polling\": \"null\"
}
**Markdown file content example:**
S/N Equipment Location Serving Location Nomenclature Naming ObjectName Read/Write Permission Upper Limit Lower Limit Object Type Device ID Object Instance BACnet IP Address BACnet IP port Mac Address Object Description Units Measurement COV/Polling
Level 2 Level 1 PLGS-C1-AHU-02-01 C1_AHU_02_01.SATemp_SP Read Only NA NA ANALOG VALUE device, 3065035 Analog Value 19 10.239.226.249 47808 00:50:06:2E:C4:CB C1-AHU-02-01 Supply Air Temperature Setpoint  ℃
**Example response:**
{
    \"s_n\": \"null\",
    \"equipment_location\": \"Level 2\",
    \"serving_location\": \"Level 1\",
    \"nomenclature_naming\": \"PLGS-C1-AHU-02-0\",
    \"object_name\": \"C1_AHU_02_01.SATemp_SP\",
    \"read_or_write_permission\": \"Read Only\",
    \"upper_limit\": \"NA\",
    \"lower_limit\": \"NA\",
    \"object_type\": \"ANALOG VALUE\",
    \"device_id\": \"device, 3065035\",
    \"object_instance\": \"Analog Value 19\",
    \"bacnet_ip_address\": \"10.239.226.249\",
    \"bacnet_ip_port\": 47808,
    \"mac_address\": \"00:50:06:2E:C4:CB\",
    \"object_description\": \"C1-AHU-02-01 Supply Air Temperature Setpoint\",
    \"units_measurement\": \"℃\",
    \"cov_or_polling\": \"null\"
}

**Now here's the real markdown content:**
"""
TRANSFORMER_QUERY_ACMV_PROMPT = """
You are a computer that does just exactly what you are told to do. Spit only the results without additional info.
Your output is a clean Python dictionary with the keys and values as specified in the prompt.

Given a nomenclature naming of a sensor: <nomenclature_name>, please find the data from this ACMV relation and return a clean Python dictionary like:

```
{
  "location": "string_or_null",
  "first_layer": "string_or_null",
  "second_layer": "string_or_null",
  "third_layer": "string_or_null",
  "serving_area": "string_or_null",
  "zone": "string_or_null"
  "status": "found_or_not_found"
}
```
"""
