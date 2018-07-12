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
len(splitfile)

schema_file = open('jsonschema_new.json').read()
schema = yaml.load(schema_file)

for line in splitfile:
    data = yaml.load(line)
    #print([*data][0])
    try:
        validate(data, schema)
        print("Successful")
        #sys.stdout.write("Record #{}: OK\n".format(idx))
    except jsonschema.exceptions.ValidationError as ve:
        print(str(ve) + "\n")
        #sys.stderr.write("Record #{}: ERROR\n".format(idx))
        #sys.stderr.write(str(ve) + "\n") 
