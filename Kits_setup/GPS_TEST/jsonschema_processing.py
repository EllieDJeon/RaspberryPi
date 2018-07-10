import jsonschema
from jsonshema import validate
import yaml
import os
os.chdir("C:/RasberryPi_CarVi/")

filename = 'GPS_DATA_2018-07-07 19_33_55.json'

filejson = open(filename).read()
filejson = filejson.replace("[{","{").replace("}]","}")
filejson_new = filejson.replace("}, {", "}\n{").replace("}{", "}\n{")
splitfile = filejson_new.split('\n')

import ast
schema_file = open('jsonschema_new.json').read()
schema_file2 = ast.literal_eval(repr(schema_file))

print(json.dumps(schema_file, indent=4))    

schema = {"required":["camera_id", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz",
                      "location", "satellites", "speed", "time_stamp", "altitude", "trip_start",
                      "distance", "emergencyCall", "gps_qual"],
            "type": "object",

            "properties": {
                "ax":{
                    "type": "array",
                    "itmes":{
                        "type": "number"
                    }
                },
                "ay":{
                    "type": "array",
                    "itmes":{
                        "type": "number"

                    }
                },
                "az":{
                    "type": "array",
                    "itmes":{
                        "type": "number"

                    }
                },
                "gx":{
                    "type": "array",
                    "itmes":{
                        "type": "number"
                    }
                },
                "gy":{
                    "type": "array",
                    "itmes":{
                        "type": "number"

                    }
                },
                "gz":{
                    "type": "array",
                    "itmes":{
                        "type": "number"

                    }
                },
                "mx":{
                    "type": "array",
                    "itmes":{
                        "type": "number"
                    }
                },
                "my":{
                    "type": "array",
                    "itmes":{
                        "type": "number"

                    }
                },
                "mz":{
                    "type": "array",
                    "itmes":{
                        "type": "number"

                    }
                },
                "location":{
                    "type": "string",
                },
                "satellites":{
                    "type": "string",
                },
                "speed":{
                    "type": "number",
                },
                "time_stamp":{
                    "type": "string",
                },
                "altitude":{
                    "type": "number",
                },
                "trip_start":{
                    "type": "string",
                },
                "distance":{
                    "type": "number",
                },
                "emergencyCall":{
                    "type": "boolean",
                },
                "gps_qual":{
                    "type": "number",
                }
            },
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "CarVi Data",
            "type": "object"
}
                


for line in splitfile:
    data = yaml.load(line)
    #print([*data][0])
    try:
        validate(data, schema)
        print("Successful")
        #sys.stdout.write("Record #{}: OK\n".format(idx))
    except jsonschema.exceptions.ValidationError as ve:
        print("ERROR")
        #sys.stderr.write("Record #{}: ERROR\n".format(idx))
        #sys.stderr.write(str(ve) + "\n") 











               
