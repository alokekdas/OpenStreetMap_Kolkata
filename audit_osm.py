import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import csv
import codecs

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "St", "street", "Avenue", "Boulevard", "Blvd", "Drive", "Dr", "Court", "Place", "Square", "Lane", "Ln", "Road", "Rd", 
            "Trail", "Parkway", "Commons", "Way", "Expressway", "Circle", "Sarani", "SARANI", "Pally", "pally", "Park", "Connector", "ROAD", "road", "Row", "Enclave"]
OSM_FILE = 'Kolkata_sample.osm'
"""OSM_FILE = '..\project_OSM\Kolkata.osm' """

street_types = defaultdict(set) 
postcode_types = defaultdict(int)
city_names = defaultdict(int)

""" -----------------------
Audit the street types
----------------------- """
def audit_street_types(street_types, street_name):
    m = street_type_re.search(street_name)
    """ -------------------------------------------------------
     If the street type does not match the regexp, 
     e.g. contains a non-printable unicode char the return 0
     ------------------------------------------------------- """
    if m is None:
        return 0
    street_type = m.group()
    if street_type not in expected:
        street_types[street_type].add(street_name)
        return 0
    else:
        return 1
""" -----------------------
Audit the postal codes
----------------------- """
def audit_postcode(code_types, code):
    if code in code_types:
        code_types[code] += 1
    else:
        code_types[code] = 1

""" -----------------------
Audit the city names
----------------------- """
def audit_city(city_names, city):
    if city in city_names:
        city_names[city] +=1
    else:
        city_names[city] = 1

""" ----------------------------------
 Is this a street element?
 ---------------------------------- """
def is_a_street_elem(elem):
    return elem.attrib['k'] == 'addr:street'

""" ----------------------------------
 Is this a postcode element?
 ---------------------------------- """
def is_a_postcode(elem):
    return elem.attrib['k'] == 'addr:postcode'

""" ----------------------------------
 Is this a city element?
 ---------------------------------- """
def is_a_city(elem):
    return elem.attrib['k'] == 'addr:city'

""" ----------------------------------
 Audit the OSM file
 ---------------------------------- """
def audit_osm_file(osm_file):
    for event, elem in ET.iterparse(osm_file, events = ('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag_elem in elem.iter(tag ='tag'):
                if is_a_street_elem(tag_elem):
                    """ ----------------------
                     Audit the street tag
                     ---------------------- """
                    street_name = tag_elem.attrib['v']
                    """ ---------------------------------------------------
                     If the street type is not the expected list of types
                     then print the stree name
                     --------------------------------------------------- """
                    if not audit_street_types(street_types, street_name):
                        print street_name
                        
                if is_a_postcode(tag_elem):
                    """ --------------------------
                     Audit the postcode tag
                     -------------------------- """
                    raw_postcode = tag_elem.attrib['v']
                    """ -----------------------------------------------------
                     Refine the postal code to make sure it is an integer
                     ----------------------------------------------------- """
                    postcode = re.sub(r'[^0-9]', '', raw_postcode)
                    audit_postcode(postcode_types, postcode)
                    
                if is_a_city(tag_elem):
                    """ --------------------------------------
                    Find out which are the cities
                    -------------------------------------- """
                    city = tag_elem.attrib['v']
                    audit_city(city_names, city)
                
    print dict(street_types)
    print dict(postcode_types)
    print dict(city_names)
    
""" ---------------
 Main code
 --------------- """
audit_osm_file(OSM_FILE)